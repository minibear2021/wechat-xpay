# WeChat XPay SDK Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a complete WeChat XPay (virtual payment) Python SDK with all server-side APIs, proper error handling, and webhook message parsing.

**Architecture:** A single client class `XPayClient` holds configuration and exposes methods for each API endpoint. HTTP layer uses `requests` library. All responses are parsed into dataclasses from `models.py`. Webhook handlers use a separate `WebhookParser` class to parse and validate incoming push messages.

**Tech Stack:** Python 3.9+, requests, dataclasses, pytest, pytest-mock, responses (for HTTP mocking)

---

## Prerequisites

Create virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install requests pytest pytest-mock responses
```

---

## Task 1: Project Structure Setup

**Files:**
- Create: `wechat_xpay/__init__.py`
- Create: `wechat_xpay/client.py`
- Create: `tests/__init__.py`
- Create: `tests/test_client.py`
- Create: `tests/test_auth.py`
- Modify: `wechat_xpay/exceptions.py` (add missing error codes)

**Step 1: Create package init file**

`wechat_xpay/__init__.py`:
```python
"""WeChat XPay (Virtual Payment) Python SDK."""

from wechat_xpay.auth import calc_pay_sig, calc_signature
from wechat_xpay.client import XPayClient
from wechat_xpay.exceptions import XPayError, XPayAPIError

__all__ = [
    "calc_pay_sig",
    "calc_signature",
    "XPayClient",
    "XPayError",
    "XPayAPIError",
]
```

**Step 2: Add missing error codes to exceptions**

`wechat_xpay/exceptions.py` (modify existing file, add after line 31):
```python
# Additional error codes for advertising funds and account operations
# 268490018   Advertising fund account industry ID mismatch
# 268490019   Advertising fund account ID already bound to another appid
# 268490020   Advertising fund account entity name error
# 268490021   Account onboarding incomplete
# 268490022   Advertising fund account invalid
# 268490023   Insufficient advertising fund balance
# 268490024   Advertising fund recharge amount must be greater than 0
```

**Step 3: Create test init**

`tests/__init__.py`:
```python
"""Tests for WeChat XPay SDK."""
```

**Step 4: Commit**

```bash
git add wechat_xpay/__init__.py tests/__init__.py wechat_xpay/exceptions.py
git commit -m "chore: setup project structure and package init"
```

---

## Task 2: Client Base Class and HTTP Layer

**Files:**
- Create: `wechat_xpay/client.py` (base structure)
- Test: `tests/test_client.py` (base tests)

**Step 1: Write the failing test for client initialization**

`tests/test_client.py`:
```python
"""Tests for XPayClient."""
import pytest
from wechat_xpay import XPayClient


class TestXPayClientInit:
    """Test client initialization."""

    def test_client_init_with_all_params(self):
        """Client should initialize with all required parameters."""
        client = XPayClient(
            app_id="wx1234567890",
            app_key_sandbox="sandbox_key_123",
            app_key_production="prod_key_456",
        )
        assert client.app_id == "wx1234567890"
        assert client.app_key_sandbox == "sandbox_key_123"
        assert client.app_key_production == "prod_key_456"

    def test_client_init_with_access_token(self):
        """Client should accept optional access_token."""
        client = XPayClient(
            app_id="wx1234567890",
            app_key_sandbox="sandbox_key",
            app_key_production="prod_key",
            access_token="token_123",
        )
        assert client.access_token == "token_123"
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_client.py::TestXPayClientInit -v
```
Expected: FAIL with "XPayClient not defined"

**Step 3: Write minimal implementation**

`wechat_xpay/client.py` (initial structure):
```python
"""XPayClient for WeChat XPay server API."""
from __future__ import annotations

import json
from typing import Any, Optional

import requests

from wechat_xpay.auth import calc_pay_sig, calc_signature
from wechat_xpay.exceptions import XPayAPIError

BASE_URL = "https://api.weixin.qq.com"


class XPayClient:
    """Client for WeChat XPay server API.

    Args:
        app_id: Mini program AppID
        app_key_sandbox: Sandbox environment AppKey
        app_key_production: Production environment AppKey
        access_token: Optional access token (can be set later or per-request)
    """

    def __init__(
        self,
        app_id: str,
        app_key_sandbox: str,
        app_key_production: str,
        access_token: Optional[str] = None,
    ):
        self.app_id = app_id
        self.app_key_sandbox = app_key_sandbox
        self.app_key_production = app_key_production
        self.access_token = access_token

    def _get_app_key(self, env: int) -> str:
        """Get AppKey for the specified environment.

        Args:
            env: 0 for production, 1 for sandbox

        Returns:
            AppKey string
        """
        return self.app_key_sandbox if env == 1 else self.app_key_production

    def _build_url(
        self,
        uri: str,
        post_body: str,
        env: int,
        session_key: Optional[str] = None,
        need_pay_sig: bool = True,
        need_signature: bool = False,
    ) -> str:
        """Build full URL with signatures.

        Args:
            uri: API path (e.g., '/xpay/query_user_balance')
            post_body: JSON string to be sent as POST body
            env: 0 for production, 1 for sandbox
            session_key: User session key (required for signature)
            need_pay_sig: Whether to include pay_sig
            need_signature: Whether to include signature

        Returns:
            Complete URL with query parameters
        """
        access_token = self.access_token or ""
        url = f"{BASE_URL}{uri}?access_token={access_token}"

        if need_pay_sig:
            app_key = self._get_app_key(env)
            pay_sig = calc_pay_sig(uri, post_body, app_key)
            url += f"&pay_sig={pay_sig}"

        if need_signature:
            if session_key is None:
                raise ValueError("session_key is required for signature")
            signature = calc_signature(post_body, session_key)
            url += f"&signature={signature}"

        return url

    def _request(
        self,
        method: str,
        uri: str,
        data: dict[str, Any],
        env: int = 0,
        session_key: Optional[str] = None,
        need_pay_sig: bool = True,
        need_signature: bool = False,
    ) -> dict[str, Any]:
        """Make HTTP request to XPay API.

        Args:
            method: HTTP method (GET, POST, etc.)
            uri: API path
            data: Request body data
            env: 0 for production, 1 for sandbox
            session_key: User session key for signature
            need_pay_sig: Whether to include pay_sig
            need_signature: Whether to include signature

        Returns:
            Parsed JSON response

        Raises:
            XPayAPIError: If API returns non-zero errcode
        """
        post_body = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        url = self._build_url(uri, post_body, env, session_key, need_pay_sig, need_signature)

        response = requests.post(url, data=post_body.encode("utf-8"), headers={
            "Content-Type": "application/json"
        })
        response.raise_for_status()

        result = response.json()

        errcode = result.get("errcode", 0)
        if errcode != 0:
            raise XPayAPIError(errcode, result.get("errmsg", "Unknown error"))

        return result
