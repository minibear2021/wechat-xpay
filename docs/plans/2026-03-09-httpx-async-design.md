# WeChat XPay SDK httpx 异步改造设计文档

## 目标

将当前基于 `requests` 的同步 SDK 改造为同时支持同步和异步的版本，使用 `httpx` 作为 HTTP 客户端。

## 架构设计

### 三层架构

```
BaseClient (抽象基类)
    ├── 配置属性 (app_id, app_key, session_key, env, base_url)
    ├── 共享逻辑 (签名计算、请求体序列化、URL 构建、响应解析、错误处理)
    ├── 17 个 API 方法定义 (query_user_balance, currency_pay 等)
    └── 抽象方法 _http_post()

XPayClient (同步客户端)                          XPayAsyncClient (异步客户端)
    ├── 继承 BaseClient                              ├── 继承 BaseClient
    ├── 使用 httpx.Client()                          ├── 使用 httpx.AsyncClient()
    └── 实现 _http_post() 同步版本                    └── 实现 _http_post() 异步版本
```

### 文件结构

```
wechat_xpay/
├── __init__.py          # 导出 XPayClient, XPayAsyncClient
├── base.py              # BaseClient 抽象基类 + 17 个 API 方法
├── client.py            # XPayClient (同步，使用 httpx.Client)
├── async_client.py      # XPayAsyncClient (异步，使用 httpx.AsyncClient)
├── auth.py              # 签名计算（不变）
├── exceptions.py        # 异常类（不变）
├── models.py            # 数据模型（不变）
└── webhook.py           # Webhook 解析（不变）
```

## 核心设计

### 1. BaseClient 抽象基类

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import httpx
import json

from wechat_xpay.auth import calc_pay_sig, calc_signature
from wechat_xpay.exceptions import XPayAPIError
from wechat_xpay import models


