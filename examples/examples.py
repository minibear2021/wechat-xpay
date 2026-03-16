"""日志功能使用示例。"""

import logging

from config import ACCESS_TOKEN, APP_SECRET, APPID, ENV, OPENID, SESSION_KEY, USER_IP

from wechat_xpay import XPayAsyncClient, XPayClient
from wechat_xpay.webhook import (
    CoinPayNotify,
    ComplaintNotify,
    GoodsDeliverNotify,
    RefundNotify,
    WebhookParser,
)


def setup_logger() -> logging.Logger:
    """配置日志记录器。"""
    logger = logging.getLogger("wechat_xpay")
    logger.setLevel(logging.DEBUG)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # 文件处理器
    file_handler = logging.FileHandler("xpay.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    # 格式化器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def sync_example_with_logging():
    """同步客户端使用日志示例。"""
    logger = setup_logger()

    with XPayClient(
        app_id=APPID,
        app_key=APP_SECRET,
        env=ENV,
        logger=logger,
    ) as client:
        try:
            # 查询用户余额
            balance = client.query_user_balance(
                openid=OPENID, access_token=ACCESS_TOKEN, session_key=SESSION_KEY, user_ip=USER_IP
            )
            print(f"用户余额: {balance.balance}")

            # 查询商户余额
            biz_balance = client.query_biz_balance(
                access_token=ACCESS_TOKEN, session_key=SESSION_KEY
            )
            print(f"商户余额: {biz_balance.balance_available}")

            # 查询广告资金列表
            adver_funds_list = client.query_adver_funds(
                access_token=ACCESS_TOKEN, session_key=SESSION_KEY
            )
            print("广告资金列表:")
            for adver_funds in adver_funds_list.adver_funds_list:
                print(f"  - 广告ID: {adver_funds.fund_id}, 可用余额: {adver_funds.remain_amount}")

            # 查询订单
            order = client.query_order(
                openid=OPENID,
                access_token=ACCESS_TOKEN,
                session_key=SESSION_KEY,
                order_id="order_123",
            )
            print(f"订单状态: {order.status}")

        except Exception as e:
            logger.exception("API 调用失败")
            print(f"错误: {e}")


async def async_example_with_logging():
    """异步客户端使用日志示例。"""
    logger = setup_logger()

    async with XPayAsyncClient(
        app_id=APPID,
        app_key=APP_SECRET,
        env=ENV,
        logger=logger,
    ) as client:
        try:
            # 查询用户余额
            balance = await client.query_user_balance(
                openid=OPENID,
                access_token=ACCESS_TOKEN,
                session_key=SESSION_KEY,
            )
            print(f"用户余额: {balance.balance}")

            # 查询商户余额
            biz_balance = await client.query_biz_balance(
                access_token=ACCESS_TOKEN, session_key=SESSION_KEY
            )
            print(f"商户余额: {biz_balance.balance_available}")

            # 查询广告资金列表
            adver_funds_list = await client.query_adver_funds(
                access_token=ACCESS_TOKEN, session_key=SESSION_KEY
            )
            print("广告资金列表:")
            for adver_funds in adver_funds_list.adver_funds_list:
                print(f"  - 广告ID: {adver_funds.fund_id}, 可用余额: {adver_funds.remain_amount}")

            # 查询订单
            order = await client.query_order(
                openid=OPENID,
                access_token=ACCESS_TOKEN,
                session_key=SESSION_KEY,
                order_id="order_123",
            )
            print(f"订单状态: {order.status}")

        except Exception as e:
            logger.exception("API 调用失败")
            print(f"错误: {e}")


def example_without_logging():
    """不使用日志的示例（默认行为）。"""
    with XPayClient(
        app_id=APPID,
        app_key=APP_SECRET,
        env=ENV,
    ) as client:
        # 不传入 logger 参数，不会记录任何日志
        balance = client.query_user_balance(
            openid=OPENID,
            access_token=ACCESS_TOKEN,
            session_key=SESSION_KEY,
        )
        print(f"用户余额: {balance.balance}")


def webhook_example():
    """回调通知消息处理示例。

    微信服务器会以 XML 或 JSON 格式向开发者服务器推送以下四种通知：
      - xpay_goods_deliver_notify  : 道具发货通知（用户购买道具后触发，需发货）
      - xpay_coin_pay_notify       : 代币支付通知（用户消耗代币后触发）
      - xpay_refund_notify         : 退款结果通知
      - xpay_complaint_notify      : 用户投诉通知

    实际部署时（以 Flask 为例）：

        from flask import Flask, request, Response
        from wechat_xpay.webhook import CallbackResult, WebhookParser, GoodsDeliverNotify, ...

        app = Flask(__name__)
        parser = WebhookParser()

        @app.route('/notify', methods=['POST'])
        def notify():
            result = parser.callback(request.data)
            try:
                handle_notification(result.notification)
                return Response(result.success_response(), content_type=result.content_type)
            except Exception as e:
                return Response(result.fail_response(str(e)), content_type=result.content_type, status=500)
    """
    import json as _json

    parser = WebhookParser()

    # ------------------------------------------------------------------
    # 统一入口：parser.callback(body) 自动识别 JSON / XML 格式
    # 返回 CallbackResult，每次调用创建独立实例，并发环境下不会冲突
    # result.notification 为解析后的通知对象，通过 isinstance 区分处理逻辑
    # result.success_response() / result.fail_response() 与请求格式保持一致
    # ------------------------------------------------------------------

    def handle_notification(body: str | bytes) -> str:
        """模拟 HTTP 回调处理函数，返回应答给微信服务器的字符串。"""
        result = parser.callback(body)
        notification = result.notification

        if isinstance(notification, GoodsDeliverNotify):
            # 道具发货通知：完成发货后调用 client.notify_provide_goods() 确认
            print("=== 道具发货通知 ===")
            print(f"  用户 OpenID : {notification.open_id}")
            print(f"  订单号      : {notification.out_trade_no}")
            if notification.goods_info:
                print(f"  商品 ID     : {notification.goods_info.product_id}")
                print(f"  购买数量    : {notification.goods_info.quantity}")
            # TODO: client.notify_provide_goods(...)

        elif isinstance(notification, CoinPayNotify):
            # 代币支付通知：记录消费流水
            print("\n=== 代币支付通知 ===")
            print(f"  用户 OpenID : {notification.open_id}")
            print(f"  订单号      : {notification.out_trade_no}")
            if notification.coin_info:
                print(f"  消耗代币数  : {notification.coin_info.quantity}")

        elif isinstance(notification, RefundNotify):
            # 退款结果通知：ret_code=0 表示退款成功
            print("\n=== 退款结果通知 ===")
            print(f"  用户 OpenID : {notification.open_id}")
            print(f"  退款单号    : {notification.mch_refund_id}")
            print(f"  退款金额    : {notification.refund_fee}")
            if notification.ret_code == 0:
                print("  退款结果    : 成功")
            else:
                print(f"  退款结果    : 失败({notification.ret_msg})")

        elif isinstance(notification, ComplaintNotify):
            # 用户投诉通知：及时回复，避免影响商户评级
            print("\n=== 用户投诉通知 ===")
            print(f"  用户 OpenID : {notification.open_id}")
            print(f"  投诉请求 ID : {notification.request_id}")
            print(f"  关联订单号  : {notification.mch_order_id}")
            # TODO: client.response_complaint(...) 或 client.complete_complaint(...)

        return result.success_response()

    # ------------------------------------------------------------------
    # 测试：JSON 格式（dict 序列化为 JSON bytes 模拟 request.data）
    # ------------------------------------------------------------------
    json_body = _json.dumps(
        {
            "ToUserName": "gh_1234567890",
            "FromUserName": "official_account_openid",
            "CreateTime": 1700000000,
            "MsgType": "event",
            "Event": "xpay_goods_deliver_notify",
            "OpenId": OPENID,
            "OutTradeNo": "ORDER_20240101_001",
            "Env": ENV,
            "WeChatPayInfo": {
                "MchOrderNo": "ORDER_20240101_001",
                "TransactionId": "4200001234567890",
                "PaidTime": 1700000000,
            },
            "GoodsInfo": {
                "ProductId": "product_001",
                "Quantity": 1,
                "OrigPrice": 100,
                "ActualPrice": 100,
                "Attach": "custom_data",
            },
        }
    ).encode("utf-8")

    resp = handle_notification(json_body)
    print(f"  应答: {resp}")

    # ------------------------------------------------------------------
    # 测试：XML 格式（模拟 request.data 为 XML bytes）
    # ------------------------------------------------------------------
    xml_body = f"""<xml>
  <ToUserName>gh_1234567890</ToUserName>
  <FromUserName>official_account_openid</FromUserName>
  <CreateTime>1700000003</CreateTime>
  <MsgType>event</MsgType>
  <Event>xpay_complaint_notify</Event>
  <OpenId>{OPENID}</OpenId>
  <WxOrderId>4200001234567890</WxOrderId>
  <MchOrderId>ORDER_20240101_001</MchOrderId>
  <ComplaintTime>1700000003</ComplaintTime>
  <RetryTimes>0</RetryTimes>
  <RequestId>COMPLAINT_REQ_001</RequestId>
</xml>""".encode()

    resp = handle_notification(xml_body)
    print(f"  应答: {resp}")


if __name__ == "__main__":
    print("=== 同步客户端日志示例 ===")
    sync_example_with_logging()

    print("\n=== 异步客户端日志示例 ===")
    import asyncio

    asyncio.run(async_example_with_logging())

    print("\n=== 不使用日志示例 ===")
    example_without_logging()

    print("\n=== 回调通知消息处理示例 ===")
    webhook_example()