```

**Step 4: Run tests to verify they pass**

```bash
pytest tests/test_client.py::TestXPayClientInit -v
```
Expected: PASS

**Step 5: Commit**

```bash
git add wechat_xpay/client.py tests/test_client.py
git commit -m "feat: add XPayClient base class with HTTP layer"
```

---

## Task 3: User Token Management APIs

**Files:**
- Modify: `wechat_xpay/client.py` (add methods)
- Test: `tests/test_client.py` (add tests)

**Step 1: Write the failing test for query_user_balance**

Add to `tests/test_client.py`:
```python
import responses
from wechat_xpay.models import UserBalance, CurrencyPayResult


class TestUserTokenAPIs:
    """Test user token management APIs."""

    @responses.activate
    def test_query_user_balance(self):
        """Test querying user balance."""
        responses.add(
            responses.POST,
            "https://api.weixin.qq.com/xpay/query_user_balance",
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
            status=200,
        )

        client = XPayClient(
            app_id="wx123",
            app_key_sandbox="sandbox_key",
            app_key_production="prod_key",
            access_token="token_123",
        )

        result = client.query_user_balance(
            openid="user_openid_123",
            env=0,
            user_ip="1.1.1.1",
            session_key="session_key_456",
        )

        assert isinstance(result, UserBalance)
        assert result.balance == 1000
        assert result.present_balance == 200
        assert result.first_save_flag is True
```

**Step 2: Run test to verify it fails**

```bash
pytest tests/test_client.py::TestUserTokenAPIs::test_query_user_balance -v
```
Expected: FAIL with "XPayClient has no attribute query_user_balance"

**Step 3: Write minimal implementation**

Add to `wechat_xpay/client.py` (after `_request` method):
```python
from wechat_xpay.models import (
    UserBalance,
    CurrencyPayResult,
    CancelCurrencyPayResult,
    PresentCurrencyResult,
)


def query_user_balance(
    self,
    openid: str,
    env: int,
    user_ip: str,
    session_key: str,
) -> UserBalance:
    """Query user's token balance.

    Requires both pay_sig and signature.

    Args:
        openid: User's OpenID
        env: 0 for production, 1 for sandbox
        user_ip: User IP address (e.g., "1.1.1.1")
        session_key: User's session key for signature

    Returns:
        UserBalance dataclass
    """
    uri = "/xpay/query_user_balance"
    data = {
        "openid": openid,
        "env": env,
        "user_ip": user_ip,
    }
    result = self._request(
        "POST", uri, data, env, session_key,
        need_pay_sig=True, need_signature=True
    )
    return UserBalance(
        balance=result["balance"],
        present_balance=result["present_balance"],
        sum_save=result["sum_save"],
        sum_present=result["sum_present"],
        sum_balance=result["sum_balance"],
        sum_cost=result["sum_cost"],
        first_save_flag=result["first_save_flag"],
    )
```

**Step 4: Run test to verify it passes**

```bash
pytest tests/test_client.py::TestUserTokenAPIs::test_query_user_balance -v
```
Expected: PASS

**Step 5: Add currency_pay method and test**

Add test to `tests/test_client.py`:
```python
@responses.activate
def test_currency_pay(self):
    """Test currency payment."""
    responses.add(
        responses.POST,
        "https://api.weixin.qq.com/xpay/currency_pay",
        json={
            "errcode": 0,
            "errmsg": "ok",
            "order_id": "order_123",
            "balance": 800,
            "used_present_amount": 100,
        },
        status=200,
    )

    client = XPayClient(
        app_id="wx123",
        app_key_sandbox="sandbox_key",
        app_key_production="prod_key",
        access_token="token_123",
    )

    result = client.currency_pay(
        openid="user_openid_123",
        env=0,
        user_ip="1.1.1.1",
        amount=200,
        order_id="order_123",
        payitem='[{"productid":"item1", "unit_price": 100, "quantity": 2}]',
        remark="Test payment",
        session_key="session_key_456",
    )

    assert isinstance(result, CurrencyPayResult)
    assert result.order_id == "order_123"
    assert result.balance == 800
    assert result.used_present_amount == 100
```

Add implementation to `wechat_xpay/client.py`:
```python
def currency_pay(
    self,
    openid: str,
    env: int,
    user_ip: str,
    amount: int,
    order_id: str,
    payitem: str,
    remark: str,
    session_key: str,
) -> CurrencyPayResult:
    """Deduct tokens (usually for payment).

    Requires both pay_sig and signature.

    Args:
        openid: User's OpenID
        env: 0 for production, 1 for sandbox
        user_ip: User IP address
        amount: Token amount to pay
        order_id: Order ID
        payitem: Item info as JSON string
        remark: Remark/note
        session_key: User's session key for signature

    Returns:
        CurrencyPayResult dataclass
    """
    uri = "/xpay/currency_pay"
    data = {
        "openid": openid,
        "env": env,
        "user_ip": user_ip,
        "amount": amount,
        "order_id": order_id,
        "payitem": payitem,
        "remark": remark,
    }
    result = self._request(
        "POST", uri, data, env, session_key,
        need_pay_sig=True, need_signature=True
    )
    return CurrencyPayResult(
        order_id=result["order_id"],
        balance=result["balance"],
        used_present_amount=result["used_present_amount"],
    )
```

**Step 6: Run tests**

```bash
pytest tests/test_client.py::TestUserTokenAPIs -v
```
Expected: PASS

**Step 7: Commit**

```bash
git add wechat_xpay/client.py tests/test_client.py
git commit -m "feat: add user token management APIs (query_user_balance, currency_pay)"
```

---

## Task 4: Order Management APIs

**Files:**
- Modify: `wechat_xpay/client.py`
- Test: `tests/test_client.py`

**Step 1: Write failing test for query_order**

Add to `tests/test_client.py`:
```python
from wechat_xpay.models import Order, CancelCurrencyPayResult


