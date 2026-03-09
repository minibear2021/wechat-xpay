"""Tests for XPayClient."""
import pytest
import responses

from wechat_xpay import XPayClient
from wechat_xpay.exceptions import XPayAPIError
from wechat_xpay.models import (
    AdverFundList,
    BillDownload,
    BizBalance,
    CancelCurrencyPayResult,
    Complaint,
    ComplaintList,
    Order,
    PresentCurrencyResult,
    RefundOrderResult,
    TransferAccount,
    UploadFileResult,
    WithdrawOrder,
    WithdrawOrderResult,
)


class TestXPayClient:
    """Test suite for XPayClient."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return XPayClient(
            app_id="wx1234567890",
            app_key="test_app_key",
            session_key="test_session_key",
            env=0,  # Sandbox
        )

    @responses.activate
    def test_query_user_balance(self, client):
        """Test querying user balance."""
        responses.add(
            responses.POST,
            "https://api.xpay.weixin.qq.com/xpay/query_user_balance",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "balance": 1000,
                "present_balance": 500,
                "sum_save": 2000,
                "sum_present": 1000,
                "sum_balance": 3000,
                "sum_cost": 1000,
                "first_save_flag": False,
            },
            status=200,
        )

        result = client.query_user_balance("test_openid")

        assert result.balance == 1000
        assert result.present_balance == 500

    @responses.activate
    def test_api_error(self, client):
        """Test API error handling."""
        responses.add(
            responses.POST,
            "https://api.xpay.weixin.qq.com/xpay/query_user_balance",
            json={
                "errcode": 268490001,
                "errmsg": "Invalid openid",
            },
            status=200,
        )

        with pytest.raises(XPayAPIError) as exc_info:
            client.query_user_balance("invalid_openid")

        assert exc_info.value.errcode == 268490001
        assert "Invalid openid" in exc_info.value.errmsg


class TestOrderAPIs:
    """Test order management APIs."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return XPayClient(
            app_id="wx1234567890",
            app_key="test_app_key",
            session_key="test_session_key",
            env=0,  # Sandbox
        )

    @responses.activate
    def test_query_order(self, client):
        """Test querying order."""
        responses.add(
            responses.POST,
            "https://api.xpay.weixin.qq.com/xpay/query_order",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "order_id": "order_123",
                "create_time": 1700000000,
                "update_time": 1700000100,
                "status": 2,
                "biz_type": 0,
                "order_fee": 1000,
                "paid_fee": 1000,
                "order_type": 0,
                "env_type": 1,
            },
            status=200,
        )

        result = client.query_order(
            openid="user_openid_123",
            order_id="order_123",
        )

        assert isinstance(result, Order)
        assert result.order_id == "order_123"
        assert result.status == 2

    @responses.activate
    def test_cancel_currency_pay(self, client):
        """Test cancel currency pay (refund)."""
        responses.add(
            responses.POST,
            "https://api.xpay.weixin.qq.com/xpay/cancel_currency_pay",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "order_id": "refund_order_123",
            },
            status=200,
        )

        result = client.cancel_currency_pay(
            openid="user_openid_123",
            pay_order_id="original_order_123",
            order_id="refund_order_123",
            order_fee=100,
        )

        assert isinstance(result, CancelCurrencyPayResult)
        assert result.order_id == "refund_order_123"

    @responses.activate
    def test_present_currency(self, client):
        """Test presenting currency to user."""
        responses.add(
            responses.POST,
            "https://api.xpay.weixin.qq.com/xpay/present_currency",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "balance": 1200,
                "order_id": "present_order_123",
                "present_balance": 400,
            },
            status=200,
        )

        result = client.present_currency(
            openid="user_openid_123",
            order_id="present_order_123",
            pay_present=200,
        )

        assert isinstance(result, PresentCurrencyResult)
        assert result.balance == 1200
        assert result.present_balance == 400
        assert result.order_id == "present_order_123"


