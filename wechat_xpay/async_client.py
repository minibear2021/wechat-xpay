"""XPay 异步客户端。"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from wechat_xpay import models
from wechat_xpay.base import BaseClient


class XPayAsyncClient(BaseClient):
    """XPay 异步客户端。

    使用 httpx.AsyncClient 进行异步 HTTP 请求。

    Args:
        app_id: 小程序 AppID
        app_key: 用于计算 pay_sig 的 AppKey
        env: 环境，0 表示沙箱，1 表示生产环境
        base_url: 可选的自定义基础 URL
        logger: 可选的日志记录器，用于记录 API 调用和响应信息

    Examples:
        # 方式 1：异步上下文管理器（推荐，自动关闭连接）
        async with XPayAsyncClient(
            app_id="wx1234567890",
            app_key="your_app_key",
            env=0,
        ) as client:
            balance = await client.query_user_balance(
                openid="user_openid",
                session_key="user_session_key",
            )
            print(f"余额: {balance.balance}")

        # 方式 2：手动管理生命周期
        client = XPayAsyncClient(
            app_id="wx1234567890",
            app_key="your_app_key",
            env=0,
        )
        balance = await client.query_user_balance(
            openid="user_openid",
            session_key="user_session_key",
        )
        print(f"余额: {balance.balance}")
        await client.close()

        # 方式 3：使用自定义 logger
        import logging
        logger = logging.getLogger("wechat_xpay")
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)

        async with XPayAsyncClient(
            app_id="wx1234567890",
            app_key="your_app_key",
            env=0,
            logger=logger,
        ) as client:
            balance = await client.query_user_balance(
                openid="user_openid",
                session_key="user_session_key",
            )
    """

    def __init__(
        self,
        app_id: str,
        app_key: str,
        env: int = 1,
        base_url: str | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        super().__init__(app_id, app_key, env, base_url, logger)
        self._client = httpx.AsyncClient()

    async def _http_post(
        self,
        endpoint: str,
        payload: dict[str, Any],
        session_key: str,
    ) -> dict[str, Any]:
        """发送异步 HTTP POST 请求。

        Args:
            endpoint: API 端点路径
            payload: 请求体数据
            session_key: 用户的 session_key，用于计算用户态签名

        Returns:
            解析后的响应字典

        Raises:
            XPayAPIError: API 返回错误
            httpx.HTTPError: HTTP 请求错误
        """
        url, body_bytes, headers = self._prepare_request(endpoint, payload, session_key)
        response = await self._client.post(url, content=body_bytes, headers=headers)
        response.raise_for_status()
        return self._handle_response(response.json())

    async def close(self) -> None:
        """关闭 HTTP 客户端连接池。

        释放与客户端关联的所有网络资源。
        """
        await self._client.aclose()

    async def __aenter__(self) -> XPayAsyncClient:
        """异步上下文管理器入口。

        Returns:
            XPayAsyncClient 实例
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
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

    async def query_user_balance(
        self,
        openid: str,
        session_key: str,
        user_ip: str | None = None,
    ) -> models.UserBalance:
        """查询用户代币余额。

        Args:
            openid: 用户的 OpenID
            session_key: 用户的 session_key，用于计算用户态签名
            user_ip: 用户 IP，例如 1.1.1.1

        Returns:
            UserBalance 对象，包含余额详情
        """
        payload: dict[str, Any] = {"openid": openid}
        if user_ip:
            payload["user_ip"] = user_ip
        response = await self._http_post("/xpay/query_user_balance", payload, session_key)
        return models.UserBalance(**response)

    async def currency_pay(
        self,
        openid: str,
        session_key: str,
        order_id: str,
        amount: int,
        payitem: str,
        user_ip: str | None = None,
        remark: str | None = None,
    ) -> models.CurrencyPayResult:
        """扣除代币进行支付。

        Args:
            openid: 用户的 OpenID
            session_key: 用户的 session_key，用于计算用户态签名
            order_id: 订单号
            amount: 支付的代币数量
            payitem: 物品信息，如 [{"productid":"物品id", "unit_price": 单价, "quantity": 数量}]
            user_ip: 用户 IP，例如 1.1.1.1
            remark: 备注

        Returns:
            CurrencyPayResult，包含订单 ID 和余额信息
        """
        payload: dict[str, Any] = {
            "openid": openid,
            "order_id": order_id,
            "amount": amount,
            "payitem": payitem,
        }
        if user_ip:
            payload["user_ip"] = user_ip
        if remark:
            payload["remark"] = remark
        response = await self._http_post("/xpay/currency_pay", payload, session_key)
        return models.CurrencyPayResult(**response)

    async def cancel_currency_pay(
        self,
        openid: str,
        session_key: str,
        pay_order_id: str,
        order_id: str,
        amount: int,
        user_ip: str | None = None,
    ) -> models.CancelCurrencyPayResult:
        """取消代币支付（退款）。

        Args:
            openid: 用户的 OpenID
            session_key: 用户的 session_key，用于计算用户态签名
            pay_order_id: 代币支付时传的 order_id
            order_id: 本次退款单的单号
            amount: 退款金额
            user_ip: 用户 IP，例如 1.1.1.1

        Returns:
            CancelCurrencyPayResult，包含退款订单 ID
        """
        payload: dict[str, Any] = {
            "openid": openid,
            "pay_order_id": pay_order_id,
            "order_id": order_id,
            "amount": amount,
        }
        if user_ip:
            payload["user_ip"] = user_ip
        response = await self._http_post("/xpay/cancel_currency_pay", payload, session_key)
        return models.CancelCurrencyPayResult(**response)

    async def present_currency(
        self,
        openid: str,
        session_key: str,
        order_id: str,
        amount: int,
    ) -> models.PresentCurrencyResult:
        """赠送代币给用户。

        Args:
            openid: 用户的 OpenID
            session_key: 用户的 session_key，用于计算用户态签名
            order_id: 赠送订单 ID
            amount: 赠送金额

        Returns:
            PresentCurrencyResult，包含余额信息
        """
        payload: dict[str, Any] = {
            "openid": openid,
            "order_id": order_id,
            "amount": amount,
        }
        response = await self._http_post("/xpay/present_currency", payload, session_key)
        return models.PresentCurrencyResult(**response)

    # -------------------------------------------------------------------------
    # 订单管理 API
    # -------------------------------------------------------------------------

    async def query_order(
        self,
        openid: str,
        session_key: str,
        order_id: str | None = None,
        wx_order_id: str | None = None,
    ) -> models.Order:
        """查询订单详情。

        Args:
            openid: 用户的 OpenID
            session_key: 用户的 session_key，用于计算用户态签名
            order_id: 创建的订单号（与 wx_order_id 二选一）
            wx_order_id: 微信内部单号（与 order_id 二选一）

        Returns:
            Order 对象，包含完整订单详情
        """
        payload: dict[str, Any] = {"openid": openid}
        if order_id:
            payload["order_id"] = order_id
        if wx_order_id:
            payload["wx_order_id"] = wx_order_id
        response = await self._http_post("/xpay/query_order", payload, session_key)
        return models.Order(**response)

    async def refund_order(
        self,
        openid: str,
        session_key: str,
        refund_order_id: str,
        left_fee: int,
        refund_fee: int,
        refund_reason: str,
        req_from: str,
        order_id: str | None = None,
        wx_order_id: str | None = None,
        biz_meta: str | None = None,
    ) -> models.RefundOrderResult:
        """现金订单退款。

        Args:
            openid: 用户的 OpenID
            session_key: 用户的 session_key，用于计算用户态签名
            refund_order_id: 退款订单 ID（8-32 位字符）
            left_fee: 当前可退金额
            refund_fee: 退款金额（0 < refund_fee <= left_fee）
            refund_reason: "0"-无, "1"-商品问题, "2"-服务, "3"-用户请求, "4"-价格, "5"-其他
            req_from: "1"-人工, "2"-用户发起, "3"-其他
            order_id: 下单时的单号（与 wx_order_id 二选一）
            wx_order_id: 支付单对应的微信侧单号（与 order_id 二选一）
            biz_meta: 自定义数据（0-1024 字符）

        Returns:
            RefundOrderResult，包含退款详情
        """
        payload: dict[str, Any] = {
            "openid": openid,
            "refund_order_id": refund_order_id,
            "left_fee": left_fee,
            "refund_fee": refund_fee,
            "refund_reason": refund_reason,
            "req_from": req_from,
        }
        if order_id:
            payload["order_id"] = order_id
        if wx_order_id:
            payload["wx_order_id"] = wx_order_id
        if biz_meta:
            payload["biz_meta"] = biz_meta
        response = await self._http_post("/xpay/refund_order", payload, session_key)
        return models.RefundOrderResult(**response)

    # -------------------------------------------------------------------------
    # 提现管理 API
    # -------------------------------------------------------------------------

    async def create_withdraw_order(
        self,
        session_key: str,
        withdraw_no: str,
        withdraw_amount: str | None = None,
    ) -> models.WithdrawOrderResult:
        """创建提现订单。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            withdraw_no: 提现订单号（8-32 位字符）
            withdraw_amount: 提现金额（单位：元，如 "0.01"），省略表示全额提现

        Returns:
            WithdrawOrderResult，包含提现订单详情
        """
        payload: dict[str, Any] = {"withdraw_no": withdraw_no}
        if withdraw_amount:
            payload["withdraw_amount"] = withdraw_amount
        response = await self._http_post("/xpay/create_withdraw_order", payload, session_key)
        return models.WithdrawOrderResult(**response)

    async def query_withdraw_order(
        self,
        session_key: str,
        withdraw_no: str,
    ) -> models.WithdrawOrder:
        """查询提现订单。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            withdraw_no: 提现订单号

        Returns:
            WithdrawOrder，包含提现详情
        """
        payload = {"withdraw_no": withdraw_no}
        response = await self._http_post("/xpay/query_withdraw_order", payload, session_key)
        return models.WithdrawOrder(**response)

    async def download_bill(
        self,
        session_key: str,
        begin_ds: int,
        end_ds: int,
    ) -> models.BillDownload:
        """下载小程序账单。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            begin_ds: 开始日期（如 20230801）
            end_ds: 结束日期（如 20230810）

        Returns:
            BillDownload，包含下载 URL（30 分钟有效）
        """
        payload = {
            "begin_ds": begin_ds,
            "end_ds": end_ds,
        }
        response = await self._http_post("/xpay/download_bill", payload, session_key)
        return models.BillDownload(**response)

    # -------------------------------------------------------------------------
    # 商家余额和广告金 API
    # -------------------------------------------------------------------------

    async def query_biz_balance(
        self,
        session_key: str,
    ) -> models.BizBalance:
        """查询商家可提现余额。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名

        Returns:
            BizBalance，包含可用余额详情
        """
        payload: dict[str, Any] = {}
        response = await self._http_post("/xpay/query_biz_balance", payload, session_key)
        balance_data = response.get("balance_available", {})
        return models.BizBalance(
            balance_available=models.BizBalanceAvailable(
                amount=balance_data.get("amount", "0"),
                currency_code=balance_data.get("currency_code", "CNY"),
            )
        )

    async def query_transfer_account(
        self,
        session_key: str,
    ) -> list:
        """查询广告金充值账户。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名

        Returns:
            TransferAccount 对象列表
        """
        payload: dict[str, Any] = {}
        response = await self._http_post("/xpay/query_transfer_account", payload, session_key)
        return [models.TransferAccount(**acct) for acct in response.get("acct_list", [])]

    async def query_adver_funds(
        self,
        session_key: str,
        page: int = 1,
        page_size: int = 10,
    ) -> models.AdverFundList:
        """查询广告金发放记录。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            page: 页码（>= 1）
            page_size: 每页记录数

        Returns:
            AdverFundList，包含发放记录和分页信息
        """
        payload: dict[str, Any] = {
            "page": page,
            "page_size": page_size,
        }
        response = await self._http_post("/xpay/query_adver_funds", payload, session_key)
        return models.AdverFundList(
            total_page=response.get("total_page", 1),
            adver_funds_list=[
                models.AdverFund(**fund) for fund in response.get("adver_funds_list", [])
            ],
        )

    # -------------------------------------------------------------------------
    # 投诉管理 API
    # -------------------------------------------------------------------------

    async def get_complaint_list(
        self,
        session_key: str,
        begin_date: str,
        end_date: str,
        offset: int = 0,
        limit: int = 10,
    ) -> models.ComplaintList:
        """获取投诉列表。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            begin_date: 开始日期（yyyy-mm-dd）
            end_date: 结束日期（yyyy-mm-dd）
            offset: 分页偏移量（从 0 开始）
            limit: 最大返回记录数

        Returns:
            ComplaintList，包含投诉列表和总数
        """
        payload: dict[str, Any] = {
            "begin_date": begin_date,
            "end_date": end_date,
            "offset": offset,
            "limit": limit,
        }
        response = await self._http_post("/xpay/get_complaint_list", payload, session_key)
        return models.ComplaintList(
            total=response.get("total", 0),
            complaints=[models.Complaint(**c) for c in response.get("complaints", [])],
        )

    async def get_complaint_detail(
        self,
        session_key: str,
        complaint_id: str,
    ) -> models.Complaint:
        """获取投诉详情。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            complaint_id: 投诉 ID

        Returns:
            Complaint，包含完整详情
        """
        payload = {"complaint_id": complaint_id}
        response = await self._http_post("/xpay/get_complaint_detail", payload, session_key)
        return models.Complaint(**response.get("complaint", {}))

    async def response_complaint(
        self,
        session_key: str,
        complaint_id: str,
        response_content: str,
        response_images: list | None = None,
    ) -> bool:
        """回复投诉。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            complaint_id: 投诉 ID
            response_content: 回复内容
            response_images: 图片文件 ID 列表（来自 upload_vp_file）

        Returns:
            成功返回 True
        """
        payload: dict[str, Any] = {
            "complaint_id": complaint_id,
            "response_content": response_content,
        }
        if response_images:
            payload["response_images"] = response_images
        await self._http_post("/xpay/response_complaint", payload, session_key)
        return True

    async def complete_complaint(
        self,
        session_key: str,
        complaint_id: str,
    ) -> bool:
        """完成投诉处理。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            complaint_id: 投诉 ID

        Returns:
            成功返回 True
        """
        payload = {"complaint_id": complaint_id}
        await self._http_post("/xpay/complete_complaint", payload, session_key)
        return True

    async def upload_vp_file(
        self,
        session_key: str,
        file_name: str,
        base64_img: str | None = None,
        img_url: str | None = None,
    ) -> models.UploadFileResult:
        """上传媒体文件（图片、凭证等）。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            file_name: 文件名称
            base64_img: Base64 编码的图片（最大 1MB）
            img_url: 图片 URL（最大 2MB，推荐）

        Returns:
            UploadFileResult，包含 file_id
        """
        payload: dict[str, Any] = {"file_name": file_name}
        if base64_img:
            payload["base64_img"] = base64_img
        if img_url:
            payload["img_url"] = img_url
        response = await self._http_post("/xpay/upload_vp_file", payload, session_key)
        return models.UploadFileResult(**response)

    # -------------------------------------------------------------------------
    # 发货管理 API
    # -------------------------------------------------------------------------

    async def notify_provide_goods(
        self,
        session_key: str,
        order_id: str | None = None,
        wx_order_id: str | None = None,
    ) -> models.NotifyProvideGoodsResult:
        """发货完成通知。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            order_id: 订单号（与 wx_order_id 二选一）
            wx_order_id: 微信内部单号（与 order_id 二选一）

        Returns:
            NotifyProvideGoodsResult，包含发货状态
        """
        payload: dict[str, Any] = {}
        if order_id:
            payload["order_id"] = order_id
        if wx_order_id:
            payload["wx_order_id"] = wx_order_id
        response = await self._http_post("/xpay/notify_provide_goods", payload, session_key)
        return models.NotifyProvideGoodsResult(**response)

    # -------------------------------------------------------------------------
    # 道具管理 API
    # -------------------------------------------------------------------------

    async def start_upload_goods(
        self,
        session_key: str,
        goods: list[dict[str, Any]],
    ) -> models.GoodsUploadStatus:
        """启动道具上传。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            goods: 道具列表，每个道具包含 id, name, price, remark, item_url

        Returns:
            GoodsUploadStatus，包含上传任务状态
        """
        payload: dict[str, Any] = {"goods": goods}
        response = await self._http_post("/xpay/start_upload_goods", payload, session_key)
        return models.GoodsUploadStatus(
            status=response.get("status", 0),
            upload_item=[
                models.GoodsUploadItem(**item) for item in response.get("upload_item", [])
            ],
        )

    async def query_upload_goods(
        self,
        session_key: str,
    ) -> models.GoodsUploadStatus:
        """查询道具上传状态。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名

        Returns:
            GoodsUploadStatus，包含上传任务状态和每个道具的上传状态
        """
        payload: dict[str, Any] = {}
        response = await self._http_post("/xpay/query_upload_goods", payload, session_key)
        return models.GoodsUploadStatus(
            status=response.get("status", 0),
            upload_item=[
                models.GoodsUploadItem(**item) for item in response.get("upload_item", [])
            ],
        )

    async def start_publish_goods(
        self,
        session_key: str,
        goods: list[dict[str, Any]],
    ) -> models.GoodsPublishStatus:
        """启动道具发布。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            goods: 道具列表，每个道具包含 id

        Returns:
            GoodsPublishStatus，包含发布任务状态
        """
        payload: dict[str, Any] = {"goods": goods}
        response = await self._http_post("/xpay/start_publish_goods", payload, session_key)
        return models.GoodsPublishStatus(
            status=response.get("status", 0),
            publish_item=[
                models.GoodsPublishItem(**item) for item in response.get("publish_item", [])
            ],
        )

    async def query_publish_goods(
        self,
        session_key: str,
    ) -> models.GoodsPublishStatus:
        """查询道具发布状态。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名

        Returns:
            GoodsPublishStatus，包含发布任务状态和每个道具的发布状态
        """
        payload: dict[str, Any] = {}
        response = await self._http_post("/xpay/query_publish_goods", payload, session_key)
        return models.GoodsPublishStatus(
            status=response.get("status", 0),
            publish_item=[
                models.GoodsPublishItem(**item) for item in response.get("publish_item", [])
            ],
        )

    # -------------------------------------------------------------------------
    # 广告金账单 API
    # -------------------------------------------------------------------------

    async def create_funds_bill(
        self,
        session_key: str,
        transfer_account_uid: int,
        transfer_account_agency_id: int,
        transfer_amount: int,
        fund_id: str,
        settle_begin: int,
        settle_end: int,
        request_id: str | None = None,
    ) -> models.FundsBillResult:
        """创建广告金账单。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            transfer_account_uid: 转账账户 UID
            transfer_account_agency_id: 转账账户代理 ID
            transfer_amount: 转账金额（单位：分）
            fund_id: 广告金发放记录 ID
            settle_begin: 结算开始时间戳
            settle_end: 结算结束时间戳
            request_id: 请求 ID（幂等控制，可选）

        Returns:
            FundsBillResult，包含账单 ID
        """
        payload: dict[str, Any] = {
            "transfer_account_uid": transfer_account_uid,
            "transfer_account_agency_id": transfer_account_agency_id,
            "transfer_amount": transfer_amount,
            "fund_id": fund_id,
            "settle_begin": settle_begin,
            "settle_end": settle_end,
        }
        if request_id:
            payload["request_id"] = request_id
        response = await self._http_post("/xpay/create_funds_bill", payload, session_key)
        return models.FundsBillResult(**response)

    async def bind_transfer_account(
        self,
        session_key: str,
        transfer_account_uid: int,
        transfer_account_agency_id: int,
    ) -> bool:
        """绑定转账账户。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            transfer_account_uid: 转账账户 UID
            transfer_account_agency_id: 转账账户代理 ID

        Returns:
            成功返回 True
        """
        payload: dict[str, Any] = {
            "transfer_account_uid": transfer_account_uid,
            "transfer_account_agency_id": transfer_account_agency_id,
        }
        await self._http_post("/xpay/bind_transfer_accout", payload, session_key)
        return True

    async def query_funds_bill(
        self,
        session_key: str,
        page: int = 1,
        page_size: int = 10,
    ) -> models.FundsBillList:
        """查询资金账单。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            page: 页码（>= 1）
            page_size: 每页记录数

        Returns:
            FundsBillList，包含账单列表和分页信息
        """
        payload: dict[str, Any] = {
            "page": page,
            "page_size": page_size,
        }
        response = await self._http_post("/xpay/query_funds_bill", payload, session_key)
        return models.FundsBillList(
            total_page=response.get("total_page", 1),
            bill_list=[models.FundsBillItem(**item) for item in response.get("bill_list", [])],
        )

    async def query_recover_bill(
        self,
        session_key: str,
        page: int = 1,
        page_size: int = 10,
    ) -> models.RecoverBillList:
        """查询回收账单。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            page: 页码（>= 1）
            page_size: 每页记录数

        Returns:
            RecoverBillList，包含回收账单列表和分页信息
        """
        payload: dict[str, Any] = {
            "page": page,
            "page_size": page_size,
        }
        response = await self._http_post("/xpay/query_recover_bill", payload, session_key)
        return models.RecoverBillList(
            total_page=response.get("total_page", 1),
            bill_list=[models.RecoverBillItem(**item) for item in response.get("bill_list", [])],
        )

    async def download_adverfunds_order(
        self,
        session_key: str,
        begin_ds: int,
        end_ds: int,
    ) -> models.AdverfundsOrderDownload:
        """下载广告金订单账单。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            begin_ds: 开始日期（如 20230801）
            end_ds: 结束日期（如 20230810）

        Returns:
            AdverfundsOrderDownload，包含下载 URL
        """
        payload = {
            "begin_ds": begin_ds,
            "end_ds": end_ds,
        }
        response = await self._http_post("/xpay/download_adverfunds_order", payload, session_key)
        return models.AdverfundsOrderDownload(**response)

    # -------------------------------------------------------------------------
    # 协商历史 API
    # -------------------------------------------------------------------------

    async def get_negotiation_history(
        self,
        session_key: str,
        complaint_id: str,
        offset: int = 0,
        limit: int = 10,
    ) -> models.NegotiationHistory:
        """获取协商历史。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            complaint_id: 投诉 ID
            offset: 分页偏移量（从 0 开始）
            limit: 最大返回记录数

        Returns:
            NegotiationHistory，包含协商记录列表
        """
        payload: dict[str, Any] = {
            "complaint_id": complaint_id,
            "offset": offset,
            "limit": limit,
        }
        response = await self._http_post("/xpay/get_negotiation_history", payload, session_key)
        return models.NegotiationHistory(
            total=response.get("total", 0),
            history=[models.NegotiationRecord(**record) for record in response.get("history", [])],
        )

    # -------------------------------------------------------------------------
    # 文件上传签名 API
    # -------------------------------------------------------------------------

    async def get_upload_file_sign(
        self,
        session_key: str,
        file_name: str,
        file_type: str,
    ) -> models.UploadFileSign:
        """获取上传文件签名。

        Args:
            session_key: 用户的 session_key，用于计算用户态签名
            file_name: 文件名称
            file_type: 文件类型，如 "image/jpeg", "image/png"

        Returns:
            UploadFileSign，包含签名和上传 URL
        """
        payload: dict[str, Any] = {
            "file_name": file_name,
            "file_type": file_type,
        }
        response = await self._http_post("/xpay/get_upload_file_sign", payload, session_key)
        return models.UploadFileSign(**response)