class TestOrderAPIs:
    """Test order management APIs."""

    @responses.activate
    def test_query_order(self):
        """Test querying order."""
        responses.add(
            responses.POST,
            "https://api.weixin.qq.com/xpay/query_order",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "order": {
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
            },
            status=200,
        )

        client = XPayClient(
            app_id="wx123",
            app_key_sandbox="sandbox_key",
            app_key_production="prod_key",
            access_token="token_123",
        )

        result = client.query_order(
            openid="user_openid_123",
            env=0,
            order_id="order_123",
        )

        assert isinstance(result, Order)
        assert result.order_id == "order_123"
        assert result.status == 2
```

**Step 2: Run test to verify it fails**

**Step 3: Write implementation**

Add to `wechat_xpay/client.py`:
```python
from wechat_xpay.models import Order  # add to existing imports


def query_order(
    self,
    openid: str,
    env: int,
    order_id: Optional[str] = None,
    wx_order_id: Optional[str] = None,
) -> Order:
    """Query created order (cash order, not token order).

    Requires pay_sig only.

    Args:
        openid: User's OpenID
        env: 0 for production, 1 for sandbox
        order_id: Order ID (either order_id or wx_order_id required)
        wx_order_id: WeChat internal order ID

    Returns:
        Order dataclass
    """
    uri = "/xpay/query_order"
    data: dict[str, Any] = {
        "openid": openid,
        "env": env,
    }
    if order_id:
        data["order_id"] = order_id
    if wx_order_id:
        data["wx_order_id"] = wx_order_id

    result = self._request(
        "POST", uri, data, env,
        need_pay_sig=True, need_signature=False
    )
    order_data = result["order"]
    return Order(
        order_id=order_data["order_id"],
        create_time=order_data["create_time"],
        update_time=order_data["update_time"],
        status=order_data["status"],
        biz_type=order_data["biz_type"],
        order_fee=order_data["order_fee"],
        paid_fee=order_data["paid_fee"],
        order_type=order_data["order_type"],
        env_type=order_data["env_type"],
        coupon_fee=order_data.get("coupon_fee"),
        refund_fee=order_data.get("refund_fee"),
        paid_time=order_data.get("paid_time"),
        provide_time=order_data.get("provide_time"),
        biz_meta=order_data.get("biz_meta"),
        token=order_data.get("token"),
        left_fee=order_data.get("left_fee"),
        wx_order_id=order_data.get("wx_order_id"),
        channel_order_id=order_data.get("channel_order_id"),
        wxpay_order_id=order_data.get("wxpay_order_id"),
        sett_time=order_data.get("sett_time"),
        sett_state=order_data.get("sett_state"),
        platform_fee_fen=order_data.get("platform_fee_fen"),
        cps_fee_fen=order_data.get("cps_fee_fen"),
    )
```

**Step 4: Run tests**

**Step 5: Add cancel_currency_pay and present_currency**

Add tests:
```python
@responses.activate
def test_cancel_currency_pay(self):
    """Test cancel currency pay (refund)."""
    responses.add(
        responses.POST,
        "https://api.weixin.qq.com/xpay/cancel_currency_pay",
        json={
            "errcode": 0,
            "errmsg": "ok",
            "order_id": "refund_order_123",
        },
        status=200,
    )

    client = XPayClient(
        app_id="wx123",
        app_key_sandbox="sandbox_key",
        app_key_production="prod_key",
        access_token="token_123",
    )

    result = client.cancel_currency_pay(
        openid="user_openid_123",
        env=0,
        user_ip="1.1.1.1",
        pay_order_id="original_order_123",
        order_id="refund_order_123",
        amount=100,
        session_key="session_key_456",
    )

    assert isinstance(result, CancelCurrencyPayResult)
    assert result.order_id == "refund_order_123"

@responses.activate
def test_present_currency(self):
    """Test presenting currency to user."""
    responses.add(
        responses.POST,
        "https://api.weixin.qq.com/xpay/present_currency",
        json={
            "errcode": 0,
            "errmsg": "ok",
            "balance": 1200,
            "order_id": "present_order_123",
            "present_balance": 400,
        },
        status=200,
    )

    client = XPayClient(
        app_id="wx123",
        app_key_sandbox="sandbox_key",
        app_key_production="prod_key",
        access_token="token_123",
    )

    result = client.present_currency(
        openid="user_openid_123",
        env=0,
        order_id="present_order_123",
        amount=200,
    )

    assert isinstance(result, PresentCurrencyResult)
    assert result.balance == 1200
    assert result.present_balance == 400
```

Add implementations:
```python
def cancel_currency_pay(
    self,
    openid: str,
    env: int,
    user_ip: str,
    pay_order_id: str,
    order_id: str,
    amount: int,
    session_key: str,
) -> CancelCurrencyPayResult:
    """Refund currency payment (reverse of currency_pay).

    Requires both pay_sig and signature.

    Args:
        openid: User's OpenID
        env: 0 for production, 1 for sandbox
        user_ip: User IP address
        pay_order_id: Original currency_pay order ID
        order_id: Refund order ID
        amount: Refund amount
        session_key: User's session key for signature

    Returns:
        CancelCurrencyPayResult dataclass
    """
    uri = "/xpay/cancel_currency_pay"
    data = {
        "openid": openid,
        "env": env,
        "user_ip": user_ip,
        "pay_order_id": pay_order_id,
        "order_id": order_id,
        "amount": amount,
    }
    result = self._request(
        "POST", uri, data, env, session_key,
        need_pay_sig=True, need_signature=True
    )
    return CancelCurrencyPayResult(order_id=result["order_id"])


def present_currency(
    self,
    openid: str,
    env: int,
    order_id: str,
    amount: int,
) -> PresentCurrencyResult:
    """Present/gift currency to user.

    Requires pay_sig only.
    Note: Retry until returning 0 or 268490004 (duplicate operation).

    Args:
        openid: User's OpenID
        env: 0 for production, 1 for sandbox
        order_id: Present order ID
        amount: Present amount

    Returns:
        PresentCurrencyResult dataclass
    """
    uri = "/xpay/present_currency"
    data = {
        "openid": openid,
        "env": env,
        "order_id": order_id,
        "amount": amount,
    }
    result = self._request(
        "POST", uri, data, env,
        need_pay_sig=True, need_signature=False
    )
    return PresentCurrencyResult(
        balance=result["balance"],
        order_id=result["order_id"],
        present_balance=result["present_balance"],
    )
