"""XPay 客户端基础模块，包含共享逻辑。"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from wechat_xpay.auth import calc_pay_sig, calc_signature
from wechat_xpay.exceptions import XPayAPIError


class BaseClient:
    """XPay 客户端基础类。

    包含配置和共享逻辑：签名计算、请求构建、响应解析、错误处理。

    Args:
        app_id: 小程序 AppID
        app_key: 用于计算 pay_sig 的 AppKey
        env: 环境，0 表示沙箱，1 表示生产环境
        base_url: 可选的自定义基础 URL

    Note:
        session_key 不在初始化时传入，而是在每次调用 API 时传入，
        因为微信的 session_key 有生命周期，会定期过期需要更新。
    """

    SANDBOX_BASE_URL = "https://api.xpay.weixin.qq.com"
    PROD_BASE_URL = "https://api.xpay.weixin.qq.com"

    def __init__(
        self,
        app_id: str,
        app_key: str,
        env: int = 1,
        base_url: Optional[str] = None,
    ) -> None:
        self.app_id = app_id
        self.app_key = app_key
        self.env = env
        self.base_url = base_url or (
            self.PROD_BASE_URL if env == 1 else self.SANDBOX_BASE_URL
        )

    def _prepare_request(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        session_key: str,
    ) -> tuple[str, bytes, Dict[str, str]]:
        """准备请求数据。

        添加公共字段、序列化请求体、计算签名、构建完整 URL。

        Args:
            endpoint: API 端点路径（如 '/xpay/query_user_balance'）
            payload: 请求体数据
            session_key: 用户的 session_key，用于计算用户态签名

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
        signature = calc_signature(body_str, session_key)

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
