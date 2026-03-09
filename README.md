# WeChat XPay Python SDK

Python SDK for WeChat XPay (Virtual Payment) server-side APIs.

## Features

- ✅ **Sync & Async** - Supports both synchronous and asynchronous operations
- ✅ **Type Hints** - Full type annotation support
- ✅ **HTTP/2** - Built on httpx with HTTP/2 support
- ✅ **Webhook Parser** - Handle WeChat push notifications
- ✅ **Error Handling** - Comprehensive exception hierarchy with error codes

## Installation

```bash
pip install wechat-xpay
```

## Quick Start

### Synchronous Client

```python
from wechat_xpay import XPayClient

# Using context manager (recommended)
with XPayClient(
    app_id="your_app_id",
    app_key="your_app_key",
    env=0,  # 0=sandbox, 1=production
) as client:
    # session_key is passed per API call because it expires periodically
    balance = client.query_user_balance(
        openid="user_openid",
        session_key="user_session_key",
    )
    print(f"Balance: {balance.balance}")
    print(f"Present Balance: {balance.present_balance}")
```

### Asynchronous Client

```python
import asyncio
from wechat_xpay import XPayAsyncClient

async def main():
    # Using async context manager (recommended)
    async with XPayAsyncClient(
        app_id="your_app_id",
        app_key="your_app_key",
        env=0,
    ) as client:
        balance = await client.query_user_balance(
            openid="user_openid",
            session_key="user_session_key",
        )
        print(f"Balance: {balance.balance}")
        print(f"Present Balance: {balance.present_balance}")

asyncio.run(main())
```

## Why session_key is passed per API call?

WeChat's `session_key` has a lifecycle and expires periodically (typically 30 days).
When it expires, you need to re-authorize the user to get a new `session_key`.

By passing `session_key` per API call instead of at initialization:
- You can handle `session_key` expiration gracefully
- Different users can use the same client instance with their own `session_key`
- You can rotate `session_key` without recreating the client

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

### Synchronous Usage

```python
from wechat_xpay import XPayClient

with XPayClient(
    app_id="wx1234567890",
    app_key="your_app_key",
    env=0,
) as client:
    # Query user balance
    balance = client.query_user_balance(
        openid="user_openid",
        session_key="user_session_key",
    )
    print(f"Balance: {balance.balance}")
    print(f"Present: {balance.present_balance}")

    # Process payment
    result = client.currency_pay(
        openid="user_openid",
        session_key="user_session_key",
        out_trade_no="ORDER_123",
        order_fee=100,  # Amount in cents
        pay_item="Item description",
    )
    print(f"Order ID: {result.order_id}")

    # Refund order
    result = client.refund_order(
        openid="user_openid",
        session_key="user_session_key",
        refund_order_id="REFUND_123",
        left_fee=1000,
        refund_fee=500,
        refund_reason="1",  # Product issue
        req_from="1",  # Manual
        order_id="original_order_id",
    )
    print(f"Refund Order ID: {result.refund_order_id}")
```

### Asynchronous Usage

```python
import asyncio
from wechat_xpay import XPayAsyncClient

async def main():
    async with XPayAsyncClient(
        app_id="wx1234567890",
        app_key="your_app_key",
        env=0,
    ) as client:
        # Query user balance
        balance = await client.query_user_balance(
            openid="user_openid",
            session_key="user_session_key",
        )
        print(f"Balance: {balance.balance}")

        # Concurrent payments with different session_keys
        tasks = [
            client.currency_pay(
                openid=f"user_{i}",
                session_key=f"session_key_{i}",  # Each user has their own session_key
                out_trade_no=f"ORDER_{i}",
                order_fee=100,
                pay_item=f"Item {i}",
            )
            for i in range(3)
        ]
        results = await asyncio.gather(*tasks)
        for result in results:
            print(f"Order ID: {result.order_id}")

asyncio.run(main())
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

# Return success response to WeChat
response = parser.success_response()
```

## Error Handling

```python
from wechat_xpay import XPayClient
from wechat_xpay.exceptions import XPayAPIError, ERR_SESSION_KEY_EXPIRED

client = XPayClient(...)

try:
    balance = client.query_user_balance(
        openid="user_openid",
        session_key="user_session_key",
    )
except XPayAPIError as e:
    if e.errcode == ERR_SESSION_KEY_EXPIRED:
        print("Session expired, please re-login")
        # Re-authorize user to get new session_key
    else:
        print(f"API Error: {e.errcode} - {e.errmsg}")
```

## Client Lifecycle Management

### Synchronous Client

```python
# Option 1: Context manager (auto close)
with XPayClient(...) as client:
    result = client.query_user_balance(...)

# Option 2: Manual close
client = XPayClient(...)
try:
    result = client.query_user_balance(...)
finally:
    client.close()
```

### Asynchronous Client

```python
# Option 1: Async context manager (auto close)
async with XPayAsyncClient(...) as client:
    result = await client.query_user_balance(...)

# Option 2: Manual close
client = XPayAsyncClient(...)
try:
    result = await client.query_user_balance(...)
finally:
    await client.close()
```

## Authentication

The SDK handles two types of signatures automatically:
- **pay_sig**: Signed with AppKey for API authentication (configured at client initialization)
- **signature**: Signed with user's session_key for user state verification (passed per API call)

## Environment

- `env=0`: Sandbox environment (for testing)
- `env=1`: Production environment

## Documentation

See `docs/plans/` for implementation details and API specifications.

## License

MIT