```

**Step 6: Run tests**

```bash
pytest tests/test_client.py::TestOrderAPIs -v
```

**Step 7: Commit**

```bash
git add wechat_xpay/client.py tests/test_client.py
git commit -m "feat: add order management APIs (query_order, cancel_currency_pay, present_currency)"
```

---

## Task 5: Remaining APIs (Refund, Withdraw, Goods, Bill)

**Files:**
- Modify: `wechat_xpay/client.py`
- Test: `tests/test_client.py`

Add remaining methods in one batch:

1. `notify_provide_goods` - Notify goods delivery complete
2. `refund_order` - Refund cash order
3. `create_withdraw_order` - Create withdrawal order
4. `query_withdraw_order` - Query withdrawal order
5. `start_upload_goods` - Start goods upload task
6. `query_upload_goods` - Query goods upload status
7. `start_publish_goods` - Start goods publish task
8. `query_publish_goods` - Query goods publish status
9. `download_bill` - Download bill

Each method follows same pattern as above. Add all tests first, then implementations.

**Step 1: Add tests for remaining APIs**

Add comprehensive tests to `tests/test_client.py`:

```python
from wechat_xpay.models import (
    RefundOrderResult,
    WithdrawOrderResult,
    WithdrawOrder,
    GoodsUploadStatus,
    GoodsPublishStatus,
    BillDownload,
)


class TestRemainingAPIs:
    """Test remaining APIs."""

    @responses.activate
    def test_notify_provide_goods(self):
        """Test notify provide goods."""
        responses.add(
            responses.POST,
            "https://api.weixin.qq.com/xpay/notify_provide_goods",
            json={"errcode": 0, "errmsg": "ok"},
            status=200,
        )

        client = XPayClient(
            app_id="wx123",
            app_key_sandbox="sandbox_key",
            app_key_production="prod_key",
            access_token="token_123",
        )

        result = client.notify_provide_goods(
            order_id="order_123",
            env=0,
        )

        assert result is True

    @responses.activate
    def test_refund_order(self):
        """Test refund order."""
        responses.add(
            responses.POST,
            "https://api.weixin.qq.com/xpay/refund_order",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "refund_order_id": "refund_123",
                "refund_wx_order_id": "wx_refund_456",
                "pay_order_id": "order_123",
                "pay_wx_order_id": "wx_order_456",
            },
            status=200,
        )

        client = XPayClient(
            app_id="wx123",
            app_key_sandbox="sandbox_key",
            app_key_production="prod_key",
            access_token="token_123",
        )

        result = client.refund_order(
            openid="user_openid_123",
            order_id="order_123",
            refund_order_id="refund_123",
            left_fee=1000,
            refund_fee=500,
            refund_reason="0",
            req_from="1",
            env=0,
        )

        assert isinstance(result, RefundOrderResult)
        assert result.refund_order_id == "refund_123"

    @responses.activate
    def test_create_withdraw_order(self):
        """Test create withdraw order."""
        responses.add(
            responses.POST,
            "https://api.weixin.qq.com/xpay/create_withdraw_order",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "withdraw_no": "withdraw_123",
                "wx_withdraw_no": "wx_withdraw_456",
            },
            status=200,
        )

        client = XPayClient(
            app_id="wx123",
            app_key_sandbox="sandbox_key",
            app_key_production="prod_key",
            access_token="token_123",
        )

        result = client.create_withdraw_order(
            withdraw_no="withdraw_123",
            withdraw_amount="100.00",
            env=0,
        )

        assert isinstance(result, WithdrawOrderResult)
        assert result.withdraw_no == "withdraw_123"

    @responses.activate
    def test_query_withdraw_order(self):
        """Test query withdraw order."""
        responses.add(
            responses.POST,
            "https://api.weixin.qq.com/xpay/query_withdraw_order",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "withdraw_no": "withdraw_123",
                "status": 2,
                "withdraw_amount": "100.00",
                "wx_withdraw_no": "wx_withdraw_456",
            },
            status=200,
        )

        client = XPayClient(
            app_id="wx123",
            app_key_sandbox="sandbox_key",
            app_key_production="prod_key",
            access_token="token_123",
        )

        result = client.query_withdraw_order(
            withdraw_no="withdraw_123",
            env=0,
        )

        assert isinstance(result, WithdrawOrder)
        assert result.status == 2

    @responses.activate
    def test_download_bill(self):
        """Test download bill."""
        responses.add(
            responses.POST,
            "https://api.weixin.qq.com/xpay/download_bill",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "url": "https://example.com/bill.csv",
            },
            status=200,
        )

        client = XPayClient(
            app_id="wx123",
            app_key_sandbox="sandbox_key",
            app_key_production="prod_key",
            access_token="token_123",
        )

        result = client.download_bill(
            begin_ds=20230801,
            end_ds=20230810,
            env=0,
        )

        assert isinstance(result, BillDownload)
        assert result.url == "https://example.com/bill.csv"
```

**Step 2: Add implementations**

Add to `wechat_xpay/client.py`:

```python
def notify_provide_goods(
    self,
    env: int,
    order_id: Optional[str] = None,
    wx_order_id: Optional[str] = None,
) -> bool:
    """Notify that goods delivery is complete.

    Used for exception cases when push notification fails.
    Requires pay_sig only.

    Args:
        env: 0 for production, 1 for sandbox
        order_id: Order ID (either order_id or wx_order_id required)
        wx_order_id: WeChat internal order ID

    Returns:
        True on success
    """
    uri = "/xpay/notify_provide_goods"
    data: dict[str, Any] = {"env": env}
    if order_id:
        data["order_id"] = order_id
    if wx_order_id:
        data["wx_order_id"] = wx_order_id

    self._request(
        "POST", uri, data, env,
        need_pay_sig=True, need_signature=False
    )
    return True


