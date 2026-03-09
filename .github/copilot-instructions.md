# WeChat Mini-Program Virtual Payment Python SDK

## Project Overview

A Python SDK that wraps WeChat's `xpay` server API (`https://api.weixin.qq.com/xpay/*`) for virtual currency (代币) payments in Mini Programs. Targets Python 3.8+.

## Architecture

```
wechat_xpay/
  __init__.py        - Public surface: XPayClient, XPayCallbackHandler, exceptions
  auth.py            - calc_pay_sig() and calc_signature() (HMAC-SHA256)
  client.py          - XPayClient: one method per API endpoint
  exceptions.py      - XPayError, XPayAPIError with errcode mapping
  models.py          - Dataclasses for all API response objects
  callbacks/
    __init__.py
    handler.py       - XPayCallbackHandler: parse + dispatch webhook events
    models.py        - Dataclasses for all push notification payloads
setup.py             - Package metadata
docs/apis.txt        - Authoritative API reference (DO NOT edit)
```

## Signature Mechanics (critical)

Two independent signatures, both HMAC-SHA256 hex digest:

| Sig | Key | Message |
|-----|-----|---------|
| `pay_sig` | `appKey` (env-specific) | `uri + '&' + post_body` |
| `signature` | `session_key` (per-user) | `post_body` |

- `uri` is the path only, no query string, e.g. `/xpay/query_user_balance`
- `post_body` must be the **exact bytes** sent in the HTTP POST body (same serialization)
- `env=0` → production `appKey`; `env=1` → sandbox `appKey`
- See `wechat_xpay/auth.py` and the reference implementation in `docs/apis.txt` lines 1060–1134

## API Endpoint Convention

Every `XPayClient` method follows this pattern:
1. Serialize the payload to a JSON string (`json.dumps`, keys sorted or in canonical order matching the docs)
2. Compute `pay_sig` (always required) and optionally `signature` (user-state endpoints)
3. `POST https://api.weixin.qq.com/xpay/{endpoint}?access_token={token}&pay_sig={}&signature={}` with `Content-Type: application/json`
4. Raise `XPayAPIError` if `errcode != 0`; return the parsed response model

Endpoints requiring **both** signatures: `query_user_balance`, `currency_pay`, `cancel_currency_pay`
All other endpoints require **only** `pay_sig`.

## Error Handling

`XPayAPIError` carries `.errcode` and `.errmsg`. Important codes (see `docs/apis.txt` lines 4–32):
- `268490004` – Duplicate operation (idempotent success for `present_currency`)
- `268490009` – Session key expired; caller must re-login
- `268490011` – Data generating, poll again
- `268490014` – Refund in progress, retry with same params

## Webhook Callbacks

Four push event types (JSON body):
- `xpay_goods_deliver_notify` → `GoodsDeliverNotify`
- `xpay_coin_pay_notify` → `CoinPayNotify`
- `xpay_refund_notify` → `RefundNotify`
- `xpay_complaint_notify` → `ComplaintNotify`

`XPayCallbackHandler.handle(body: str | dict)` parses the `Event` field, dispatches to registered handlers, and returns `{"ErrCode": 0, "ErrMsg": "success"}`. Handlers must be registered via `handler.on_goods_deliver(func)` etc.

## Build & Test

```bash
pip install -e ".[dev]"
pytest tests/
```

## Key Files

- [docs/apis.txt](docs/apis.txt) — full API spec and signature reference
- [wechat_xpay/auth.py](wechat_xpay/auth.py) — signature implementation
- [wechat_xpay/client.py](wechat_xpay/client.py) — all API methods
- [wechat_xpay/callbacks/handler.py](wechat_xpay/callbacks/handler.py) — webhook handler
