"""Custom exceptions for the WeChat XPay SDK."""

# Error code constants - aligned with apis.txt documentation
ERR_SYSTEM_ERROR = -1
ERR_INVALID_OPENID = 268490001
ERR_BAD_REQUEST_PARAMS = 268490002
ERR_SIGNATURE_ERROR = 268490003
ERR_DUPLICATE_OPERATION = 268490004
ERR_ORDER_ALREADY_REFUNDED = 268490005
ERR_INSUFFICIENT_TOKEN_BALANCE = 268490006
ERR_SENSITIVE_CONTENT = 268490007
ERR_TOKEN_NOT_PUBLISHED = 268490008
ERR_SESSION_KEY_EXPIRED = 268490009
ERR_DATA_GENERATING = 268490011
ERR_BATCH_TASK_RUNNING = 268490012
ERR_CANNOT_REFUND_VERIFIED_ORDER = 268490013
ERR_REFUND_IN_PROGRESS = 268490014
ERR_RATE_LIMIT_EXCEEDED = 268490015
ERR_LEFT_FEE_MISMATCH = 268490016
ERR_ADVER_FUND_INDUSTRY_MISMATCH = 268490018
ERR_ADVER_FUND_ACCOUNT_BOUND_TO_OTHER_APP = 268490019
ERR_ADVER_FUND_ORG_NAME_MISMATCH = 268490020
ERR_ACCOUNT_NOT_COMPLETED = 268490021
ERR_ADVER_FUND_ACCOUNT_INVALID = 268490022
ERR_ADVER_FUND_BALANCE_INSUFFICIENT = 268490023
ERR_ADVER_FUND_AMOUNT_MUST_BE_POSITIVE = 268490024


class XPayError(Exception):
    """Base exception for all SDK errors."""


class XPayAPIError(XPayError):
    """Raised when the WeChat XPay API returns a non-zero errcode.

    Attributes:
        errcode: WeChat error code integer.
        errmsg:  Human-readable error message from the API.

    Common error codes:
        -1 (ERR_SYSTEM_ERROR)
            系统错误
        268490001 (ERR_INVALID_OPENID)
            openid 错误
        268490002 (ERR_BAD_REQUEST_PARAMS)
            请求参数字段错误，具体看 errmsg
        268490003 (ERR_SIGNATURE_ERROR)
            签名错误
        268490004 (ERR_DUPLICATE_OPERATION)
            重复操作（赠送和代币支付和充值广告金相关接口会返回，表示之前的操作已经成功）
        268490005 (ERR_ORDER_ALREADY_REFUNDED)
            订单已经通过 cancel_currency_pay 接口退款，不支持再退款
        268490006 (ERR_INSUFFICIENT_TOKEN_BALANCE)
            代币的退款/支付操作金额不足
        268490007 (ERR_SENSITIVE_CONTENT)
            图片或文字存在敏感内容，禁止使用
        268490008 (ERR_TOKEN_NOT_PUBLISHED)
            代币未发布，不允许进行代币操作
        268490009 (ERR_SESSION_KEY_EXPIRED)
            用户 session_key 不存在或已过期，请重新登录
        268490011 (ERR_DATA_GENERATING)
            数据生成中，请稍后调用本接口获取
        268490012 (ERR_BATCH_TASK_RUNNING)
            批量任务运行中，请等待完成后才能再次运行
        268490013 (ERR_CANNOT_REFUND_VERIFIED_ORDER)
            禁止对核销状态的单进行退款
        268490014 (ERR_REFUND_IN_PROGRESS)
            退款操作进行中，稍后可以使用相同参数重试
        268490015 (ERR_RATE_LIMIT_EXCEEDED)
            频率限制
        268490016 (ERR_LEFT_FEE_MISMATCH)
            退款的 left_fee 字段与实际不符，请通过 query_order 接口查询确认
        268490018 (ERR_ADVER_FUND_INDUSTRY_MISMATCH)
            广告金充值帐户行业 id 不匹配
        268490019 (ERR_ADVER_FUND_ACCOUNT_BOUND_TO_OTHER_APP)
            广告金充值帐户 id 已绑定其他 appid
        268490020 (ERR_ADVER_FUND_ORG_NAME_MISMATCH)
            广告金充值帐户主体名称错误
        268490021 (ERR_ACCOUNT_NOT_COMPLETED)
            账户未完成进件
        268490022 (ERR_ADVER_FUND_ACCOUNT_INVALID)
            广告金充值账户无效
        268490023 (ERR_ADVER_FUND_BALANCE_INSUFFICIENT)
            广告金余额不足
        268490024 (ERR_ADVER_FUND_AMOUNT_MUST_BE_POSITIVE)
            广告金充值金额必须大于 0
    """

    def __init__(self, errcode: int, errmsg: str) -> None:
        self.errcode = errcode
        self.errmsg = errmsg
        super().__init__(f"XPay API error {errcode}: {errmsg}")