def refund_order(
    self,
    openid: str,
    refund_order_id: str,
    left_fee: int,
    refund_fee: int,
    refund_reason: str,
    req_from: str,
    env: int,
    order_id: Optional[str] = None,
    wx_order_id: Optional[str] = None,
    biz_meta: Optional[str] = None,
) -> RefundOrderResult:
    """Refund a cash order created via jsapi.

    This only starts the refund task. Poll query_order to check status.
    Requires pay_sig only.

    Args:
        openid: User's OpenID
        refund_order_id: Refund order ID (8-32 chars, alphanumeric + '_' + '-')
        left_fee: Current refundable amount (query from query_order)
        refund_fee: Refund amount (0 < refund_fee <= left_fee)
        refund_reason: "0"-none, "1"-product issue, "2"-service, "3"-user request, "4"-price, "5"-other
        req_from: "1"-manual, "2"-user initiated, "3"-other
        env: 0 for production, 1 for sandbox
        order_id: Original order ID
        wx_order_id: WeChat order ID
        biz_meta: Custom data (0-1024 chars)

    Returns:
        RefundOrderResult dataclass
    """
    uri = "/xpay/refund_order"
    data: dict[str, Any] = {
        "openid": openid,
        "refund_order_id": refund_order_id,
        "left_fee": left_fee,
        "refund_fee": refund_fee,
        "refund_reason": refund_reason,
        "req_from": req_from,
        "env": env,
    }
    if order_id:
        data["order_id"] = order_id
    if wx_order_id:
        data["wx_order_id"] = wx_order_id
    if biz_meta:
        data["biz_meta"] = biz_meta

    result = self._request(
        "POST", uri, data, env,
        need_pay_sig=True, need_signature=False
    )
    return RefundOrderResult(
        refund_order_id=result["refund_order_id"],
        refund_wx_order_id=result["refund_wx_order_id"],
        pay_order_id=result["pay_order_id"],
        pay_wx_order_id=result["pay_wx_order_id"],
    )


def create_withdraw_order(
    self,
    withdraw_no: str,
    env: int,
    withdraw_amount: Optional[str] = None,
) -> WithdrawOrderResult:
    """Create withdrawal order.

    Requires pay_sig only.

    Args:
        withdraw_no: Withdrawal order number (8-32 chars, alphanumeric + '_' + '-')
        env: 0 for production, 1 for sandbox
        withdraw_amount: Amount in yuan (e.g., "0.01"), omit for full withdrawal

    Returns:
        WithdrawOrderResult dataclass
    """
    uri = "/xpay/create_withdraw_order"
    data: dict[str, Any] = {
        "withdraw_no": withdraw_no,
        "env": env,
    }
    if withdraw_amount:
        data["withdraw_amount"] = withdraw_amount

    result = self._request(
        "POST", uri, data, env,
        need_pay_sig=True, need_signature=False
    )
    return WithdrawOrderResult(
        withdraw_no=result["withdraw_no"],
        wx_withdraw_no=result["wx_withdraw_no"],
    )


def query_withdraw_order(
    self,
    withdraw_no: str,
    env: int,
) -> WithdrawOrder:
    """Query withdrawal order.

    Requires pay_sig only.

    Args:
        withdraw_no: Withdrawal order number
        env: 0 for production, 1 for sandbox

    Returns:
        WithdrawOrder dataclass
    """
    uri = "/xpay/query_withdraw_order"
    data = {
        "withdraw_no": withdraw_no,
        "env": env,
    }
    result = self._request(
        "POST", uri, data, env,
        need_pay_sig=True, need_signature=False
    )
    return WithdrawOrder(
        withdraw_no=result["withdraw_no"],
        status=result["status"],
        withdraw_amount=result["withdraw_amount"],
        wx_withdraw_no=result["wx_withdraw_no"],
        withdraw_success_timestamp=result.get("withdraw_success_timestamp"),
        create_time=result.get("create_time"),
        fail_reason=result.get("fail_reason"),
    )


def download_bill(
    self,
    begin_ds: int,
    end_ds: int,
    env: int,
) -> BillDownload:
    """Download mini program bill.

    First call triggers URL generation, poll to get final URL.
    Requires pay_sig only.

    Args:
        begin_ds: Start date (e.g., 20230801)
        end_ds: End date (e.g., 20230810)
        env: 0 for production, 1 for sandbox

    Returns:
        BillDownload dataclass with URL (valid for 30 minutes)
    """
    uri = "/xpay/download_bill"
    data = {
        "begin_ds": begin_ds,
        "end_ds": end_ds,
    }
    result = self._request(
        "POST", uri, data, env,
        need_pay_sig=True, need_signature=False
    )
    return BillDownload(url=result["url"])
```

**Step 3: Run all tests**

```bash
pytest tests/test_client.py -v
```

**Step 4: Commit**

```bash
git add wechat_xpay/client.py tests/test_client.py
git commit -m "feat: add remaining core APIs (refund, withdraw, bill download)"
```

---

## Task 6: Business Balance and Advertising Fund APIs

**Files:**
- Modify: `wechat_xpay/client.py`
- Test: `tests/test_client.py`

Add methods for:
1. `query_biz_balance` - Query business withdrawable balance
2. `query_transfer_account` - Query advertising fund accounts
3. `query_adver_funds` - Query advertising fund distribution records
4. `create_funds_bill` - Create advertising fund bill
5. `bind_transfer_accout` - Bind advertising fund account
6. `query_funds_bill` - Query advertising fund bills
7. `query_recover_bill` - Query advertising fund recovery records
8. `download_adverfunds_order` - Download advertising fund orders

**Step 1: Add tests**

```python
from wechat_xpay.models import (
    BizBalance,
    TransferAccount,
    AdverFundList,
    FundsBillResult,
    FundsBillList,
    RecoverBillList,
)


class TestAdvertisingFundAPIs:
    """Test advertising fund APIs."""

    @responses.activate
    def test_query_biz_balance(self):
        """Test query business balance."""
        responses.add(
            responses.POST,
            "https://api.weixin.qq.com/xpay/query_biz_balance",
            json={
                "errcode": 0,
                "errmsg": "ok",
                "balance_available": {
                    "amount": "1000.00",
                    "currency_code": "CNY",
                },
            },
            status=200,
        )

        client = XPayClient(
            app_id="wx123",
            app_key_sandbox="sandbox_key",
            app_key_production="prod_key",
            access_token="token_123",
        )

        result = client.query_biz_balance(env=0)

        assert isinstance(result, BizBalance)
        assert result.balance_available.amount == "1000.00"

    @responses.activate
    def test_query_transfer_account(self):
        """Test query transfer account."""
        responses.add(
            responses.POST,
            "https://api.weixin.qq.com/xpay/query_transfer_account",
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
            status=200,
        )

        client = XPayClient(
            app_id="wx123",
            app_key_sandbox="sandbox_key",
            app_key_production="prod_key",
            access_token="token_123",
        )

        result = client.query_transfer_account(env=0)

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TransferAccount)
        assert result[0].transfer_account_name == "Account 1"

    @responses.activate
    def test_query_adver_funds(self):
        """Test query advertising funds."""
        responses.add(
            responses.POST,
            "https://api.weixin.qq.com/xpay/query_adver_funds",
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
            status=200,
        )

        client = XPayClient(
            app_id="wx123",
            app_key_sandbox="sandbox_key",
            app_key_production="prod_key",
            access_token="token_123",
        )

        result = client.query_adver_funds(
            page=1,
            page_size=10,
            env=0,
        )

        assert isinstance(result, AdverFundList)
        assert result.total_page == 1
        assert len(result.adver_funds_list) == 1
