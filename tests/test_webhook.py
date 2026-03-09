"""Tests for webhook message parser."""
import pytest
from wechat_xpay.webhook import (
    WebhookParser,
    GoodsDeliverNotify,
    CoinPayNotify,
    RefundNotify,
    ComplaintNotify,
)


class TestWebhookParser:
    """Test webhook parser."""

    def test_parse_goods_deliver_notify_json(self):
        """Test parsing goods delivery notification from JSON."""
        parser = WebhookParser()
        payload = {
            "ToUserName": "gh_123",
            "FromUserName": "official_openid",
            "CreateTime": 1700000000,
            "MsgType": "event",
            "Event": "xpay_goods_deliver_notify",
            "OpenId": "user_openid_123",
            "OutTradeNo": "order_123",
            "Env": 0,
            "WeChatPayInfo": {
                "MchOrderNo": "mch_order_123",
                "TransactionId": "transaction_456",
                "PaidTime": 1700000000,
            },
            "GoodsInfo": {
                "ProductId": "product_123",
                "Quantity": 1,
                "OrigPrice": 100,
                "ActualPrice": 100,
                "Attach": "custom_data",
            },
        }

        result = parser.parse(payload)

        assert isinstance(result, GoodsDeliverNotify)
        assert result.event == "xpay_goods_deliver_notify"
        assert result.open_id == "user_openid_123"
        assert result.out_trade_no == "order_123"
        assert result.env == 0
        assert result.wechat_pay_info is not None
        assert result.wechat_pay_info.transaction_id == "transaction_456"
        assert result.goods_info is not None
        assert result.goods_info.quantity == 1

    def test_parse_coin_pay_notify_json(self):
        """Test parsing coin payment notification from JSON."""
        parser = WebhookParser()
        payload = {
            "ToUserName": "gh_123",
            "FromUserName": "official_openid",
            "CreateTime": 1700000000,
            "MsgType": "event",
            "Event": "xpay_coin_pay_notify",
            "OpenId": "user_openid_123",
            "OutTradeNo": "order_123",
            "Env": 0,
            "CoinInfo": {
                "Quantity": 100,
                "OrigPrice": 100,
                "ActualPrice": 100,
                "Attach": "custom_data",
            },
        }

        result = parser.parse(payload)

        assert isinstance(result, CoinPayNotify)
        assert result.event == "xpay_coin_pay_notify"
        assert result.open_id == "user_openid_123"
        assert result.coin_info is not None
        assert result.coin_info.quantity == 100

    def test_parse_refund_notify_json(self):
        """Test parsing refund notification from JSON."""
        parser = WebhookParser()
        payload = {
            "ToUserName": "gh_123",
            "FromUserName": "official_openid",
            "CreateTime": 1700000000,
            "MsgType": "event",
            "Event": "xpay_refund_notify",
            "OpenId": "user_openid_123",
            "WxRefundId": "wx_refund_123",
            "MchRefundId": "mch_refund_456",
            "WxOrderId": "wx_order_789",
            "MchOrderId": "mch_order_abc",
            "RefundFee": 100,
            "RetCode": 0,
            "RetMsg": "Success",
            "RefundStartTimestamp": 1700000000,
            "RefundSuccTimestamp": 1700000100,
            "WxpayRefundTransactionId": "wxpay_refund_123",
            "RetryTimes": 0,
        }

        result = parser.parse(payload)

        assert isinstance(result, RefundNotify)
        assert result.event == "xpay_refund_notify"
        assert result.open_id == "user_openid_123"
        assert result.refund_fee == 100
        assert result.ret_code == 0

    def test_parse_complaint_notify_json(self):
        """Test parsing complaint notification from JSON."""
        parser = WebhookParser()
        payload = {
            "ToUserName": "gh_123",
            "FromUserName": "official_openid",
            "CreateTime": 1700000000,
            "MsgType": "event",
            "Event": "xpay_complaint_notify",
            "OpenId": "user_openid_123",
            "WxOrderId": "wx_order_123",
            "MchOrderId": "mch_order_456",
            "ComplaintTime": 1700000000,
            "RetryTimes": 0,
            "RequestId": "req_123",
        }

        result = parser.parse(payload)

        assert isinstance(result, ComplaintNotify)
        assert result.event == "xpay_complaint_notify"
        assert result.open_id == "user_openid_123"
        assert result.wx_order_id == "wx_order_123"

    def test_parse_unknown_event(self):
        """Test parsing unknown event type raises error."""
        parser = WebhookParser()
        payload = {
            "Event": "unknown_event",
        }

        with pytest.raises(ValueError) as exc_info:
            parser.parse(payload)

        assert "Unknown event type" in str(exc_info.value)

    def test_parse_xml(self):
        """Test parsing XML payload."""
        parser = WebhookParser()
        xml_payload = """<?xml version="1.0" encoding="UTF-8"?>
        <xml>
            <ToUserName>gh_123</ToUserName>
            <FromUserName>official_openid</FromUserName>
            <CreateTime>1700000000</CreateTime>
            <MsgType>event</MsgType>
            <Event>xpay_goods_deliver_notify</Event>
            <OpenId>user_openid_123</OpenId>
            <OutTradeNo>order_123</OutTradeNo>
            <Env>0</Env>
        </xml>"""

        result = parser.parse(xml_payload)

        assert isinstance(result, GoodsDeliverNotify)
        assert result.event == "xpay_goods_deliver_notify"
        assert result.open_id == "user_openid_123"
