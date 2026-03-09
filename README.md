# WeChat XPay Python SDK

Python SDK for WeChat XPay (Virtual Payment) server-side APIs.

## Installation

```bash
pip install requests
```

## Quick Start

```python
from wechat_xpay import XPayClient

# Initialize client
client = XPayClient(
    app_id="your_app_id",
    app_key="your_app_key",
    session_key="user_session_key",
    env=0,  # 0=sandbox, 1=production
)

# Query user balance
balance = client.query_user_balance(openid="user_openid")
print(f"Balance: {balance.balance}")
print(f"Present Balance: {balance.present_balance}")
```

## API Coverage

- [x] User Token Management (query_user_balance, currency_pay, cancel_currency_pay, present_currency)
- [x] Order Management (query_order)
- [x] Refund (refund_order)
- [x] Withdrawal (create_withdraw_order, query_withdraw_order)
- [x] Business Balance (query_biz_balance)
- [x] Advertising Funds (query_transfer_account, query_adver_funds)
- [x] Complaint Management (get_complaint_list, get_complaint_detail, response_complaint, complete_complaint)
- [x] File Upload (upload_vp_file)
- [x] Webhook Parser (goods delivery, coin payment, refund, complaint notifications)

## Usage Examples

### Query User Balance

```python
from wechat_xpay import XPayClient

client = XPayClient(
    app_id="wx1234567890",
    app_key="your_app_key",
    session_key="user_session_key",
    env=0,
)

balance = client.query_user_balance(openid="user_openid")
print(f"Balance: {balance.balance}")
print(f"Present: {balance.present_balance}")
```

### Process Payment

```python
result = client.currency_pay(
    openid="user_openid",
    out_trade_no="ORDER_123",
    order_fee=100,  # Amount in cents
    pay_item="Item description",
)
print(f"Order ID: {result.order_id}")
```

### Refund Order

```python
result = client.refund_order(
    openid="user_openid",
    refund_order_id="REFUND_123",
    left_fee=1000,
    refund_fee=500,
    refund_reason="1",  # Product issue
    req_from="1",  # Manual
    order_id="original_order_id",
)
print(f"Refund Order ID: {result.refund_order_id}")
```

### Handle Webhook

```python
from wechat_xpay.webhook import WebhookParser

parser = WebhookParser()

# Parse JSON payload
notification = parser.parse({
    "Event": "xpay_goods_deliver_notify",
    "OpenId": "user_openid",
    "OutTradeNo": "order_123",
    # ... other fields
})

print(f"Event: {notification.event}")
print(f"OpenID: {notification.open_id}")
```

## Error Handling

```python
from wechat_xpay import XPayClient
from wechat_xpay.exceptions import XPayAPIError, ERR_SESSION_KEY_EXPIRED

client = XPayClient(...)

try:
    balance = client.query_user_balance(openid="user_openid")
except XPayAPIError as e:
    if e.errcode == ERR_SESSION_KEY_EXPIRED:
        print("Session expired, please re-login")
    else:
        print(f"API Error: {e.errcode} - {e.errmsg}")
```

## Authentication

The SDK handles two types of signatures automatically:
- **pay_sig**: Signed with AppKey for API authentication
- **signature**: Signed with user's session_key for user state verification

## Environment

- `env=0`: Sandbox environment (for testing)
- `env=1`: Production environment

## Documentation

See `docs/plans/` for implementation details and API specifications.

## License

MIT