```

**Step 2: Add implementations**

```python
def query_biz_balance(self, env: int) -> BizBalance:
    """Query business withdrawable balance.

    Requires pay_sig only.
    Note: Results are always from production environment.

    Args:
        env: 0 for production, 1 for sandbox (only for signature verification)

    Returns:
        BizBalance dataclass
    """
    uri = "/xpay/query_biz_balance"
    data = {"env": env}
    result = self._request(
        "POST", uri, data, env,
        need_pay_sig=True, need_signature=False
    )
    balance_data = result["balance_available"]
    return BizBalance(
        balance_available=BizBalanceAvailable(
            amount=balance_data["amount"],
            currency_code=balance_data["currency_code"],
        )
    )


def query_transfer_account(self, env: int) -> list[TransferAccount]:
    """Query advertising fund transfer accounts.

    Requires pay_sig only.
    Note: Results are always from production environment.

    Args:
        env: 0 for production, 1 for sandbox (only for signature verification)

    Returns:
        List of TransferAccount dataclasses
    """
    uri = "/xpay/query_transfer_account"
    data = {"env": env}
    result = self._request(
        "POST", uri, data, env,
        need_pay_sig=True, need_signature=False
    )
    return [
        TransferAccount(
            transfer_account_name=acct["transfer_account_name"],
            transfer_account_uid=acct["transfer_account_uid"],
            transfer_account_agency_id=acct["transfer_account_agency_id"],
            transfer_account_agency_name=acct["transfer_account_agency_name"],
            state=acct["state"],
            bind_result=acct["bind_result"],
            error_msg=acct.get("error_msg"),
        )
        for acct in result.get("acct_list", [])
    ]


def query_adver_funds(
    self,
    page: int,
    page_size: int,
    env: int,
    filter_params: Optional[dict] = None,
) -> AdverFundList:
    """Query advertising fund distribution records.

    Requires pay_sig only.
    Note: Results are always from production environment.

    Args:
        page: Page number (>= 1)
        page_size: Records per page
        env: 0 for production, 1 for sandbox (only for signature verification)
        filter_params: Optional filter with settle_begin, settle_end, fund_type

    Returns:
        AdverFundList dataclass
    """
    uri = "/xpay/query_adver_funds"
    data: dict[str, Any] = {
        "page": page,
        "page_size": page_size,
        "env": env,
    }
    if filter_params:
        data["filter"] = filter_params

    result = self._request(
        "POST", uri, data, env,
        need_pay_sig=True, need_signature=False
    )
    return AdverFundList(
        total_page=result["total_page"],
        adver_funds_list=[
            AdverFund(
                settle_begin=fund["settle_begin"],
                settle_end=fund["settle_end"],
                total_amount=fund["total_amount"],
                remain_amount=fund["remain_amount"],
                expire_time=fund["expire_time"],
                fund_type=fund["fund_type"],
                fund_id=fund["fund_id"],
            )
            for fund in result.get("adver_funds_list", [])
        ],
    )
```

**Step 3: Run tests and commit**

```bash
pytest tests/test_client.py::TestAdvertisingFundAPIs -v
git add wechat_xpay/client.py tests/test_client.py
git commit -m "feat: add advertising fund APIs (biz balance, transfer account, adver funds)"
```

---

## Task 7: Complaint Management APIs

**Files:**
- Modify: `wechat_xpay/client.py`
- Test: `tests/test_client.py`

Add methods for:
1. `get_complaint_list` - Get complaint list
2. `get_complaint_detail` - Get complaint detail
3. `get_negotiation_history` - Get negotiation history
4. `response_complaint` - Response to complaint
5. `complete_complaint` - Complete complaint handling
6. `upload_vp_file` - Upload media file
7. `get_upload_file_sign` - Get upload file signature

**Step 1: Add tests**

```python
from wechat_xpay.models import (
    ComplaintList,
    Complaint,
    NegotiationHistory,
    UploadFileResult,
    UploadFileSign,
)


class TestComplaintAPIs:
    """Test complaint management APIs."""

    @responses.activate
    def test_get_complaint_list(self):
        """Test get complaint list."""
        responses.add(
            responses.POST,
            "https://api.weixin.qq.com/xpay/get_complaint_list",
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
            status=200,
        )

        client = XPayClient(
            app_id="wx123",
            app_key_sandbox="sandbox_key",
            app_key_production="prod_key",
            access_token="token_123",
        )

        result = client.get_complaint_list(
            env=0,
            begin_date="2023-01-01",
            end_date="2023-12-31",
            offset=0,
            limit=10,
        )

        assert isinstance(result, ComplaintList)
        assert result.total == 1
        assert len(result.complaints) == 1
        assert result.complaints[0].complaint_id == "complaint_123"

    @responses.activate
    def test_get_complaint_detail(self):
        """Test get complaint detail."""
        responses.add(
            responses.POST,
            "https://api.weixin.qq.com/xpay/get_complaint_detail",
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
            status=200,
        )

        client = XPayClient(
            app_id="wx123",
            app_key_sandbox="sandbox_key",
            app_key_production="prod_key",
            access_token="token_123",
        )

        result = client.get_complaint_detail(
            env=0,
            complaint_id="complaint_123",
        )

        assert isinstance(result, Complaint)
        assert result.complaint_id == "complaint_123"

    @responses.activate
    def test_response_complaint(self):
        """Test response to complaint."""
        responses.add(
            responses.POST,
            "https://api.weixin.qq.com/xpay/response_complaint",
            json={"errcode": 0, "errmsg": "ok"},
            status=200,
        )

        client = XPayClient(
            app_id="wx123",
            app_key_sandbox="sandbox_key",
            app_key_production="prod_key",
            access_token="token_123",
        )

        result = client.response_complaint(
            env=0,
            complaint_id="complaint_123",
            response_content="We will process this soon",
        )

        assert result is True
