# 微信支付虚拟支付 Python SDK

微信支付虚拟支付（XPay）服务端 API 的 Python SDK。

## 特性

- ✅ **同步与异步** - 同时支持同步和异步操作
- ✅ **类型提示** - 完整的类型注解支持
- ✅ **HTTP/2** - 基于 httpx，支持 HTTP/2
- ✅ **Webhook 解析** - 处理微信推送通知
- ✅ **错误处理** - 完善的异常层次结构和错误码
- ✅ **日志支持** - 可选的日志记录功能，便于调试

## 安装

```bash
pip install wechat-xpay
```

## 快速开始

### 同步客户端

```python
from wechat_xpay import XPayClient

# 使用上下文管理器（推荐）
with XPayClient(
    app_id="你的_app_id",
    app_key="你的_app_key",
    env=0,  # 0=沙箱环境，1=生产环境
) as client:
    # access_token 和 session_key 在每次调用 API 时传入，因为它们都会定期过期
    balance = client.query_user_balance(
        openid="用户_openid",
        access_token="你的_access_token",
        session_key="用户_session_key",
    )
    print(f"余额: {balance.balance}")
    print(f"赠送余额: {balance.present_balance}")
```

### 异步客户端

```python
import asyncio
from wechat_xpay import XPayAsyncClient

async def main():
    # 使用异步上下文管理器（推荐）
    async with XPayAsyncClient(
        app_id="你的_app_id",
        app_key="你的_app_key",
        env=0,
    ) as client:
        balance = await client.query_user_balance(
            openid="用户_openid",
            access_token="你的_access_token",
            session_key="用户_session_key",
        )
        print(f"余额: {balance.balance}")
        print(f"赠送余额: {balance.present_balance}")

asyncio.run(main())
```

## 为什么 access_token 和 session_key 要在每次调用时传入？

微信的 `access_token`（通过 `auth.getAccessToken` 获取）和 `session_key`（通过 `auth.code2Session` 获取）都有生命周期，会定期过期。

通过在每次 API 调用时传入而不是在客户端初始化时传入：
- 你可以优雅地处理凭证过期，及时更新
- 不同用户可以使用同一个客户端实例，各自使用自己的 `access_token` 和 `session_key`
- 你可以轮换凭证而无需重新创建客户端

## API 覆盖

- [x] 用户代币管理 (query_user_balance, currency_pay, cancel_currency_pay, present_currency)
- [x] 订单管理 (query_order)
- [x] 退款 (refund_order)
- [x] 提现 (create_withdraw_order, query_withdraw_order)
- [x] 发货通知 (notify_provide_goods)
- [x] 商家余额 (query_biz_balance)
- [x] 广告金 (query_transfer_account, query_adver_funds, create_funds_bill)
- [x] 广告金账单 (query_funds_bill, query_recover_bill, download_adverfunds_order)
- [x] 转账账户绑定 (bind_transfer_account)
- [x] 道具管理 (start_upload_goods, query_upload_goods, start_publish_goods, query_publish_goods)
- [x] 投诉管理 (get_complaint_list, get_complaint_detail, response_complaint, complete_complaint, get_negotiation_history)
- [x] 文件上传 (upload_vp_file, get_upload_file_sign)
- [x] 账单下载 (download_bill, download_adverfunds_order)
- [x] Webhook 解析 (发货通知、代币支付通知、退款通知、投诉通知)

**共计 29 个 API 端点，已全部实现。**

## 使用示例

### 同步使用

```python
from wechat_xpay import XPayClient

with XPayClient(
    app_id="wx1234567890",
    app_key="你的_app_key",
    env=0,
) as client:
    # 查询用户余额
    balance = client.query_user_balance(
        openid="用户_openid",
        access_token="你的_access_token",
        session_key="用户_session_key",
    )
    print(f"余额: {balance.balance}")
    print(f"赠送余额: {balance.present_balance}")

    # 处理支付
    result = client.currency_pay(
        openid="用户_openid",
        access_token="你的_access_token",
        session_key="用户_session_key",
        order_id="订单_123",
        amount=100,  # 代币数量
        payitem="商品描述",
    )
    print(f"订单 ID: {result.order_id}")

    # 退款
    result = client.refund_order(
        openid="用户_openid",
        access_token="你的_access_token",
        session_key="用户_session_key",
        refund_order_id="退款_123",
        left_fee=1000,
        refund_fee=500,
        refund_reason="1",  # 商品问题
        req_from="1",  # 人工
        order_id="原订单_id",
    )
    print(f"退款订单 ID: {result.refund_order_id}")
```

### 异步使用

```python
import asyncio
from wechat_xpay import XPayAsyncClient

async def main():
    async with XPayAsyncClient(
        app_id="wx1234567890",
        app_key="你的_app_key",
        env=0,
    ) as client:
        # 查询用户余额
        balance = await client.query_user_balance(
            openid="用户_openid",
            access_token="你的_access_token",
            session_key="用户_session_key",
        )
        print(f"余额: {balance.balance}")

        # 并发处理多个支付（使用不同的 access_token / session_key）
        tasks = [
            client.currency_pay(
                openid=f"用户_{i}",
                access_token="你的_access_token",
                session_key=f"session_key_{i}",  # 每个用户有自己的 session_key
                order_id=f"订单_{i}",
                amount=100,
                payitem=f"商品_{i}",
            )
            for i in range(3)
        ]
        results = await asyncio.gather(*tasks)
        for result in results:
            print(f"订单 ID: {result.order_id}")

asyncio.run(main())
```