class BaseClient(ABC):
    """XPay 客户端抽象基类。

    包含所有共享逻辑：配置、签名计算、请求构建、响应解析、错误处理。
    子类只需实现 _http_post 方法。

    Args:
        app_id: 小程序 AppID
        app_key: 用于计算 pay_sig 的 AppKey
        session_key: 用于计算用户态签名的 session_key
        env: 环境，0 表示沙箱，1 表示生产环境
        base_url: 可选的自定义基础 URL
    """

    SANDBOX_BASE_URL = "https://api.xpay.weixin.qq.com"
    PROD_BASE_URL = "https://api.xpay.weixin.qq.com"

    def __init__(
        self,
        app_id: str,
        app_key: str,
        session_key: str,
        env: int = 1,
        base_url: Optional[str] = None,
    ) -> None:
        self.app_id = app_id
        self.app_key = app_key
        self.session_key = session_key
        self.env = env
        self.base_url = base_url or (
            self.PROD_BASE_URL if env == 1 else self.SANDBOX_BASE_URL
        )

    def _prepare_request(
        self,
        endpoint: str,
        payload: Dict[str, Any],
    ) -> tuple[str, bytes, Dict[str, str]]:
        """准备请求数据。

        添加公共字段、序列化请求体、计算签名、构建完整 URL。

        Args:
            endpoint: API 端点路径（如 '/xpay/query_user_balance'）
            payload: 请求体数据

        Returns:
            (完整 URL, 请求体字节, 请求头字典)
        """
        # 添加公共字段
        payload["appid"] = self.app_id
        payload["env"] = self.env

        # 序列化请求体用于签名
        body_str = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        body_bytes = body_str.encode("utf-8")

        # 计算签名
        pay_sig = calc_pay_sig(endpoint, body_str, self.app_key)
        signature = calc_signature(body_str, self.session_key)

        # 构建 URL
        url = f"{self.base_url}{endpoint}?pay_sig={pay_sig}"

        # 请求头
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Signature": signature,
        }

        return url, body_bytes, headers

    def _handle_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理响应数据。

        检查 API 错误码，返回业务数据。

        Args:
            data: 解析后的 JSON 响应

        Returns:
            业务数据（去除 errcode 和 errmsg）

        Raises:
            XPayAPIError: API 返回非零错误码
        """
        if data.get("errcode", 0) != 0:
            raise XPayAPIError(data.get("errcode", -1), data.get("errmsg", "未知错误"))
        return {k: v for k, v in data.items() if k not in ("errcode", "errmsg")}

    @abstractmethod
    def _http_post(
        self,
        endpoint: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """发送 HTTP POST 请求，由子类实现。"""
        ...

    # -------------------------------------------------------------------------
    # API 方法（在基类中定义一次，子类自动继承）
    # -------------------------------------------------------------------------

    def query_user_balance(self, openid: str) -> models.UserBalance:
        """查询用户代币余额。

        Args:
            openid: 用户的 OpenID

        Returns:
            UserBalance 对象，包含余额详情
        """
        payload = {"openid": openid}
        response = self._http_post("/xpay/query_user_balance", payload)
        return models.UserBalance(**response)

    def currency_pay(
        self,
        openid: str,
        out_trade_no: str,
        order_fee: int,
        pay_item: str,
        **kwargs: Any,
    ) -> models.CurrencyPayResult:
        """扣除代币进行支付。

        Args:
            openid: 用户的 OpenID
            out_trade_no: 商户订单号
            order_fee: 订单金额（单位：分）
            pay_item: 商品名称/描述
            **kwargs: 可选参数（attach, device_id 等）

        Returns:
            CurrencyPayResult，包含订单 ID 和余额信息
        """
        payload: Dict[str, Any] = {
            "openid": openid,
            "out_trade_no": out_trade_no,
            "order_fee": order_fee,
            "pay_item": pay_item,
        }
        payload.update(kwargs)
        response = self._http_post("/xpay/currency_pay", payload)
        return models.CurrencyPayResult(**response)

    # 其他 15 个 API 方法...
    # query_order, cancel_currency_pay, present_currency, refund_order,
    # create_withdraw_order, query_withdraw_order, download_bill,
    # query_biz_balance, query_transfer_account, query_adver_funds,
    # get_complaint_list, get_complaint_detail, response_complaint,
    # complete_complaint, upload_vp_file
```

### 2. 同步客户端 XPayClient

```python
import httpx
from typing import Any, Dict, Optional

from wechat_xpay.base import BaseClient


class XPayClient(BaseClient):
    """XPay 同步客户端。

    使用 httpx.Client 进行同步 HTTP 请求。

    Examples:
        # 简单用法（需手动关闭）
        client = XPayClient(app_id="...", app_key="...", session_key="...")
        balance = client.query_user_balance(openid="xxx")
        client.close()

        # 上下文管理器（推荐，自动关闭）
        with XPayClient(app_id="...", app_key="...", session_key="...") as client:
            balance = client.query_user_balance(openid="xxx")
    """

    def __init__(
        self,
        app_id: str,
        app_key: str,
        session_key: str,
        env: int = 1,
        base_url: Optional[str] = None,
    ) -> None:
        super().__init__(app_id, app_key, session_key, env, base_url)
        self._client = httpx.Client()

    def _http_post(
        self,
        endpoint: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """发送同步 HTTP POST 请求。"""
        url, body_bytes, headers = self._prepare_request(endpoint, payload)
        response = self._client.post(url, content=body_bytes, headers=headers)
        response.raise_for_status()
        return self._handle_response(response.json())

    def close(self) -> None:
        """关闭 HTTP 客户端连接池。"""
        self._client.close()

    def __enter__(self) -> "XPayClient":
        """上下文管理器入口。"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """上下文管理器出口，自动关闭连接。"""
        self.close()
```

### 3. 异步客户端 XPayAsyncClient

```python
import httpx
from typing import Any, Dict, Optional

from wechat_xpay.base import BaseClient


class XPayAsyncClient(BaseClient):
    """XPay 异步客户端。

    使用 httpx.AsyncClient 进行异步 HTTP 请求。

    Examples:
        # 简单用法（需手动关闭）
        client = XPayAsyncClient(app_id="...", app_key="...", session_key="...")
        balance = await client.query_user_balance(openid="xxx")
        await client.close()

        # 上下文管理器（推荐，自动关闭）
        async with XPayAsyncClient(app_id="...", app_key="...", session_key="...") as client:
            balance = await client.query_user_balance(openid="xxx")
    """

    def __init__(
        self,
        app_id: str,
        app_key: str,
        session_key: str,
        env: int = 1,
        base_url: Optional[str] = None,
    ) -> None:
        super().__init__(app_id, app_key, session_key, env, base_url)
        self._client = httpx.AsyncClient()

    async def _http_post(
        self,
        endpoint: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """发送异步 HTTP POST 请求。"""
        url, body_bytes, headers = self._prepare_request(endpoint, payload)
        response = await self._client.post(url, content=body_bytes, headers=headers)
        response.raise_for_status()
        return self._handle_response(response.json())

    async def close(self) -> None:
        """关闭 HTTP 客户端连接池。"""
        await self._client.aclose()

    async def __aenter__(self) -> "XPayAsyncClient":
        """异步上下文管理器入口。"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """异步上下文管理器出口，自动关闭连接。"""
        await self.close()
```

## 依赖变更

### pyproject.toml 更新

```toml
dependencies = [
    "httpx>=0.24.0",  # 替换 requests
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-mock>=3.10.0",
    "pytest-asyncio>=0.21.0",  # 新增：异步测试支持
    "respx>=0.20.0",           # 新增：httpx 模拟库
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]
```

## 测试策略

### 测试结构

```
tests/
├── __init__.py
├── test_auth.py              # 签名计算测试（不变）
├── test_client.py            # 同步客户端测试（改造）
├── test_async_client.py      # 异步客户端测试（新增）
└── test_webhook.py           # Webhook 测试（不变）
```

### 测试策略：B + 少量 C

1. **核心测试**（验证异步 HTTP 调用）：
   - `_http_post` 正确调用 httpx.AsyncClient
   - 请求头和请求体正确构建
   - 错误正确抛出

2. **少量端到端测试**（验证完整流程）：
   - `query_user_balance` 异步版本完整流程
   - `currency_pay` 异步版本完整流程
   - 异常处理流程

### 示例测试代码

```python
import pytest
import respx
from httpx import Response

from wechat_xpay import XPayAsyncClient
from wechat_xpay.exceptions import XPayAPIError


class TestXPayAsyncClient:
    """异步客户端测试。"""

    @pytest.fixture
    async def async_client(self):
        """提供异步客户端 fixture。"""
        client = XPayAsyncClient(
            app_id="wx123",
            app_key="test_key",
            session_key="session_key",
            env=0,
        )
        yield client
        await client.close()

    @respx.mock
    async def test_query_user_balance(self, async_client):
        """测试异步查询用户余额。"""
        # 模拟响应
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/query_user_balance").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "balance": 1000,
                    "present_balance": 200,
                    "sum_save": 800,
                    "sum_present": 200,
                    "sum_balance": 1000,
                    "sum_cost": 0,
                    "first_save_flag": True,
                },
            )
        )

        # 调用异步方法
        result = await async_client.query_user_balance(openid="user_123")

        # 验证结果
        assert result.balance == 1000
        assert result.present_balance == 200
        assert route.called

    @respx.mock
    async def test_api_error(self, async_client):
        """测试异步 API 错误处理。"""
        respx.post("https://api.xpay.weixin.qq.com/xpay/query_user_balance").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 268490009,
                    "errmsg": "session_key 不存在或已过期",
                },
            )
        )

        with pytest.raises(XPayAPIError) as exc_info:
            await async_client.query_user_balance(openid="user_123")

        assert exc_info.value.errcode == 268490009
```

## 使用示例

### 同步客户端

```python
from wechat_xpay import XPayClient

# 方式 1：上下文管理器（推荐）
with XPayClient(
    app_id="wx1234567890",
    app_key="your_app_key",
    session_key="user_session_key",
    env=0,
) as client:
    balance = client.query_user_balance(openid="user_openid")
    print(f"余额: {balance.balance}")

# 方式 2：手动管理生命周期
client = XPayClient(
    app_id="wx1234567890",
    app_key="your_app_key",
    session_key="user_session_key",
    env=0,
)
balance = client.query_user_balance(openid="user_openid")
client.close()
```

### 异步客户端

```python
import asyncio
from wechat_xpay import XPayAsyncClient

async def main():
    # 方式 1：异步上下文管理器（推荐）
    async with XPayAsyncClient(
        app_id="wx1234567890",
        app_key="your_app_key",
        session_key="user_session_key",
        env=0,
    ) as client:
        balance = await client.query_user_balance(openid="user_openid")
        print(f"余额: {balance.balance}")

    # 方式 2：手动管理生命周期
    client = XPayAsyncClient(
        app_id="wx1234567890",
        app_key="your_app_key",
        session_key="user_session_key",
        env=0,
    )
    balance = await client.query_user_balance(openid="user_openid")
    await client.close()

asyncio.run(main())
```

## 向后兼容性

- ✅ `XPayClient` 接口完全兼容，现有同步代码无需修改
- ✅ 所有导出保持不变（auth, exceptions, models, webhook）
- ✅ 新增 `XPayAsyncClient` 导出
- ⚠️ 依赖从 `requests` 变为 `httpx`，但 API 兼容层保持

## 实施步骤

1. 更新依赖（pyproject.toml, requirements.txt）
2. 创建 `base.py` 实现 `BaseClient`
3. 改造 `client.py` 使用 `httpx.Client`
4. 创建 `async_client.py` 实现 `XPayAsyncClient`
5. 更新 `__init__.py` 导出
6. 添加异步测试
7. 更新文档和示例
8. 运行完整测试套件