```

**Step 2: Add implementations**

```python
def get_complaint_list(
    self,
    env: int,
    begin_date: str,
    end_date: str,
    offset: int,
    limit: int,
) -> ComplaintList:
    """Get complaint list.

    Requires pay_sig only.

    Args:
        env: 0 for production, 1 for sandbox
        begin_date: Start date (yyyy-mm-dd)
        end_date: End date (yyyy-mm-dd)
        offset: Pagination offset (from 0)
        limit: Max records to return

    Returns:
        ComplaintList dataclass
    """
    uri = "/xpay/get_complaint_list"
    data = {
        "env": env,
        "begin_date": begin_date,
        "end_date": end_date,
        "offset": offset,
        "limit": limit,
    }
    result = self._request(
        "POST", uri, data, env,
        need_pay_sig=True, need_signature=False
    )

    complaints = []
    for c in result.get("complaints", []):
        complaint = Complaint(
            complaint_id=c["complaint_id"],
            complaint_time=c["complaint_time"],
            complaint_detail=c["complaint_detail"],
            complaint_state=c["complaint_state"],
            payer_openid=c["payer_openid"],
            complaint_full_refunded=c.get("complaint_full_refunded", False),
            incoming_user_response=c.get("incoming_user_response", False),
            user_complaint_times=c.get("user_complaint_times", 0),
            problem_description=c.get("problem_description"),
            problem_type=c.get("problem_type"),
            apply_refund_amount=c.get("apply_refund_amount"),
            payer_phone=c.get("payer_phone"),
        )
        # Parse nested objects if present
        if "complaint_order_info" in c:
            complaint.complaint_order_info = [
                ComplaintOrderInfo(
                    transaction_id=coi.get("transaction_id", ""),
                    out_trade_no=coi.get("out_trade_no", ""),
                    amount=coi.get("amount", 0),
                    wxa_out_trade_no=coi.get("wxa_out_trade_no", ""),
                    wx_order_id=coi.get("wx_order_id", ""),
                )
                for coi in c["complaint_order_info"]
            ]
        complaints.append(complaint)

    return ComplaintList(total=result["total"], complaints=complaints)


def get_complaint_detail(
    self,
    env: int,
    complaint_id: str,
) -> Complaint:
    """Get complaint detail.

    Requires pay_sig only.

    Args:
        env: 0 for production, 1 for sandbox
        complaint_id: Complaint ID

    Returns:
        Complaint dataclass
    """
    uri = "/xpay/get_complaint_detail"
    data = {
        "env": env,
        "complaint_id": complaint_id,
    }
    result = self._request(
        "POST", uri, data, env,
        need_pay_sig=True, need_signature=False
    )
    c = result["complaint"]
    return Complaint(
        complaint_id=c["complaint_id"],
        complaint_time=c["complaint_time"],
        complaint_detail=c["complaint_detail"],
        complaint_state=c["complaint_state"],
        payer_openid=c["payer_openid"],
        complaint_full_refunded=c.get("complaint_full_refunded", False),
        incoming_user_response=c.get("incoming_user_response", False),
        user_complaint_times=c.get("user_complaint_times", 0),
        problem_description=c.get("problem_description"),
        problem_type=c.get("problem_type"),
        apply_refund_amount=c.get("apply_refund_amount"),
        payer_phone=c.get("payer_phone"),
    )


def response_complaint(
    self,
    env: int,
    complaint_id: str,
    response_content: str,
    response_images: Optional[list[str]] = None,
) -> bool:
    """Response to complaint.

    Requires pay_sig only.

    Args:
        env: 0 for production, 1 for sandbox
        complaint_id: Complaint ID
        response_content: Response content
        response_images: List of file IDs from upload_vp_file

    Returns:
        True on success
    """
    uri = "/xpay/response_complaint"
    data: dict[str, Any] = {
        "env": env,
        "complaint_id": complaint_id,
        "response_content": response_content,
    }
    if response_images:
        data["response_images"] = response_images

    self._request(
        "POST", uri, data, env,
        need_pay_sig=True, need_signature=False
    )
    return True


def complete_complaint(
    self,
    env: int,
    complaint_id: str,
) -> bool:
    """Complete complaint handling.

    Requires pay_sig only.

    Args:
        env: 0 for production, 1 for sandbox
        complaint_id: Complaint ID

    Returns:
        True on success
    """
    uri = "/xpay/complete_complaint"
    data = {
        "env": env,
        "complaint_id": complaint_id,
    }
    self._request(
        "POST", uri, data, env,
        need_pay_sig=True, need_signature=False
    )
    return True


def upload_vp_file(
    self,
    env: int,
    file_name: str,
    base64_img: Optional[str] = None,
    img_url: Optional[str] = None,
) -> UploadFileResult:
    """Upload media file (image, voucher, etc.).

    Requires pay_sig only.
    Use img_url for files > 1MB (up to 2MB).

    Args:
        env: 0 for production, 1 for sandbox
        file_name: File name
        base64_img: Base64 encoded image (max 1MB)
        img_url: Image URL (max 2MB, preferred)

    Returns:
        UploadFileResult dataclass with file_id
    """
    uri = "/xpay/upload_vp_file"
    data: dict[str, Any] = {
        "env": env,
        "file_name": file_name,
    }
    if base64_img:
        data["base64_img"] = base64_img
    if img_url:
        data["img_url"] = img_url

    result = self._request(
        "POST", uri, data, env,
        need_pay_sig=True, need_signature=False
    )
    return UploadFileResult(file_id=result["file_id"])
```

**Step 3: Run tests and commit**

```bash
pytest tests/test_client.py::TestComplaintAPIs -v
git add wechat_xpay/client.py tests/test_client.py
git commit -m "feat: add complaint management APIs"
```

---

## Task 8: Webhook Message Parser

**Files:**
- Create: `wechat_xpay/webhook.py`
- Create: `tests/test_webhook.py`

Add webhook parser for:
1. `xpay_goods_deliver_notify` - Goods delivery notification
2. `xpay_coin_pay_notify` - Token payment notification
3. `xpay_refund_notify` - Refund notification
4. `xpay_complaint_notify` - Complaint notification

**Step 1: Write failing test**

`tests/test_webhook.py`:
```python
"""Tests for webhook message parser."""
import pytest
from wechat_xpay.webhook import WebhookParser, GoodsDeliverNotify, CoinPayNotify


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
        assert result.quantity == 100