class TestRefundAndWithdrawAPIs:
    """Test refund and withdrawal APIs."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return XPayClient(
            app_id="wx1234567890",
            app_key="test_app_key",
            session_key="test_session_key",
            env=0,
        )

    @responses.activate
    def test_refund_order(self, client):
        """Test refund order."""
        responses.add(
            responses.POST,
            "https://api.xpay.weixin.qq.com/xpay/refund_order",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "refund_order_id": "refund_123",
                "refund_wx_order_id": "wx_refund_456",
                "pay_order_id": "order_123",
                "pay_wx_order_id": "wx_order_456",
            },
            status=200,
        )

        result = client.refund_order(
            openid="user_openid_123",
            refund_order_id="refund_123",
            left_fee=1000,
            refund_fee=500,
            refund_reason="0",
            req_from="1",
            order_id="order_123",
        )

        assert isinstance(result, RefundOrderResult)
        assert result.refund_order_id == "refund_123"
        assert result.pay_order_id == "order_123"

    @responses.activate
    def test_create_withdraw_order(self, client):
        """Test create withdraw order."""
        responses.add(
            responses.POST,
            "https://api.xpay.weixin.qq.com/xpay/create_withdraw_order",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "withdraw_no": "withdraw_123",
                "wx_withdraw_no": "wx_withdraw_456",
            },
            status=200,
        )

        result = client.create_withdraw_order(
            withdraw_no="withdraw_123",
            withdraw_amount="100.00",
        )

        assert isinstance(result, WithdrawOrderResult)
        assert result.withdraw_no == "withdraw_123"

    @responses.activate
    def test_query_withdraw_order(self, client):
        """Test query withdraw order."""
        responses.add(
            responses.POST,
            "https://api.xpay.weixin.qq.com/xpay/query_withdraw_order",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "withdraw_no": "withdraw_123",
                "status": 2,
                "withdraw_amount": "100.00",
                "wx_withdraw_no": "wx_withdraw_456",
            },
            status=200,
        )

        result = client.query_withdraw_order(
            withdraw_no="withdraw_123",
        )

        assert isinstance(result, WithdrawOrder)
        assert result.status == 2
        assert result.withdraw_no == "withdraw_123"

    @responses.activate
    def test_download_bill(self, client):
        """Test download bill."""
        responses.add(
            responses.POST,
            "https://api.xpay.weixin.qq.com/xpay/download_bill",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "url": "https://example.com/bill.csv",
            },
            status=200,
        )

        result = client.download_bill(
            begin_ds=20230801,
            end_ds=20230810,
        )

        assert isinstance(result, BillDownload)
        assert result.url == "https://example.com/bill.csv"


class TestAdvertisingFundAPIs:
    """Test advertising fund APIs."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return XPayClient(
            app_id="wx1234567890",
            app_key="test_app_key",
            session_key="test_session_key",
            env=0,
        )

    @responses.activate
    def test_query_biz_balance(self, client):
        """Test query business balance."""
        responses.add(
            responses.POST,
            "https://api.xpay.weixin.qq.com/xpay/query_biz_balance",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "balance_available": {
                    "amount": "1000.00",
                    "currency_code": "CNY",
                },
            },
            status=200,
        )

        result = client.query_biz_balance()

        assert isinstance(result, BizBalance)
        assert result.balance_available.amount == "1000.00"
        assert result.balance_available.currency_code == "CNY"

    @responses.activate
    def test_query_transfer_account(self, client):
        """Test query transfer account."""
        responses.add(
            responses.POST,
            "https://api.xpay.weixin.qq.com/xpay/query_transfer_account",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "acct_list": [
                    {
                        "transfer_account_name": "Account 1",
                        "transfer_account_uid": 12345,
                        "transfer_account_agency_id": 67890,
                        "transfer_account_agency_name": "Agency 1",
                        "state": 1,
                        "bind_result": 1,
                    }
                ],
            },
            status=200,
        )

        result = client.query_transfer_account()

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TransferAccount)
        assert result[0].transfer_account_name == "Account 1"

    @responses.activate
    def test_query_adver_funds(self, client):
        """Test query advertising funds."""
        responses.add(
            responses.POST,
            "https://api.xpay.weixin.qq.com/xpay/query_adver_funds",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "total_page": 1,
                "adver_funds_list": [
                    {
                        "settle_begin": 1700000000,
                        "settle_end": 1700086400,
                        "total_amount": 10000,
                        "remain_amount": 5000,
                        "expire_time": 1702678400,
                        "fund_type": 0,
                        "fund_id": "fund_123",
                    }
                ],
            },
            status=200,
        )

        result = client.query_adver_funds(
            page=1,
            page_size=10,
        )

        assert isinstance(result, AdverFundList)
        assert result.total_page == 1
        assert len(result.adver_funds_list) == 1


