"""同步客户端测试。"""
import pytest
import respx
from httpx import Response

from wechat_xpay import XPayClient
from wechat_xpay.exceptions import XPayAPIError
from wechat_xpay import models


class TestXPayClient:
    """测试 XPayClient 同步客户端。"""

    @pytest.fixture
    def client(self):
        """提供同步客户端 fixture。"""
        return XPayClient(
            app_id="wx1234567890",
            app_key="test_app_key",
            session_key="test_session_key",
            env=0,  # Sandbox
        )

    @respx.mock
    def test_query_user_balance(self, client):
        """测试查询用户余额。"""
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/query_user_balance").mock(
            return_value=Response(
                200,
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
            )
        )

        result = client.query_user_balance("test_openid")

        assert result.balance == 1000
        assert result.present_balance == 500
        assert route.called

    @respx.mock
    def test_api_error(self, client):
        """测试 API 错误处理。"""
        respx.post("https://api.xpay.weixin.qq.com/xpay/query_user_balance").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 268490001,
                    "errmsg": "Invalid openid",
                },
            )
        )

        with pytest.raises(XPayAPIError) as exc_info:
            client.query_user_balance("invalid_openid")

        assert exc_info.value.errcode == 268490001
        assert "Invalid openid" in exc_info.value.errmsg

    def test_context_manager(self):
        """测试同步上下文管理器。"""
        with XPayClient(
            app_id="wx123",
            app_key="test_key",
            session_key="session_key",
            env=0,
        ) as client:
            assert client.app_id == "wx123"
            assert client._client is not None


class TestOrderAPIs:
    """测试订单管理 API。"""

    @pytest.fixture
    def client(self):
        """提供同步客户端 fixture。"""
        return XPayClient(
            app_id="wx1234567890",
            app_key="test_app_key",
            session_key="test_session_key",
            env=0,
        )

    @respx.mock
    def test_query_order(self, client):
        """测试查询订单。"""
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/query_order").mock(
            return_value=Response(
                200,
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
            )
        )

        result = client.query_order(openid="user_123", order_id="order_123")

        assert isinstance(result, models.Order)
        assert result.order_id == "order_123"
        assert result.status == 2
        assert route.called

    @respx.mock
    def test_cancel_currency_pay(self, client):
        """测试取消代币支付。"""
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/cancel_currency_pay").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "order_id": "refund_order_123",
                },
            )
        )

        result = client.cancel_currency_pay(
            openid="user_123",
            pay_order_id="original_order_123",
            order_id="refund_order_123",
            order_fee=100,
        )

        assert isinstance(result, models.CancelCurrencyPayResult)
        assert result.order_id == "refund_order_123"
        assert route.called

    @respx.mock
    def test_present_currency(self, client):
        """测试赠送代币。"""
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/present_currency").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "balance": 1200,
                    "order_id": "present_order_123",
                    "present_balance": 400,
                },
            )
        )

        result = client.present_currency(
            openid="user_123",
            order_id="present_order_123",
            pay_present=200,
        )

        assert isinstance(result, models.PresentCurrencyResult)
        assert result.balance == 1200
        assert result.present_balance == 400
        assert route.called


class TestRefundAndWithdrawAPIs:
    """测试退款和提现 API。"""

    @pytest.fixture
    def client(self):
        """提供同步客户端 fixture。"""
        return XPayClient(
            app_id="wx1234567890",
            app_key="test_app_key",
            session_key="test_session_key",
            env=0,
        )

    @respx.mock
    def test_refund_order(self, client):
        """测试退款订单。"""
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/refund_order").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "refund_order_id": "refund_123",
                    "refund_wx_order_id": "wx_refund_456",
                    "pay_order_id": "order_123",
                    "pay_wx_order_id": "wx_order_456",
                },
            )
        )

        result = client.refund_order(
            openid="user_123",
            refund_order_id="refund_123",
            left_fee=1000,
            refund_fee=500,
            refund_reason="1",
            req_from="1",
            order_id="original_order",
        )

        assert isinstance(result, models.RefundOrderResult)
        assert result.refund_order_id == "refund_123"
        assert route.called

    @respx.mock
    def test_create_withdraw_order(self, client):
        """测试创建提现订单。"""
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/create_withdraw_order").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "withdraw_no": "withdraw_123",
                    "wx_withdraw_no": "wx_withdraw_456",
                },
            )
        )

        result = client.create_withdraw_order(
            withdraw_no="withdraw_123",
            withdraw_amount="100.00",
        )

        assert isinstance(result, models.WithdrawOrderResult)
        assert result.withdraw_no == "withdraw_123"
        assert route.called

    @respx.mock
    def test_query_withdraw_order(self, client):
        """测试查询提现订单。"""
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/query_withdraw_order").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "withdraw_no": "withdraw_123",
                    "status": 2,
                    "withdraw_amount": "100.00",
                    "wx_withdraw_no": "wx_withdraw_456",
                },
            )
        )

        result = client.query_withdraw_order(withdraw_no="withdraw_123")

        assert isinstance(result, models.WithdrawOrder)
        assert result.status == 2
        assert route.called

    @respx.mock
    def test_download_bill(self, client):
        """测试下载账单。"""
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/download_bill").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "url": "https://example.com/bill.csv",
                },
            )
        )

        result = client.download_bill(
            begin_ds=20230801,
            end_ds=20230810,
        )

        assert isinstance(result, models.BillDownload)
        assert result.url == "https://example.com/bill.csv"
        assert route.called


