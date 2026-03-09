"""Basic usage example for WeChat XPay SDK."""
import asyncio

from wechat_xpay import XPayClient, XPayAsyncClient
from wechat_xpay.webhook import WebhookParser


def sync_examples():
    """同步客户端使用示例。"""
    print("=" * 60)
    print("同步客户端示例")
    print("=" * 60)

    # 方式 1：上下文管理器（推荐）
    with XPayClient(
        app_id="wx1234567890",
        app_key="your_app_key",
        env=0,  # 0=沙箱，1=生产环境
    ) as client:
        # 示例 1：查询用户余额
        print("\n=== 查询用户余额 ===")
        try:
            # 注意：session_key 在调用时传入，因为它会定期过期
            balance = client.query_user_balance(
                openid="user_openid",
                session_key="user_session_key",
            )
            print(f"余额: {balance.balance}")
            print(f"赠送余额: {balance.present_balance}")
            print(f"累计充值: {balance.sum_save}")
        except Exception as e:
            print(f"错误: {e}")

        # 示例 2：处理支付（扣除代币）
        print("\n=== 处理支付 ===")
        try:
            result = client.currency_pay(
                openid="user_openid",
                session_key="user_session_key",
                order_id="ORDER_20240101_001",
                amount=100,  # 代币数量
                payitem="高级道具",
            )
            print(f"订单 ID: {result.order_id}")
            print(f"剩余余额: {result.balance}")
        except Exception as e:
            print(f"错误: {e}")

        # 示例 3：查询订单
        print("\n=== 查询订单 ===")
        try:
            order = client.query_order(
                openid="user_openid",
                session_key="user_session_key",
                order_id="ORDER_20240101_001",
            )
            print(f"订单 ID: {order.order_id}")
            print(f"状态: {order.status}")
            print(f"订单金额: {order.order_fee}")
        except Exception as e:
            print(f"错误: {e}")

    # 方式 2：手动管理生命周期
    print("\n=== 手动管理生命周期 ===")
    client = XPayClient(
        app_id="wx1234567890",
        app_key="your_app_key",
        env=0,
    )
    try:
        # 可以为不同用户使用不同的 session_key
        balance = client.query_user_balance(
            openid="user_openid",
            session_key="current_session_key",
        )
        print(f"余额: {balance.balance}")
    finally:
        client.close()


async def async_examples():
    """异步客户端使用示例。"""
    print("\n" + "=" * 60)
    print("异步客户端示例")
    print("=" * 60)

    # 方式 1：异步上下文管理器（推荐）
    async with XPayAsyncClient(
        app_id="wx1234567890",
        app_key="your_app_key",
        env=0,
    ) as client:
        # 示例 1：查询用户余额
        print("\n=== 异步查询用户余额 ===")
        try:
            balance = await client.query_user_balance(
                openid="user_openid",
                session_key="user_session_key",
            )
            print(f"余额: {balance.balance}")
            print(f"赠送余额: {balance.present_balance}")
        except Exception as e:
            print(f"错误: {e}")

        # 示例 2：并发处理多个支付（每个使用不同的 session_key）
        print("\n=== 并发处理多个支付 ===")
        tasks = [
            client.currency_pay(
                openid=f"user_{i}",
                session_key=f"session_key_{i}",  # 每个用户有自己的 session_key
                order_id=f"ORDER_20240101_00{i}",
                amount=100,
                payitem=f"道具_{i}",
            )
            for i in range(3)
        ]
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    print(f"订单 {i} 错误: {result}")
                else:
                    print(f"订单 {i} ID: {result.order_id}")
        except Exception as e:
            print(f"错误: {e}")

        # 示例 3：查询订单
        print("\n=== 异步查询订单 ===")
        try:
            order = await client.query_order(
                openid="user_openid",
                session_key="user_session_key",
                order_id="ORDER_20240101_001",
            )
            print(f"订单 ID: {order.order_id}")
            print(f"状态: {order.status}")
        except Exception as e:
            print(f"错误: {e}")

    # 方式 2：手动管理生命周期
    print("\n=== 异步手动管理生命周期 ===")
    client = XPayAsyncClient(
        app_id="wx1234567890",
        app_key="your_app_key",
        env=0,
    )
    try:
        balance = await client.query_user_balance(
            openid="user_openid",
            session_key="current_session_key",
        )
        print(f"余额: {balance.balance}")
    finally:
        await client.close()


def webhook_example():
    """Webhook 处理示例。"""
    print("\n" + "=" * 60)
    print("Webhook 处理示例")
    print("=" * 60)

    parser = WebhookParser()

    # 示例 webhook 负载（来自微信）
    webhook_payload = {
        "ToUserName": "gh_1234567890",
        "FromUserName": "official_account_openid",
        "CreateTime": 1700000000,
        "MsgType": "event",
        "Event": "xpay_goods_deliver_notify",
        "OpenId": "user_openid_here",
        "OutTradeNo": "ORDER_20240101_001",
        "Env": 0,
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

    print("\n=== 解析 Webhook ===")
    try:
        notification = parser.parse(webhook_payload)
        print(f"事件类型: {notification.event}")
        print(f"用户 OpenID: {notification.open_id}")
        print(f"订单号: {notification.out_trade_no}")

        if notification.goods_info:
            print(f"商品 ID: {notification.goods_info.product_id}")
            print(f"数量: {notification.goods_info.quantity}")

        # 返回成功响应
        success_response = parser.success_response()
        print(f"\n成功响应: {success_response}")
    except Exception as e:
        print(f"解析 Webhook 错误: {e}")


def main():
    """主函数。"""
    # 运行同步示例
    sync_examples()

    # 运行异步示例
    asyncio.run(async_examples())

    # 运行 Webhook 示例
    webhook_example()


if __name__ == "__main__":
    main()
