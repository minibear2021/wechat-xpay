"""XPayClient - Main client for WeChat XPay API."""
from __future__ import annotations

import json
import time
from dataclasses import asdict
from typing import Any, Dict, Optional

import requests

from wechat_xpay.auth import calc_pay_sig, calc_signature
from wechat_xpay.exceptions import XPayAPIError
from wechat_xpay import models


class XPayClient:
    """WeChat XPay API client.

    This client handles all server-side API calls for WeChat XPay,
    including signature generation, request signing, and response parsing.

    Args:
        app_id: Mini Program AppID
        app_key: AppKey for pay_sig calculation
        session_key: User's session_key for signature calculation
        env: Environment, 0 for sandbox, 1 for production
        base_url: Optional custom base URL
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
        self.session = requests.Session()

    def _make_request(
        self,
        endpoint: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Make a signed request to the XPay API.

        Args:
            endpoint: API endpoint path (e.g., '/xpay/query_user_balance')
            payload: Request body data

        Returns:
            Parsed JSON response

        Raises:
            XPayAPIError: If the API returns an error
        """
        # Add common fields
        payload["appid"] = self.app_id
        payload["env"] = self.env

        # Serialize body for signing
        body_str = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)

        # Calculate signatures
        pay_sig = calc_pay_sig(endpoint, body_str, self.app_key)
        signature = calc_signature(body_str, self.session_key)

        # Build URL with pay_sig
        url = f"{self.base_url}{endpoint}?pay_sig={pay_sig}"

        # Set headers
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Signature": signature,
        }

        # Make request
        response = self.session.post(url, data=body_str.encode("utf-8"), headers=headers)
        response.raise_for_status()

        # Parse response
        data = response.json()

        # Check for API errors
        if data.get("errcode", 0) != 0:
            raise XPayAPIError(data.get("errcode", -1), data.get("errmsg", "Unknown error"))

        # Return only business data (exclude errcode and errmsg)
        return {k: v for k, v in data.items() if k not in ("errcode", "errmsg")}

    # -------------------------------------------------------------------------
    # User Balance APIs
    # -------------------------------------------------------------------------

    def query_user_balance(self, openid: str) -> models.UserBalance:
        """Query user's virtual currency balance.

        Args:
            openid: User's OpenID

        Returns:
            UserBalance object with balance details
        """
        payload = {"openid": openid}
        response = self._make_request("/xpay/query_user_balance", payload)
        return models.UserBalance(**response)

    # -------------------------------------------------------------------------
    # Payment APIs
    # -------------------------------------------------------------------------

    def currency_pay(
        self,
        openid: str,
        out_trade_no: str,
        order_fee: int,
        pay_item: str,
        **kwargs: Any,
    ) -> models.CurrencyPayResult:
        """Deduct virtual currency for payment.

        Args:
            openid: User's OpenID
            out_trade_no: Merchant order number
            order_fee: Order amount (in cents)
            pay_item: Item name/description
            **kwargs: Optional parameters (attach, device_id, profit_sharing, etc.)

        Returns:
            CurrencyPayResult with order_id and balance info
        """
        payload: Dict[str, Any] = {
            "openid": openid,
            "out_trade_no": out_trade_no,
            "order_fee": order_fee,
            "pay_item": pay_item,
        }
        payload.update(kwargs)
        response = self._make_request("/xpay/currency_pay", payload)
        return models.CurrencyPayResult(**response)

    def query_order(
        self,
        openid: str,
        out_trade_no: Optional[str] = None,
        order_id: Optional[str] = None,
    ) -> models.Order:
        """Query order details.

        Args:
            openid: User's OpenID
            out_trade_no: Merchant order number (optional if order_id provided)
            order_id: XPay order ID (optional if out_trade_no provided)

        Returns:
            Order object with full order details
        """
        payload: Dict[str, Any] = {"openid": openid}
        if out_trade_no:
            payload["out_trade_no"] = out_trade_no
        if order_id:
            payload["order_id"] = order_id
        response = self._make_request("/xpay/query_order", payload)
        return models.Order(**response)

    def cancel_currency_pay(
        self,
        openid: str,
        pay_order_id: str,
        order_id: str,
        order_fee: int,
    ) -> models.CancelCurrencyPayResult:
        """Refund/cancel a currency payment order.

        Args:
            openid: User's OpenID
            pay_order_id: Original payment order ID to cancel
            order_id: New refund order ID
            order_fee: Refund amount (in cents)

        Returns:
            CancelCurrencyPayResult with refund order_id
        """
        payload: Dict[str, Any] = {
            "openid": openid,
            "pay_order_id": pay_order_id,
            "order_id": order_id,
            "order_fee": order_fee,
        }
        response = self._make_request("/xpay/cancel_currency_pay", payload)
        return models.CancelCurrencyPayResult(**response)

    def present_currency(
        self,
        openid: str,
        order_id: str,
        pay_present: int,
    ) -> models.PresentCurrencyResult:
        """Present/gift currency to user.

        Args:
            openid: User's OpenID
            order_id: Present order ID
            pay_present: Present amount

        Returns:
            PresentCurrencyResult with balance info
        """
        payload: Dict[str, Any] = {
            "openid": openid,
            "order_id": order_id,
            "pay_present": pay_present,
        }
        response = self._make_request("/xpay/present_currency", payload)
        return models.PresentCurrencyResult(**response)

    def refund_order(
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
        """Refund a cash order.

        Args:
            openid: User's OpenID
            refund_order_id: Refund order ID (8-32 chars)
            left_fee: Current refundable amount
            refund_fee: Refund amount (0 < refund_fee <= left_fee)
            refund_reason: "0"-none, "1"-product issue, "2"-service, "3"-user request, "4"-price, "5"-other
            req_from: "1"-manual, "2"-user initiated, "3"-other
            out_trade_no: Original merchant order number
            order_id: Original XPay order ID
            biz_meta: Custom data (0-1024 chars)

        Returns:
            RefundOrderResult with refund details
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
        response = self._make_request("/xpay/refund_order", payload)
        return models.RefundOrderResult(**response)

    def create_withdraw_order(
        self,
        withdraw_no: str,
        withdraw_amount: Optional[str] = None,
    ) -> models.WithdrawOrderResult:
        """Create withdrawal order.

        Args:
            withdraw_no: Withdrawal order number (8-32 chars)
            withdraw_amount: Amount in yuan (e.g., "0.01"), omit for full withdrawal

        Returns:
            WithdrawOrderResult with withdraw order details
        """
        payload: Dict[str, Any] = {"withdraw_no": withdraw_no}
        if withdraw_amount:
            payload["withdraw_amount"] = withdraw_amount
        response = self._make_request("/xpay/create_withdraw_order", payload)
        return models.WithdrawOrderResult(**response)

    def query_withdraw_order(self, withdraw_no: str) -> models.WithdrawOrder:
        """Query withdrawal order.

        Args:
            withdraw_no: Withdrawal order number

        Returns:
            WithdrawOrder with withdrawal details
        """
        payload = {"withdraw_no": withdraw_no}
        response = self._make_request("/xpay/query_withdraw_order", payload)
        return models.WithdrawOrder(**response)

    def download_bill(
        self,
        begin_ds: int,
        end_ds: int,
    ) -> models.BillDownload:
        """Download mini program bill.

        Args:
            begin_ds: Start date (e.g., 20230801)
            end_ds: End date (e.g., 20230810)

        Returns:
            BillDownload with URL (valid for 30 minutes)
        """
        payload = {
            "begin_ds": begin_ds,
            "end_ds": end_ds,
        }
        response = self._make_request("/xpay/download_bill", payload)
        return models.BillDownload(**response)

    def query_biz_balance(self) -> models.BizBalance:
        """Query business withdrawable balance.

        Returns:
            BizBalance with available balance details
        """
        payload: Dict[str, Any] = {}
        response = self._make_request("/xpay/query_biz_balance", payload)
        balance_data = response.get("balance_available", {})
        return models.BizBalance(
            balance_available=models.BizBalanceAvailable(
                amount=balance_data.get("amount", "0"),
                currency_code=balance_data.get("currency_code", "CNY"),
            )
        )

    def query_transfer_account(self) -> list:
        """Query advertising fund transfer accounts.

        Returns:
            List of TransferAccount objects
        """
        payload: Dict[str, Any] = {}
        response = self._make_request("/xpay/query_transfer_account", payload)
        return [
            models.TransferAccount(**acct)
            for acct in response.get("acct_list", [])
        ]

    def query_adver_funds(
        self,
        page: int = 1,
        page_size: int = 10,
    ) -> models.AdverFundList:
        """Query advertising fund distribution records.

        Args:
            page: Page number (>= 1)
            page_size: Records per page

        Returns:
            AdverFundList with fund records and pagination
        """
        payload: Dict[str, Any] = {
            "page": page,
            "page_size": page_size,
        }
        response = self._make_request("/xpay/query_adver_funds", payload)
        return models.AdverFundList(
            total_page=response.get("total_page", 1),
            adver_funds_list=[
                models.AdverFund(**fund)
                for fund in response.get("adver_funds_list", [])
            ],
        )

    # -------------------------------------------------------------------------
    # Complaint Management APIs
    # -------------------------------------------------------------------------

    def get_complaint_list(
        self,
        begin_date: str,
        end_date: str,
        offset: int = 0,
        limit: int = 10,
    ) -> models.ComplaintList:
        """Get complaint list.

        Args:
            begin_date: Start date (yyyy-mm-dd)
            end_date: End date (yyyy-mm-dd)
            offset: Pagination offset (from 0)
            limit: Max records to return

        Returns:
            ComplaintList with complaints and total count
        """
        payload: Dict[str, Any] = {
            "begin_date": begin_date,
            "end_date": end_date,
            "offset": offset,
            "limit": limit,
        }
        response = self._make_request("/xpay/get_complaint_list", payload)
        return models.ComplaintList(
            total=response.get("total", 0),
            complaints=[
                models.Complaint(**c)
                for c in response.get("complaints", [])
            ],
        )

    def get_complaint_detail(self, complaint_id: str) -> models.Complaint:
        """Get complaint detail.

        Args:
            complaint_id: Complaint ID

        Returns:
            Complaint with full details
        """
        payload = {"complaint_id": complaint_id}
        response = self._make_request("/xpay/get_complaint_detail", payload)
        return models.Complaint(**response.get("complaint", {}))

    def response_complaint(
        self,
        complaint_id: str,
        response_content: str,
        response_images: Optional[list] = None,
    ) -> bool:
        """Response to complaint.

        Args:
            complaint_id: Complaint ID
            response_content: Response content
            response_images: List of file IDs from upload_vp_file

        Returns:
            True on success
        """
        payload: Dict[str, Any] = {
            "complaint_id": complaint_id,
            "response_content": response_content,
        }
        if response_images:
            payload["response_images"] = response_images
        self._make_request("/xpay/response_complaint", payload)
        return True

    def complete_complaint(self, complaint_id: str) -> bool:
        """Complete complaint handling.

        Args:
            complaint_id: Complaint ID

        Returns:
            True on success
        """
        payload = {"complaint_id": complaint_id}
        self._make_request("/xpay/complete_complaint", payload)
        return True

    def upload_vp_file(
        self,
        file_name: str,
        base64_img: Optional[str] = None,
        img_url: Optional[str] = None,
    ) -> models.UploadFileResult:
        """Upload media file (image, voucher, etc.).

        Args:
            file_name: File name
            base64_img: Base64 encoded image (max 1MB)
            img_url: Image URL (max 2MB, preferred)

        Returns:
            UploadFileResult with file_id
        """
        payload: Dict[str, Any] = {"file_name": file_name}
        if base64_img:
            payload["base64_img"] = base64_img
        if img_url:
            payload["img_url"] = img_url
        response = self._make_request("/xpay/upload_vp_file", payload)
        return models.UploadFileResult(**response)