class TestAdvertisingFundAPIs:
    """测试广告金相关 API。"""

    @pytest.fixture
    def client(self):
        """提供同步客户端 fixture。"""
        return XPayClient(
            app_id="wx1234567890",
            app_key="test_app_key",
            session_key="test_session_key",
            env=0,
        )

    @respx.mock
    def test_query_biz_balance(self, client):
        """测试查询商家余额。"""
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/query_biz_balance").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "balance_available": {
                        "amount": "1000.00",
                        "currency_code": "CNY",
                    },
                },
            )
        )

        result = client.query_biz_balance()

        assert isinstance(result, models.BizBalance)
        assert result.balance_available.amount == "1000.00"
        assert route.called

    @respx.mock
    def test_query_transfer_account(self, client):
        """测试查询转账账户。"""
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/query_transfer_account").mock(
            return_value=Response(
                200,
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
            )
        )

        result = client.query_transfer_account()

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], models.TransferAccount)
        assert result[0].transfer_account_name == "Account 1"
        assert route.called

    @respx.mock
    def test_query_adver_funds(self, client):
        """测试查询广告金。"""
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/query_adver_funds").mock(
            return_value=Response(
                200,
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
            )
        )

        result = client.query_adver_funds(page=1, page_size=10)

        assert isinstance(result, models.AdverFundList)
        assert result.total_page == 1
        assert len(result.adver_funds_list) == 1
        assert route.called


class TestComplaintAPIs:
    """测试投诉管理 API。"""

    @pytest.fixture
    def client(self):
        """提供同步客户端 fixture。"""
        return XPayClient(
            app_id="wx1234567890",
            app_key="test_app_key",
            session_key="test_session_key",
            env=0,
        )

    @respx.mock
    def test_get_complaint_list(self, client):
        """测试获取投诉列表。"""
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/get_complaint_list").mock(
            return_value=Response(
                200,
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
            )
        )

        result = client.get_complaint_list(
            begin_date="2023-01-01",
            end_date="2023-12-31",
            offset=0,
            limit=10,
        )

        assert isinstance(result, models.ComplaintList)
        assert result.total == 1
        assert len(result.complaints) == 1
        assert route.called

    @respx.mock
    def test_get_complaint_detail(self, client):
        """测试获取投诉详情。"""
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/get_complaint_detail").mock(
            return_value=Response(
                200,
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
            )
        )

        result = client.get_complaint_detail(complaint_id="complaint_123")

        assert isinstance(result, models.Complaint)
        assert result.complaint_id == "complaint_123"
        assert route.called

    @respx.mock
    def test_response_complaint(self, client):
        """测试回复投诉。"""
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/response_complaint").mock(
            return_value=Response(
                200,
                json={"errcode": 0, "errmsg": "ok"},
            )
        )

        result = client.response_complaint(
            complaint_id="complaint_123",
            response_content="We will process this soon",
        )

        assert result is True
        assert route.called

    @respx.mock
    def test_complete_complaint(self, client):
        """测试完成投诉处理。"""
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/complete_complaint").mock(
            return_value=Response(
                200,
                json={"errcode": 0, "errmsg": "ok"},
            )
        )

        result = client.complete_complaint(complaint_id="complaint_123")

        assert result is True
        assert route.called

    @respx.mock
    def test_upload_vp_file(self, client):
        """测试上传文件。"""
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/upload_vp_file").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "file_id": "file_123",
                },
            )
        )

        result = client.upload_vp_file(
            file_name="test.jpg",
            img_url="https://example.com/image.jpg",
        )

        assert isinstance(result, models.UploadFileResult)
        assert result.file_id == "file_123"
        assert route.called
