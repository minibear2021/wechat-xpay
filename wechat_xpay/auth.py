"""
Signature computation for WeChat XPay server API.

Two independent HMAC-SHA256 signatures:
  pay_sig   - keyed by appKey,     message = uri + '&' + post_body
  signature - keyed by session_key, message = post_body
"""

import hashlib
import hmac


def calc_pay_sig(uri, post_body, appkey):
    """pay_sig签名算法
     Args:
    uri - 当前请求的API的uri部分，不带query_string 例如：/xpay/query_user_balance
         post_body - http POST的数据包体
         appkey    - 对应环境的AppKey
     Returns:
         支付请求签名pay_sig
    """
    need_sign_msg = uri + "&" + post_body
    pay_sig = hmac.new(
        key=appkey.encode("utf-8"), msg=need_sign_msg.encode("utf-8"), digestmod=hashlib.sha256
    ).hexdigest()
    return pay_sig


def calc_signature(post_body, session_key):
    """用户登录态signature签名算法
    Args:
        post_body   - http POST的数据包体
        session_key - 当前用户有效的session_key，参考auth.code2Session接口
    Returns:
        用户登录态签名signature
    """
    need_sign_msg = post_body
    signature = hmac.new(
        key=session_key.encode("utf-8"), msg=need_sign_msg.encode("utf-8"), digestmod=hashlib.sha256
    ).hexdigest()
    return signature


def generate_request_signature(
    uri: str,
    payload: dict,
    app_key: str,
    session_key: str,
) -> tuple[str, str]:
    """Generate both signatures for a request.

    This is a convenience function that generates both pay_sig and
    signature for a complete request payload.

    Args:
        uri:          API endpoint path (e.g., '/xpay/query_user_balance')
        payload:      Request body as a dictionary
        app_key:      AppKey for pay_sig calculation
        session_key:  User's session_key for signature calculation

    Returns:
        Tuple of (pay_sig, signature)
    """
    import json

    body_str = json.dumps(payload, ensure_ascii=False)
    pay_sig = calc_pay_sig(uri, body_str, app_key)
    signature = calc_signature(body_str, session_key)
    return pay_sig, signature


def verify_webhook_signature(
    body: str,
    signature: str,
    session_key: str,
) -> bool:
    """Verify webhook callback signature.

    Args:
        body:          Raw request body string
        signature:     Signature from X-Signature header
        session_key:   User's session_key used to sign the request

    Returns:
        True if signature is valid, False otherwise
    """
    expected = calc_signature(body, session_key)
    return hmac.compare_digest(expected, signature)


def generate_timestamp() -> int:
    """Generate current Unix timestamp in seconds.

    Returns:
        Current Unix timestamp
    """
    import time

    return int(time.time())


def generate_nonce_str(length: int = 32) -> str:
    """Generate a random nonce string.

    Args:
        length: Length of the nonce string (default: 32)

    Returns:
        Random alphanumeric string
    """
    import secrets

    return secrets.token_hex(length // 2)
