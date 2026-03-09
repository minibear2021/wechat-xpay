"""Webhook message parser for WeChat XPay push notifications."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional
import json
import xml.etree.ElementTree as ET


@dataclass
class WechatPayInfo:
    """WeChat payment information in notifications."""

    mch_order_no: str = ""
    transaction_id: str = ""
    paid_time: int = 0


@dataclass
class GoodsInfo:
    """Goods information in delivery notification."""

    product_id: str = ""
    quantity: int = 0
    orig_price: int = 0
    actual_price: int = 0
    attach: str = ""


@dataclass
class CoinInfo:
    """Coin/token information in payment notification."""

    quantity: int = 0
    orig_price: int = 0
    actual_price: int = 0
    attach: str = ""


@dataclass
class TeamInfo:
    """Group buying information in notifications."""

    activity_id: str = ""
    team_id: str = ""
    team_type: int = 0
    team_action: int = 0


@dataclass
class GoodsDeliverNotify:
    """xpay_goods_deliver_notify message."""

    to_user_name: str = ""
    from_user_name: str = ""
    create_time: int = 0
    msg_type: str = ""
    event: str = ""
    open_id: str = ""
    out_trade_no: str = ""
    env: int = 0
    wechat_pay_info: Optional[WechatPayInfo] = None
    goods_info: Optional[GoodsInfo] = None
    team_info: Optional[TeamInfo] = None


@dataclass
class CoinPayNotify:
    """xpay_coin_pay_notify message."""

    to_user_name: str = ""
    from_user_name: str = ""
    create_time: int = 0
    msg_type: str = ""
    event: str = ""
    open_id: str = ""
    out_trade_no: str = ""
    env: int = 0
    wechat_pay_info: Optional[WechatPayInfo] = None
    coin_info: Optional[CoinInfo] = None


@dataclass
class RefundNotify:
    """xpay_refund_notify message."""

    to_user_name: str = ""
    from_user_name: str = ""
    create_time: int = 0
    msg_type: str = ""
    event: str = ""
    open_id: str = ""
    wx_refund_id: str = ""
    mch_refund_id: str = ""
    wx_order_id: str = ""
    mch_order_id: str = ""
    refund_fee: int = 0
    ret_code: int = 0
    ret_msg: str = ""
    refund_start_timestamp: int = 0
    refund_succ_timestamp: int = 0
    wxpay_refund_transaction_id: str = ""
    retry_times: int = 0
    team_info: Optional[TeamInfo] = None


@dataclass
class ComplaintNotify:
    """xpay_complaint_notify message."""

    to_user_name: str = ""
    from_user_name: str = ""
    create_time: int = 0
    msg_type: str = ""
    event: str = ""
    open_id: str = ""
    wx_order_id: str = ""
    mch_order_id: str = ""
    complaint_time: int = 0
    retry_times: int = 0
    request_id: str = ""


class WebhookParser:
    """Parser for WeChat XPay webhook messages."""

    def parse(
        self, payload: dict[str, Any] | str
    ) -> GoodsDeliverNotify | CoinPayNotify | RefundNotify | ComplaintNotify:
        """Parse webhook message.

        Args:
            payload: JSON dict or XML string from WeChat

        Returns:
            Parsed notification dataclass

        Raises:
            ValueError: If payload format is invalid
        """
        if isinstance(payload, str):
            data = self._parse_xml(payload)
        else:
            data = payload

        event = data.get("Event")
        if event == "xpay_goods_deliver_notify":
            return self._parse_goods_deliver_notify(data)
        elif event == "xpay_coin_pay_notify":
            return self._parse_coin_pay_notify(data)
        elif event == "xpay_refund_notify":
            return self._parse_refund_notify(data)
        elif event == "xpay_complaint_notify":
            return self._parse_complaint_notify(data)
        else:
            raise ValueError(f"Unknown event type: {event}")

    def _parse_xml(self, xml_str: str) -> dict[str, Any]:
        """Parse XML string to dict."""
        root = ET.fromstring(xml_str)
        return self._xml_to_dict(root)

    def _xml_to_dict(self, element: ET.Element) -> dict[str, Any]:
        """Convert XML element to dictionary."""
        result: dict[str, Any] = {}
        for child in element:
            if len(child) > 0:
                result[child.tag] = self._xml_to_dict(child)
            else:
                result[child.tag] = child.text or ""
        return result

    def _parse_goods_deliver_notify(self, data: dict) -> GoodsDeliverNotify:
        """Parse goods delivery notification."""
        notify = GoodsDeliverNotify(
            to_user_name=data.get("ToUserName", ""),
            from_user_name=data.get("FromUserName", ""),
            create_time=int(data.get("CreateTime", 0)),
            msg_type=data.get("MsgType", ""),
            event=data.get("Event", ""),
            open_id=data.get("OpenId", ""),
            out_trade_no=data.get("OutTradeNo", ""),
            env=int(data.get("Env", 0)),
        )

        if "WeChatPayInfo" in data:
            wp = data["WeChatPayInfo"]
            notify.wechat_pay_info = WechatPayInfo(
                mch_order_no=wp.get("MchOrderNo", ""),
                transaction_id=wp.get("TransactionId", ""),
                paid_time=int(wp.get("PaidTime", 0)),
            )

        if "GoodsInfo" in data:
            gi = data["GoodsInfo"]
            notify.goods_info = GoodsInfo(
                product_id=gi.get("ProductId", ""),
                quantity=int(gi.get("Quantity", 0)),
                orig_price=int(gi.get("OrigPrice", 0)),
                actual_price=int(gi.get("ActualPrice", 0)),
                attach=gi.get("Attach", ""),
            )

        if "TeamInfo" in data:
            ti = data["TeamInfo"]
            notify.team_info = TeamInfo(
                activity_id=ti.get("ActivityId", ""),
                team_id=ti.get("TeamId", ""),
                team_type=int(ti.get("TeamType", 0)),
                team_action=int(ti.get("TeamAction", 0)),
            )

        return notify

    def _parse_coin_pay_notify(self, data: dict) -> CoinPayNotify:
        """Parse coin payment notification."""
        notify = CoinPayNotify(
            to_user_name=data.get("ToUserName", ""),
            from_user_name=data.get("FromUserName", ""),
            create_time=int(data.get("CreateTime", 0)),
            msg_type=data.get("MsgType", ""),
            event=data.get("Event", ""),
            open_id=data.get("OpenId", ""),
            out_trade_no=data.get("OutTradeNo", ""),
            env=int(data.get("Env", 0)),
        )

        if "WeChatPayInfo" in data:
            wp = data["WeChatPayInfo"]
            notify.wechat_pay_info = WechatPayInfo(
                mch_order_no=wp.get("MchOrderNo", ""),
                transaction_id=wp.get("TransactionId", ""),
                paid_time=int(wp.get("PaidTime", 0)),
            )

        if "CoinInfo" in data:
            ci = data["CoinInfo"]
            notify.coin_info = CoinInfo(
                quantity=int(ci.get("Quantity", 0)),
                orig_price=int(ci.get("OrigPrice", 0)),
                actual_price=int(ci.get("ActualPrice", 0)),
                attach=ci.get("Attach", ""),
            )

        return notify

    def _parse_refund_notify(self, data: dict) -> RefundNotify:
        """Parse refund notification."""
        notify = RefundNotify(
            to_user_name=data.get("ToUserName", ""),
            from_user_name=data.get("FromUserName", ""),
            create_time=int(data.get("CreateTime", 0)),
            msg_type=data.get("MsgType", ""),
            event=data.get("Event", ""),
            open_id=data.get("OpenId", ""),
            wx_refund_id=data.get("WxRefundId", ""),
            mch_refund_id=data.get("MchRefundId", ""),
            wx_order_id=data.get("WxOrderId", ""),
            mch_order_id=data.get("MchOrderId", ""),
            refund_fee=int(data.get("RefundFee", 0)),
            ret_code=int(data.get("RetCode", 0)),
            ret_msg=data.get("RetMsg", ""),
            refund_start_timestamp=int(data.get("RefundStartTimestamp", 0)),
            refund_succ_timestamp=int(data.get("RefundSuccTimestamp", 0)),
            wxpay_refund_transaction_id=data.get("WxpayRefundTransactionId", ""),
            retry_times=int(data.get("RetryTimes", 0)),
        )

        if "TeamInfo" in data:
            ti = data["TeamInfo"]
            notify.team_info = TeamInfo(
                activity_id=ti.get("ActivityId", ""),
                team_id=ti.get("TeamId", ""),
                team_type=int(ti.get("TeamType", 0)),
                team_action=int(ti.get("TeamAction", 0)),
            )

        return notify

    def _parse_complaint_notify(self, data: dict) -> ComplaintNotify:
        """Parse complaint notification."""
        return ComplaintNotify(
            to_user_name=data.get("ToUserName", ""),
            from_user_name=data.get("FromUserName", ""),
            create_time=int(data.get("CreateTime", 0)),
            msg_type=data.get("MsgType", ""),
            event=data.get("Event", ""),
            open_id=data.get("OpenId", ""),
            wx_order_id=data.get("WxOrderId", ""),
            mch_order_id=data.get("MchOrderId", ""),
            complaint_time=int(data.get("ComplaintTime", 0)),
            retry_times=int(data.get("RetryTimes", 0)),
            request_id=data.get("RequestId", ""),
        )