### 处理 Webhook

```python
from wechat_xpay.webhook import WebhookParser

parser = WebhookParser()

# 解析 JSON 负载
notification = parser.parse({
    "Event": "xpay_goods_deliver_notify",
    "OpenId": "用户_openid",
    "OutTradeNo": "订单_123",
    # ... 其他字段
})

print(f"事件类型: {notification.event}")
print(f"用户 OpenID: {notification.open_id}")

# 返回成功响应给微信
response = parser.success_response()
```

## 错误处理

```python
from wechat_xpay import XPayClient
from wechat_xpay.exceptions import XPayAPIError, ERR_SESSION_KEY_EXPIRED

client = XPayClient(...)

try:
    balance = client.query_user_balance(
        openid="用户_openid",
        access_token="你的_access_token",
        session_key="用户_session_key",
    )
except XPayAPIError as e:
    if e.errcode == ERR_SESSION_KEY_EXPIRED:
        print("会话已过期，请重新登录")
        # 重新授权用户获取新的 session_key
    else:
        print(f"API 错误: {e.errcode} - {e.errmsg}")
```

## 客户端生命周期管理

### 同步客户端

```python
# 方式 1：上下文管理器（自动关闭）
with XPayClient(...) as client:
    result = client.query_user_balance(...)

# 方式 2：手动关闭
client = XPayClient(...)
try:
    result = client.query_user_balance(...)
finally:
    client.close()
```

### 异步客户端

```python
# 方式 1：异步上下文管理器（自动关闭）
async with XPayAsyncClient(...) as client:
    result = await client.query_user_balance(...)

# 方式 2：手动关闭
client = XPayAsyncClient(...)
try:
    result = await client.query_user_balance(...)
finally:
    await client.close()
```

## 日志功能

SDK 支持可选的日志记录功能，可以记录所有 API 请求和响应信息，便于开发调试。

### 启用日志

```python
import logging
from wechat_xpay import XPayClient

# 配置日志记录器
logger = logging.getLogger("wechat_xpay")
logger.setLevel(logging.DEBUG)

# 添加控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# 添加文件处理器（可选）
file_handler = logging.FileHandler("xpay.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# 传入 logger 参数
with XPayClient(
    app_id="wx1234567890",
    app_key="your_app_key",
    env=0,
    logger=logger,  # 启用日志
) as client:
    balance = client.query_user_balance(
        openid="user_openid",
        access_token="your_access_token",
        session_key="user_session_key",
    )
```

### 日志内容

启用日志后，SDK 会记录：

- **请求信息**：API 端点、URL、请求参数（不包含敏感签名信息）
- **响应信息**：成功响应的数据
- **错误信息**：API 错误码和错误消息

日志级别：
- `DEBUG`：记录所有请求和响应详情
- `ERROR`：仅记录 API 错误

### 异步客户端日志

```python
import logging
from wechat_xpay import XPayAsyncClient

logger = logging.getLogger("wechat_xpay")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

async with XPayAsyncClient(
    app_id="wx1234567890",
    app_key="your_app_key",
    env=0,
    logger=logger,
) as client:
    balance = await client.query_user_balance(
        openid="user_openid",
        access_token="your_access_token",
        session_key="user_session_key",
    )
```

### 不使用日志

如果不传入 `logger` 参数，SDK 不会记录任何日志（默认行为）：

```python
# 不传入 logger，不会记录日志
with XPayClient(
    app_id="wx1234567890",
    app_key="your_app_key",
    env=0,
) as client:
    balance = client.query_user_balance(
        openid="user_openid",
        access_token="your_access_token",
        session_key="user_session_key",
    )
```

## 认证

SDK 自动处理请求认证，所有签名通过 URL 查询参数传递：

- **access_token**: 接口调用凭证，通过 `auth.getAccessToken` 获取，每次 API 调用时传入
- **pay_sig**: 使用 AppKey 的 HMAC-SHA256 签名，所有接口都需要，SDK 自动计算
- **signature**: 使用 session_key 的 HMAC-SHA256 用户态签名，仅 `query_user_balance` 和 `currency_pay` 接口需要，SDK 自动判断并计算

URL 格式示例：
```
https://api.weixin.qq.com/xpay/{endpoint}?access_token=xxx&pay_sig=xxx
https://api.weixin.qq.com/xpay/{endpoint}?access_token=xxx&pay_sig=xxx&signature=xxx
```

## 环境

- `env=0`: 沙箱环境（用于测试）
- `env=1`: 生产环境

## 文档

查看 `docs/plans/` 目录了解实现细节和 API 规范。

## 许可证

MIT
