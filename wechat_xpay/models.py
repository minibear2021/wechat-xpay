"""Dataclasses for WeChat XPay API response objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# query_user_balance
# ---------------------------------------------------------------------------


@dataclass
class UserBalance:
    balance: int
    present_balance: int
    sum_save: int
    sum_present: int
    sum_balance: int
    sum_cost: int
    first_save_flag: bool


# ---------------------------------------------------------------------------
# currency_pay
# ---------------------------------------------------------------------------


@dataclass
class CurrencyPayResult:
    order_id: str
    balance: int
    used_present_amount: int


# ---------------------------------------------------------------------------
# query_order — nested Order object
# ---------------------------------------------------------------------------


@dataclass
class Order:
    order_id: str
    create_time: int
    update_time: int
    status: int
    biz_type: int
    order_fee: int
    paid_fee: int
    order_type: int
    env_type: int
    coupon_fee: Optional[int] = None
    refund_fee: Optional[int] = None
    paid_time: Optional[int] = None
    provide_time: Optional[int] = None
    biz_meta: Optional[str] = None
    token: Optional[str] = None
    left_fee: Optional[int] = None
    wx_order_id: Optional[str] = None
    channel_order_id: Optional[str] = None
    wxpay_order_id: Optional[str] = None
    sett_time: Optional[int] = None
    sett_state: Optional[int] = None
    platform_fee_fen: Optional[int] = None
    cps_fee_fen: Optional[int] = None


# ---------------------------------------------------------------------------
# cancel_currency_pay
# ---------------------------------------------------------------------------


@dataclass
class CancelCurrencyPayResult:
    order_id: str


# ---------------------------------------------------------------------------
# present_currency
# ---------------------------------------------------------------------------


@dataclass
class PresentCurrencyResult:
    balance: int
    order_id: str
    present_balance: int


# ---------------------------------------------------------------------------
# download_bill / download_adverfunds_order
# ---------------------------------------------------------------------------


@dataclass
class BillDownload:
    url: str


# ---------------------------------------------------------------------------
# refund_order
# ---------------------------------------------------------------------------


@dataclass
class RefundOrderResult:
    refund_order_id: str
    refund_wx_order_id: str
    pay_order_id: str
    pay_wx_order_id: str


# ---------------------------------------------------------------------------
# create_withdraw_order
# ---------------------------------------------------------------------------


@dataclass
class WithdrawOrderResult:
    withdraw_no: str
    wx_withdraw_no: str


# ---------------------------------------------------------------------------
# query_withdraw_order
# ---------------------------------------------------------------------------


@dataclass
class WithdrawOrder:
    withdraw_no: str
    status: int
    withdraw_amount: str
    wx_withdraw_no: str
    withdraw_success_timestamp: Optional[str] = None
    create_time: Optional[str] = None
    fail_reason: Optional[str] = None


# ---------------------------------------------------------------------------
# start_upload_goods / query_upload_goods
# ---------------------------------------------------------------------------


@dataclass
class GoodsUploadItem:
    id: str
    name: str
    price: int
    remark: str
    item_url: str
    upload_status: Optional[int] = None
    errmsg: Optional[str] = None


@dataclass
class GoodsUploadStatus:
    status: int
    upload_item: List[GoodsUploadItem] = field(default_factory=list)


# ---------------------------------------------------------------------------
# start_publish_goods / query_publish_goods
# ---------------------------------------------------------------------------


@dataclass
class GoodsPublishItem:
    id: str
    publish_status: Optional[int] = None
    errmsg: Optional[str] = None


@dataclass
class GoodsPublishStatus:
    status: int
    publish_item: List[GoodsPublishItem] = field(default_factory=list)


# ---------------------------------------------------------------------------
# query_biz_balance
# ---------------------------------------------------------------------------


@dataclass
class BizBalanceAvailable:
    amount: str
    currency_code: str


@dataclass
class BizBalance:
    balance_available: BizBalanceAvailable


# ---------------------------------------------------------------------------
# query_transfer_account
# ---------------------------------------------------------------------------


@dataclass
class TransferAccount:
    transfer_account_name: str
    transfer_account_uid: int
    transfer_account_agency_id: int
    transfer_account_agency_name: str
    state: int
    bind_result: int
    error_msg: Optional[str] = None


# ---------------------------------------------------------------------------
# query_adver_funds
# ---------------------------------------------------------------------------


@dataclass
class AdverFund:
    settle_begin: int
    settle_end: int
    total_amount: int
    remain_amount: int
    expire_time: int
    fund_type: int
    fund_id: str


@dataclass
class AdverFundList:
    adver_funds_list: List[AdverFund]
    total_page: int


# ---------------------------------------------------------------------------
# create_funds_bill
# ---------------------------------------------------------------------------


@dataclass
class FundsBillResult:
    bill_id: str


# ---------------------------------------------------------------------------
# query_funds_bill
# ---------------------------------------------------------------------------


@dataclass
class FundsBillItem:
    bill_id: str
    oper_time: int
    settle_begin: int
    settle_end: int
    fund_id: str
    transfer_account_name: str
    transfer_account_uid: int
    transfer_amount: int
    status: int
    request_id: str


@dataclass
class FundsBillList:
    bill_list: List[FundsBillItem]
    total_page: int


# ---------------------------------------------------------------------------
# query_recover_bill
# ---------------------------------------------------------------------------


@dataclass
class RecoverBillItem:
    bill_id: str
    recover_time: int
    settle_begin: int
    settle_end: int
    fund_id: str
    recover_account_name: str
    recover_amount: int
    refund_order_list: List[str] = field(default_factory=list)


@dataclass
class RecoverBillList:
    bill_list: List[RecoverBillItem]
    total_page: int


# ---------------------------------------------------------------------------
# get_complaint_list / get_complaint_detail
# ---------------------------------------------------------------------------


@dataclass
class ComplaintOrderInfo:
    transaction_id: str
    out_trade_no: str
    amount: int
    wxa_out_trade_no: str
    wx_order_id: str


@dataclass
class ComplaintMedia:
    media_type: str
    media_url: List[str] = field(default_factory=list)


@dataclass
class ServiceOrderInfo:
    order_id: str
    out_order_no: str
    state: str


@dataclass
class Complaint:
    complaint_id: str
    complaint_time: str
    complaint_detail: str
    complaint_state: str
    payer_openid: str
    complaint_order_info: List[ComplaintOrderInfo] = field(default_factory=list)
    complaint_full_refunded: bool = False
    incoming_user_response: bool = False
    user_complaint_times: int = 0
    complaint_media_list: List[ComplaintMedia] = field(default_factory=list)
    problem_description: Optional[str] = None
    problem_type: Optional[str] = None
    apply_refund_amount: Optional[int] = None
    user_tag_list: List[str] = field(default_factory=list)
    service_order_info: List[ServiceOrderInfo] = field(default_factory=list)
    payer_phone: Optional[str] = None


@dataclass
class ComplaintList:
    total: int
    complaints: List[Complaint]


# ---------------------------------------------------------------------------
# get_negotiation_history
# ---------------------------------------------------------------------------


@dataclass
class NegotiationRecord:
    log_id: str
    operator: str
    operate_time: str
    operate_type: str
    operate_details: str
    complaint_media_list: List[ComplaintMedia] = field(default_factory=list)


@dataclass
class NegotiationHistory:
    total: int
    history: List[NegotiationRecord]


# ---------------------------------------------------------------------------
# upload_vp_file / get_upload_file_sign
# ---------------------------------------------------------------------------


@dataclass
class UploadFileResult:
    file_id: str


@dataclass
class UploadFileSign:
    sign: str
    cos_url: Optional[str] = None


# ---------------------------------------------------------------------------
# notify_provide_goods
# ---------------------------------------------------------------------------


@dataclass
class NotifyProvideGoodsResult:
    order_id: str
    out_trade_no: str
    provide_status: int


# ---------------------------------------------------------------------------
# download_adverfunds_order
# ---------------------------------------------------------------------------


@dataclass
class AdverfundsOrderDownload:
    url: str