```

**Step 2: Run test to verify it fails**

**Step 3: Write implementation**

`wechat_xpay/webhook.py`:
```python
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
    to_user_name: str
    from_user_name: str
    create_time: int
    msg_type: str
    event: str
    open_id: str
    out_trade_no: str
    env: int
    wechat_pay_info: Optional[WechatPayInfo] = None
    goods_info: Optional[GoodsInfo] = None
    team_info: Optional[TeamInfo] = None


@dataclass
class CoinPayNotify:
    """xpay_coin_pay_notify message."""
    to_user_name: str
    from_user_name: str
    create_time: int
    msg_type: str
    event: str
    open_id: str
    out_trade_no: str
    env: int
    wechat_pay_info: Optional[WechatPayInfo] = None
    coin_info: Optional[CoinInfo] = None


@dataclass
class RefundNotify:
    """xpay_refund_notify message."""
    to_user_name: str
    from_user_name: str
    create_time: int
    msg_type: str
    event: str
    open_id: str
    wx_refund_id: str
    mch_refund_id: str
    wx_order_id: str
    mch_order_id: str
    refund_fee: int
    ret_code: int
    ret_msg: str
    refund_start_timestamp: int
    refund_succ_timestamp: int
    wxpay_refund_transaction_id: str
    retry_times: int
    team_info: Optional[TeamInfo] = None


@dataclass
class ComplaintNotify:
    """xpay_complaint_notify message."""
    to_user_name: str
    from_user_name: str
    create_time: int
    msg_type: str
    event: str
    open_id: str
    wx_order_id: str
    mch_order_id: str
    complaint_time: int
    retry_times: int
    request_id: str


class WebhookParser:
    """Parser for WeChat XPay webhook messages."""

    def parse(self, payload: dict[str, Any] | str) -> GoodsDeliverNotify | CoinPayNotify | RefundNotify | ComplaintNotify:
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

    @staticmethod
    def success_response() -> dict[str, Any]:
        """Generate success response for webhook.

        Returns:
            JSON response dict
        """
        return {"ErrCode": 0, "ErrMsg": "success"}

    @staticmethod
    def success_response_xml() -> str:
        """Generate success response in XML format.

        Returns:
            XML response string
        """
        return "<xml><ErrCode>0</ErrCode><ErrMsg><![CDATA[success]]></ErrMsg></xml>"
```

**Step 4: Run tests and commit**

```bash
pytest tests/test_webhook.py -v
git add wechat_xpay/webhook.py tests/test_webhook.py
git commit -m "feat: add webhook message parser for push notifications"
```

---

## Task 9: Documentation and Examples

**Files:**
- Create: `README.md`
- Create: `examples/basic_usage.py`

**Step 1: Create README**

`README.md`:
```markdown
# WeChat XPay Python SDK

Python SDK for WeChat XPay (Virtual Payment) server-side APIs.

## Installation

```bash
pip install wechat-xpay
```

## Quick Start

```python
from wechat_xpay import XPayClient

# Initialize client
client = XPayClient(
    app_id="your_app_id",
    app_key_sandbox="your_sandbox_key",
    app_key_production="your_production_key",
    access_token="your_access_token",
)

# Query user balance
balance = client.query_user_balance(
    openid="user_openid",
    env=0,  # 0=production, 1=sandbox
    user_ip="1.1.1.1",
    session_key="user_session_key",
)
print(f"Balance: {balance.balance}")
```

## API Coverage

- [x] User Token Management (query_user_balance, currency_pay, cancel_currency_pay, present_currency)
- [x] Order Management (query_order, refund_order, notify_provide_goods)
- [x] Withdrawal (create_withdraw_order, query_withdraw_order)
- [x] Goods Management (start_upload_goods, query_upload_goods, start_publish_goods, query_publish_goods)
- [x] Business Balance (query_biz_balance)
- [x] Advertising Funds (query_transfer_account, query_adver_funds, create_funds_bill, etc.)
- [x] Complaint Management (get_complaint_list, response_complaint, etc.)
- [x] Webhook Parser (goods delivery, coin payment, refund, complaint notifications)

## Documentation

See `docs/plans/` for implementation details.

## License

MIT
```

**Step 2: Create example file**

`examples/basic_usage.py`:
```python
"""Basic usage example for WeChat XPay SDK."""
from wechat_xpay import XPayClient


def main():
    # Initialize client
    client = XPayClient(
        app_id="wx1234567890",
        app_key_sandbox="sandbox_key_here",
        app_key_production="production_key_here",
        access_token="access_token_here",
    )

    # Example: Query user balance
    try:
        balance = client.query_user_balance(
            openid="user_openid_here",
            env=1,  # Sandbox for testing
            user_ip="127.0.0.1",
            session_key="user_session_key_here",
        )
        print(f"User Balance: {balance.balance}")
        print(f"Present Balance: {balance.present_balance}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
```

**Step 3: Commit**

```bash
git add README.md examples/basic_usage.py
git commit -m "docs: add README and usage examples"
```

---

## Task 10: Final Verification

**Step 1: Run all tests**

```bash
pytest tests/ -v --tb=short
```

Expected: All tests pass

**Step 2: Check code coverage (optional)**

```bash
pip install pytest-cov
pytest tests/ --cov=wechat_xpay --cov-report=term-missing
```

**Step 3: Final commit**

```bash
git commit -m "test: add comprehensive test suite" --allow-empty
```

---

## Summary

This implementation plan covers:

1. **Core Client** (`XPayClient`) - HTTP layer, signature handling, error handling
2. **User Token APIs** - Balance query, payment, refund, present
3. **Order APIs** - Query, refund, notify delivery
4. **Withdrawal APIs** - Create and query withdrawal orders
5. **Goods APIs** - Upload and publish goods
6. **Business Balance** - Query withdrawable balance
7. **Advertising Fund APIs** - Account query, fund records, billing
8. **Complaint APIs** - List, detail, response, complete
9. **Webhook Parser** - Parse and handle push notifications
10. **Documentation** - README and usage examples

All APIs follow the same pattern:
- Input validation
- Proper signature calculation (pay_sig and/or signature)
- HTTP POST request
- Response parsing into dataclasses
- Error handling with XPayAPIError