class TestComplaintAPIs:
    """Test complaint management APIs."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return XPayClient(
            app_id="wx1234567890",
            app_key="test_app_key",
            session_key="test_session_key",
            env=0,
        )

    @responses.activate
    def test_get_complaint_list(self, client):
        """Test get complaint list."""
        responses.add(
            responses.POST,
            "https://api.xpay.weixin.qq.com/xpay/get_complaint_list",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "total": 1,
                "complaints": [
                    {
                        "complaint_id": "complaint_123",
                        "complaint_time": "2023-11-28T11:11:49+08:00",
                        "complaint_detail": "Test complaint",
                        "complaint_state": "PENDING",
                        "payer_openid": "openid_123",
                    }
                ],
            },
            status=200,
        )

        result = client.get_complaint_list(
            begin_date="2023-01-01",
            end_date="2023-12-31",
            offset=0,
            limit=10,
        )

        assert isinstance(result, ComplaintList)
        assert result.total == 1
        assert len(result.complaints) == 1
        assert result.complaints[0].complaint_id == "complaint_123"

    @responses.activate
    def test_get_complaint_detail(self, client):
        """Test get complaint detail."""
        responses.add(
            responses.POST,
            "https://api.xpay.weixin.qq.com/xpay/get_complaint_detail",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "complaint": {
                    "complaint_id": "complaint_123",
                    "complaint_time": "2023-11-28T11:11:49+08:00",
                    "complaint_detail": "Test complaint",
                    "complaint_state": "PENDING",
                    "payer_openid": "openid_123",
                },
            },
            status=200,
        )

        result = client.get_complaint_detail(
            complaint_id="complaint_123",
        )

        assert isinstance(result, Complaint)
        assert result.complaint_id == "complaint_123"

    @responses.activate
    def test_response_complaint(self, client):
        """Test response to complaint."""
        responses.add(
            responses.POST,
            "https://api.xpay.weixin.qq.com/xpay/response_complaint",
            json={"errcode": 0, "errmsg": "ok"},
            status=200,
        )

        result = client.response_complaint(
            complaint_id="complaint_123",
            response_content="We will process this soon",
        )

        assert result is True

    @responses.activate
    def test_complete_complaint(self, client):
        """Test complete complaint handling."""
        responses.add(
            responses.POST,
            "https://api.xpay.weixin.qq.com/xpay/complete_complaint",
            json={"errcode": 0, "errmsg": "ok"},
            status=200,
        )

        result = client.complete_complaint(
            complaint_id="complaint_123",
        )

        assert result is True

    @responses.activate
    def test_upload_vp_file(self, client):
        """Test upload media file."""
        responses.add(
            responses.POST,
            "https://api.xpay.weixin.qq.com/xpay/upload_vp_file",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "file_id": "file_123",
            },
            status=200,
        )

        result = client.upload_vp_file(
            file_name="test.jpg",
            base64_img="base64encodedstring",
        )

        assert isinstance(result, UploadFileResult)
        assert result.file_id == "file_123"
