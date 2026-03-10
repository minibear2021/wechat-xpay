"""异步客户端测试。"""

import pytest
import respx
from httpx import Response

from wechat_xpay import XPayAsyncClient, models
from wechat_xpay.exceptions import XPayAPIError


class TestXPayAsyncClient:
    """测试 XPayAsyncClient 异步客户端。"""

    @pytest.fixture
    async def async_client(self):
        """提供异步客户端 fixture。"""
        client = XPayAsyncClient(
            app_id="wx123",
            app_key="test_key",
            env=0,
        )
        yield client
        await client.close()

    @respx.mock
    async def test_query_user_balance(self, async_client):
        """测试异步查询用户余额。"""
        route = respx.post("https://api.weixin.qq.com/xpay/query_user_balance").mock(
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

        result = await async_client.query_user_balance(
            openid="user_123",
            access_token="test_access_token",
            session_key="session_key_456",
        )

        assert isinstance(result, models.UserBalance)
        assert result.balance == 1000
        assert result.present_balance == 200
        assert result.first_save_flag is True
        assert route.called

    @respx.mock
    async def test_currency_pay(self, async_client):
        """测试异步代币支付。"""
        route = respx.post("https://api.weixin.qq.com/xpay/currency_pay").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "order_id": "order_123",
                    "balance": 800,
                    "used_present_amount": 100,
                },
            )
        )

        result = await async_client.currency_pay(
            openid="user_123",
            access_token="test_access_token",
            session_key="session_key_456",
            order_id="ORDER_001",
            amount=200,
            payitem="Test Item",
        )

        assert isinstance(result, models.CurrencyPayResult)
        assert result.order_id == "order_123"
        assert result.balance == 800
        assert route.called

    @respx.mock
    async def test_api_error(self, async_client):
        """测试异步 API 错误处理。"""
        respx.post("https://api.weixin.qq.com/xpay/query_user_balance").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 268490009,
                    "errmsg": "session_key 不存在或已过期",
                },
            )
        )

        with pytest.raises(XPayAPIError) as exc_info:
            await async_client.query_user_balance(
                openid="user_123",
                access_token="test_access_token",
                session_key="expired_session_key",
            )

        assert exc_info.value.errcode == 268490009
        assert "session_key" in exc_info.value.errmsg

    @respx.mock
    async def test_http_error(self, async_client):
        """测试异步 HTTP 错误处理。"""
        respx.post("https://api.weixin.qq.com/xpay/query_user_balance").mock(
            return_value=Response(500, text="Internal Server Error")
        )

        with pytest.raises((XPayAPIError, Exception)):
            await async_client.query_user_balance(
                openid="user_123",
                access_token="test_access_token",
                session_key="session_key_456",
            )

    async def test_context_manager(self):
        """测试异步上下文管理器。"""
        async with XPayAsyncClient(
            app_id="wx123",
            app_key="test_key",
            env=0,
        ) as client:
            # 验证客户端已正确初始化
            assert client.app_id == "wx123"
            assert client._client is not None

    @respx.mock
    async def test_query_order(self, async_client):
        """测试异步查询订单。"""
        route = respx.post("https://api.weixin.qq.com/xpay/query_order").mock(
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

        result = await async_client.query_order(
            openid="user_123",
            access_token="test_access_token",
            session_key="session_key_456",
            order_id="order_123",
        )

        assert isinstance(result, models.Order)
        assert result.order_id == "order_123"
        assert result.status == 2
        assert route.called

    @respx.mock
    async def test_refund_order(self, async_client):
        """测试异步退款。"""
        route = respx.post("https://api.weixin.qq.com/xpay/refund_order").mock(
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

        result = await async_client.refund_order(
            openid="user_123",
            access_token="test_access_token",
            session_key="session_key_456",
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
    async def test_query_biz_balance(self, async_client):
        """测试异步查询商家余额。"""
        route = respx.post("https://api.weixin.qq.com/xpay/query_biz_balance").mock(
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

        result = await async_client.query_biz_balance(
            access_token="test_access_token", session_key="session_key_456"
        )

        assert isinstance(result, models.BizBalance)
        assert result.balance_available.amount == "1000.00"
        assert route.called

    @respx.mock
    async def test_get_complaint_list(self, async_client):
        """测试异步获取投诉列表。"""
        route = respx.post("https://api.weixin.qq.com/xpay/get_complaint_list").mock(
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

        result = await async_client.get_complaint_list(
            access_token="test_access_token",
            session_key="session_key_456",
            begin_date="2023-01-01",
            end_date="2023-12-31",
            offset=0,
            limit=10,
        )

        assert isinstance(result, models.ComplaintList)
        assert result.total == 1
        assert len(result.complaints) == 1
        assert route.called
