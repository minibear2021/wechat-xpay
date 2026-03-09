"""XPay 异步客户端。"""
from __future__ import annotations

from typing import Any, Dict, Optional

import httpx

from wechat_xpay.base import BaseClient
from wechat_xpay import models


class XPayAsyncClient(BaseClient):
    """XPay 异步客户端。

    使用 httpx.AsyncClient 进行异步 HTTP 请求。

    Args:
        app_id: 小程序 AppID
        app_key: 用于计算 pay_sig 的 AppKey
        session_key: 用于计算用户态签名的 session_key
        env: 环境，0 表示沙箱，1 表示生产环境
        base_url: 可选的自定义基础 URL

    Examples:
        # 方式 1：异步上下文管理器（推荐，自动关闭连接）
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
        print(f"余额: {balance.balance}")
        await client.close()
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
        """发送异步 HTTP POST 请求。

        Args:
            endpoint: API 端点路径
            payload: 请求体数据

        Returns:
            解析后的响应字典

        Raises:
            XPayAPIError: API 返回错误
            httpx.HTTPError: HTTP 请求错误
        """
        url, body_bytes, headers = self._prepare_request(endpoint, payload)
        response = await self._client.post(url, content=body_bytes, headers=headers)
        response.raise_for_status()
        return self._handle_response(response.json())

    async def close(self) -> None:
        """关闭 HTTP 客户端连接池。

        释放与客户端关联的所有网络资源。
        """
        await self._client.aclose()

    async def __aenter__(self) -> "XPayAsyncClient":
        """异步上下文管理器入口。

        Returns:
            XPayAsyncClient 实例
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """异步上下文管理器出口，自动关闭连接。

        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常回溯
        """
        await self.close()

    # -------------------------------------------------------------------------
    # 用户代币管理 API
    # -------------------------------------------------------------------------

    async def query_user_balance(self, openid: str) -> models.UserBalance:
        """查询用户代币余额。

        Args:
            openid: 用户的 OpenID

        Returns:
            UserBalance 对象，包含余额详情
        """
        payload = {"openid": openid}
        response = await self._http_post("/xpay/query_user_balance", payload)
        return models.UserBalance(**response)

    async def currency_pay(
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
        response = await self._http_post("/xpay/currency_pay", payload)
        return models.CurrencyPayResult(**response)

    async def cancel_currency_pay(
        self,
        openid: str,
        pay_order_id: str,
        order_id: str,
        order_fee: int,
    ) -> models.CancelCurrencyPayResult:
        """取消代币支付（退款）。

        Args:
            openid: 用户的 OpenID
            pay_order_id: 原支付订单 ID
            order_id: 新的退款订单 ID
            order_fee: 退款金额（单位：分）

        Returns:
            CancelCurrencyPayResult，包含退款订单 ID
        """
        payload: Dict[str, Any] = {
            "openid": openid,
            "pay_order_id": pay_order_id,
            "order_id": order_id,
            "order_fee": order_fee,
        }
        response = await self._http_post("/xpay/cancel_currency_pay", payload)
        return models.CancelCurrencyPayResult(**response)

    async def present_currency(
        self,
        openid: str,
        order_id: str,
        pay_present: int,
    ) -> models.PresentCurrencyResult:
        """赠送代币给用户。

        Args:
            openid: 用户的 OpenID
            order_id: 赠送订单 ID
            pay_present: 赠送金额

        Returns:
            PresentCurrencyResult，包含余额信息
        """
        payload: Dict[str, Any] = {
            "openid": openid,
            "order_id": order_id,
            "pay_present": pay_present,
        }
        response = await self._http_post("/xpay/present_currency", payload)
        return models.PresentCurrencyResult(**response)

    # -------------------------------------------------------------------------
    # 订单管理 API
    # -------------------------------------------------------------------------

    async def query_order(
        self,
        openid: str,
        out_trade_no: Optional[str] = None,
        order_id: Optional[str] = None,
    ) -> models.Order:
        """查询订单详情。

        Args:
            openid: 用户的 OpenID
            out_trade_no: 商户订单号（如未提供 order_id 则必填）
            order_id: XPay 订单 ID（如未提供 out_trade_no 则必填）

        Returns:
            Order 对象，包含完整订单详情
        """
        payload: Dict[str, Any] = {"openid": openid}
        if out_trade_no:
            payload["out_trade_no"] = out_trade_no
        if order_id:
            payload["order_id"] = order_id
        response = await self._http_post("/xpay/query_order", payload)
        return models.Order(**response)

    async def refund_order(
        self,
        openid: str,
        refund_order_id: str,
        left_fee: int,
        refund_fee: int,
        refund_reason: str,
        req_from: str,
        out_trade_no: Optional[str] = None,
        order_id: Optional[str] = None,
        biz_meta: Optional[str] = None,
    ) -> models.RefundOrderResult:
        """现金订单退款。

        Args:
            openid: 用户的 OpenID
            refund_order_id: 退款订单 ID（8-32 位字符）
            left_fee: 当前可退金额
            refund_fee: 退款金额（0 < refund_fee <= left_fee）
            refund_reason: "0"-无, "1"-商品问题, "2"-服务, "3"-用户请求, "4"-价格, "5"-其他
            req_from: "1"-人工, "2"-用户发起, "3"-其他
            out_trade_no: 原商户订单号
            order_id: 原 XPay 订单 ID
            biz_meta: 自定义数据（0-1024 字符）

        Returns:
            RefundOrderResult，包含退款详情
        """
        payload: Dict[str, Any] = {
            "openid": openid,
            "refund_order_id": refund_order_id,
            "left_fee": left_fee,
            "refund_fee": refund_fee,
            "refund_reason": refund_reason,
            "req_from": req_from,
        }
        if out_trade_no:
            payload["out_trade_no"] = out_trade_no
        if order_id:
            payload["order_id"] = order_id
        if biz_meta:
            payload["biz_meta"] = biz_meta
        response = await self._http_post("/xpay/refund_order", payload)
        return models.RefundOrderResult(**response)

    # -------------------------------------------------------------------------
    # 提现管理 API
    # -------------------------------------------------------------------------

    async def create_withdraw_order(
        self,
        withdraw_no: str,
        withdraw_amount: Optional[str] = None,
    ) -> models.WithdrawOrderResult:
        """创建提现订单。

        Args:
            withdraw_no: 提现订单号（8-32 位字符）
            withdraw_amount: 提现金额（单位：元，如 "0.01"），省略表示全额提现

        Returns:
            WithdrawOrderResult，包含提现订单详情
        """
        payload: Dict[str, Any] = {"withdraw_no": withdraw_no}
        if withdraw_amount:
            payload["withdraw_amount"] = withdraw_amount
        response = await self._http_post("/xpay/create_withdraw_order", payload)
        return models.WithdrawOrderResult(**response)

    async def query_withdraw_order(self, withdraw_no: str) -> models.WithdrawOrder:
        """查询提现订单。

        Args:
            withdraw_no: 提现订单号

        Returns:
            WithdrawOrder，包含提现详情
        """
        payload = {"withdraw_no": withdraw_no}
        response = await self._http_post("/xpay/query_withdraw_order", payload)
        return models.WithdrawOrder(**response)

    async def download_bill(
        self,
        begin_ds: int,
        end_ds: int,
    ) -> models.BillDownload:
        """下载小程序账单。

        Args:
            begin_ds: 开始日期（如 20230801）
            end_ds: 结束日期（如 20230810）

        Returns:
            BillDownload，包含下载 URL（30 分钟有效）
        """
        payload = {
            "begin_ds": begin_ds,
            "end_ds": end_ds,
        }
        response = await self._http_post("/xpay/download_bill", payload)
        return models.BillDownload(**response)

    # -------------------------------------------------------------------------
    # 商家余额和广告金 API
    # -------------------------------------------------------------------------

    async def query_biz_balance(self) -> models.BizBalance:
        """查询商家可提现余额。

        Returns:
            BizBalance，包含可用余额详情
        """
        payload: Dict[str, Any] = {}
        response = await self._http_post("/xpay/query_biz_balance", payload)
        balance_data = response.get("balance_available", {})
        return models.BizBalance(
            balance_available=models.BizBalanceAvailable(
                amount=balance_data.get("amount", "0"),
                currency_code=balance_data.get("currency_code", "CNY"),
            )
        )

    async def query_transfer_account(self) -> list:
        """查询广告金充值账户。

        Returns:
            TransferAccount 对象列表
        """
        payload: Dict[str, Any] = {}
        response = await self._http_post("/xpay/query_transfer_account", payload)
        return [
            models.TransferAccount(**acct)
            for acct in response.get("acct_list", [])
        ]

    async def query_adver_funds(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> models.AdverFundList:
        """查询广告金发放记录。

        Args:
            page: 页码（>= 1）
            page_size: 每页记录数

        Returns:
            AdverFundList，包含发放记录和分页信息
        """
        payload: Dict[str, Any] = {
            "page": page,
            "page_size": page_size,
        }
        response = await self._http_post("/xpay/query_adver_funds", payload)
        return models.AdverFundList(
            total_page=response.get("total_page", 1),
            adver_funds_list=[
                models.AdverFund(**fund)
                for fund in response.get("adver_funds_list", [])
            ],
        )

    # -------------------------------------------------------------------------
    # 投诉管理 API
    # -------------------------------------------------------------------------

    async def get_complaint_list(
        self,
        begin_date: str,
        end_date: str,
        offset: int = 0,
        limit: int = 10,
    ) -> models.ComplaintList:
        """获取投诉列表。

        Args:
            begin_date: 开始日期（yyyy-mm-dd）
            end_date: 结束日期（yyyy-mm-dd）
            offset: 分页偏移量（从 0 开始）
            limit: 最大返回记录数

        Returns:
            ComplaintList，包含投诉列表和总数
        """
        payload: Dict[str, Any] = {
            "begin_date": begin_date,
            "end_date": end_date,
            "offset": offset,
            "limit": limit,
        }
        response = await self._http_post("/xpay/get_complaint_list", payload)
        return models.ComplaintList(
            total=response.get("total", 0),
            complaints=[
                models.Complaint(**c)
                for c in response.get("complaints", [])
            ],
        )

    async def get_complaint_detail(self, complaint_id: str) -> models.Complaint:
        """获取投诉详情。

        Args:
            complaint_id: 投诉 ID

        Returns:
            Complaint，包含完整详情
        """
        payload = {"complaint_id": complaint_id}
        response = await self._http_post("/xpay/get_complaint_detail", payload)
        return models.Complaint(**response.get("complaint", {}))

    async def response_complaint(
        self,
        complaint_id: str,
        response_content: str,
        response_images: Optional[list] = None,
    ) -> bool:
        """回复投诉。

        Args:
            complaint_id: 投诉 ID
            response_content: 回复内容
            response_images: 图片文件 ID 列表（来自 upload_vp_file）

        Returns:
            成功返回 True
        """
        payload: Dict[str, Any] = {
            "complaint_id": complaint_id,
            "response_content": response_content,
        }
        if response_images:
            payload["response_images"] = response_images
        await self._http_post("/xpay/response_complaint", payload)
        return True

    async def complete_complaint(self, complaint_id: str) -> bool:
        """完成投诉处理。

        Args:
            complaint_id: 投诉 ID

        Returns:
            成功返回 True
        """
        payload = {"complaint_id": complaint_id}
        await self._http_post("/xpay/complete_complaint", payload)
        return True

    async def upload_vp_file(
        self,
        file_name: str,
        base64_img: Optional[str] = None,
        img_url: Optional[str] = None,
    ) -> models.UploadFileResult:
        """上传媒体文件（图片、凭证等）。

        Args:
            file_name: 文件名称
            base64_img: Base64 编码的图片（最大 1MB）
            img_url: 图片 URL（最大 2MB，推荐）

        Returns:
            UploadFileResult，包含 file_id
        """
        payload: Dict[str, Any] = {"file_name": file_name}
        if base64_img:
            payload["base64_img"] = base64_img
        if img_url:
            payload["img_url"] = img_url
        response = await self._http_post("/xpay/upload_vp_file", payload)
        return models.UploadFileResult(**response)
