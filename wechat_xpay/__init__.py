"""WeChat XPay (Virtual Payment) Python SDK."""

from wechat_xpay import models
from wechat_xpay.async_client import XPayAsyncClient
from wechat_xpay.auth import (
    calc_pay_sig,
    calc_signature,
    generate_nonce_str,
    generate_request_signature,
    generate_timestamp,
    verify_webhook_signature,
)
from wechat_xpay.client import XPayClient
from wechat_xpay.exceptions import (
    ERR_ACCOUNT_NOT_COMPLETED,
    ERR_ADVER_FUND_ACCOUNT_BOUND_TO_OTHER_APP,
    ERR_ADVER_FUND_ACCOUNT_INVALID,
    ERR_ADVER_FUND_AMOUNT_MUST_BE_POSITIVE,
    ERR_ADVER_FUND_BALANCE_INSUFFICIENT,
    ERR_ADVER_FUND_INDUSTRY_MISMATCH,
    ERR_ADVER_FUND_ORG_NAME_MISMATCH,
    ERR_BAD_REQUEST_PARAMS,
    ERR_BATCH_TASK_RUNNING,
    ERR_CANNOT_REFUND_VERIFIED_ORDER,
    ERR_DATA_GENERATING,
    ERR_DUPLICATE_OPERATION,
    ERR_INSUFFICIENT_TOKEN_BALANCE,
    ERR_INVALID_OPENID,
    ERR_LEFT_FEE_MISMATCH,
    ERR_ORDER_ALREADY_REFUNDED,
    ERR_RATE_LIMIT_EXCEEDED,
    ERR_REFUND_IN_PROGRESS,
    ERR_SENSITIVE_CONTENT,
    ERR_SESSION_KEY_EXPIRED,
    ERR_SIGNATURE_ERROR,
    ERR_SYSTEM_ERROR,
    ERR_TOKEN_NOT_PUBLISHED,
    XPayAPIError,
    XPayError,
)

__all__ = [
    # Client
    "XPayClient",
    "XPayAsyncClient",
    # Auth
    "calc_pay_sig",
    "calc_signature",
    "generate_request_signature",
    "verify_webhook_signature",
    "generate_timestamp",
    "generate_nonce_str",
    # Exceptions
    "XPayError",
    "XPayAPIError",
    # Error Codes - aligned with apis.txt documentation
    "ERR_SYSTEM_ERROR",
    "ERR_INVALID_OPENID",
    "ERR_BAD_REQUEST_PARAMS",
    "ERR_SIGNATURE_ERROR",
    "ERR_DUPLICATE_OPERATION",
    "ERR_ORDER_ALREADY_REFUNDED",
    "ERR_INSUFFICIENT_TOKEN_BALANCE",
    "ERR_SENSITIVE_CONTENT",
    "ERR_TOKEN_NOT_PUBLISHED",
    "ERR_SESSION_KEY_EXPIRED",
    "ERR_DATA_GENERATING",
    "ERR_BATCH_TASK_RUNNING",
    "ERR_CANNOT_REFUND_VERIFIED_ORDER",
    "ERR_REFUND_IN_PROGRESS",
    "ERR_RATE_LIMIT_EXCEEDED",
    "ERR_LEFT_FEE_MISMATCH",
    "ERR_ADVER_FUND_INDUSTRY_MISMATCH",
    "ERR_ADVER_FUND_ACCOUNT_BOUND_TO_OTHER_APP",
    "ERR_ADVER_FUND_ORG_NAME_MISMATCH",
    "ERR_ACCOUNT_NOT_COMPLETED",
    "ERR_ADVER_FUND_ACCOUNT_INVALID",
    "ERR_ADVER_FUND_BALANCE_INSUFFICIENT",
    "ERR_ADVER_FUND_AMOUNT_MUST_BE_POSITIVE",
    # Models
    "models",
]
