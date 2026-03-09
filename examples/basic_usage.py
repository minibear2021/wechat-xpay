"""Basic usage example for WeChat XPay SDK."""
from wechat_xpay import XPayClient
from wechat_xpay.webhook import WebhookParser


def main():
    # Initialize client
    # Replace with your actual credentials
    client = XPayClient(
        app_id="wx1234567890",
        app_key="your_app_key_here",
        session_key="user_session_key_here",
        env=0,  # 0=sandbox for testing, 1=production
    )

    # Example 1: Query user balance
    print("=== Query User Balance ===")
    try:
        balance = client.query_user_balance(openid="user_openid_here")
        print(f"Balance: {balance.balance}")
        print(f"Present Balance: {balance.present_balance}")
        print(f"Sum Save: {balance.sum_save}")
    except Exception as e:
        print(f"Error: {e}")

    # Example 2: Process payment (deduct tokens)
    print("\n=== Process Payment ===")
    try:
        result = client.currency_pay(
            openid="user_openid_here",
            out_trade_no="ORDER_20240101_001",
            order_fee=100,  # Amount in cents
            pay_item="Premium Item",
        )
        print(f"Order ID: {result.order_id}")
        print(f"Remaining Balance: {result.balance}")
    except Exception as e:
        print(f"Error: {e}")

    # Example 3: Query order
    print("\n=== Query Order ===")
    try:
        order = client.query_order(
            openid="user_openid_here",
            order_id="ORDER_20240101_001",
        )
        print(f"Order ID: {order.order_id}")
        print(f"Status: {order.status}")
        print(f"Order Fee: {order.order_fee}")
    except Exception as e:
        print(f"Error: {e}")

    # Example 4: Handle Webhook
    print("\n=== Handle Webhook ===")
    parser = WebhookParser()

    # Example webhook payload (from WeChat)
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

    try:
        notification = parser.parse(webhook_payload)
        print(f"Event Type: {notification.event}")
        print(f"User OpenID: {notification.open_id}")
        print(f"Order Number: {notification.out_trade_no}")

        if notification.goods_info:
            print(f"Product ID: {notification.goods_info.product_id}")
            print(f"Quantity: {notification.goods_info.quantity}")
    except Exception as e:
        print(f"Error parsing webhook: {e}")


if __name__ == "__main__":
    main()
