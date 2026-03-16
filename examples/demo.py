"""WeChat XPay (Virtual Payment) SDK Flask Demo

参考微信支付的示例代码风格，演示如何使用 wechat-xpay SDK 处理
小游戏虚拟支付的相关业务。
"""
import logging
import os
import time
import uuid
from random import sample
from string import ascii_letters, digits

from flask import Flask, Response, jsonify, request

from wechat_xpay import XPayClient, XPayError
from wechat_xpay.webhook import (
    CoinPayNotify,
    ComplaintNotify,
    GoodsDeliverNotify,
    RefundNotify,
    WebhookParser,
)

# ============================================================================
# 配置区域 - 请根据实际环境修改以下配置
# ============================================================================

# 小程序 AppID
APPID = "wxaa1f951f4433be7b"

# 小程序 AppKey（用于计算 pay_sig）
APP_KEY = "your_app_key_here"

# 环境配置：0=正式环境，1=沙箱环境
ENV = 1

# 回调地址配置
NOTIFY_URL = "https://www.xxxx.com/notify"

# 日志记录器，记录 API 请求和回调细节
logging.basicConfig(
    filename=os.path.join(os.getcwd(), "xpay_demo.log"),
    level=logging.DEBUG,
    filemode="a",
    format="%(asctime)s - %(process)s - %(levelname)s: %(message)s",
)
LOGGER = logging.getLogger("xpay_demo")

# 代理设置，None 或者 {"https": "http://10.10.1.10:1080"}
PROXY = None

# 请求超时时间配置（秒）
TIMEOUT = 30

# 初始化 XPay 客户端
xpay = XPayClient(
    app_id=APPID,
    app_key=APP_KEY,
    env=ENV,
    logger=LOGGER,
)

# 初始化 Webhook 解析器
webhook_parser = WebhookParser()

app = Flask(__name__)


# ============================================================================
# 用户代币相关接口
# ============================================================================


@app.route("/balance/<openid>")
def get_user_balance(openid):
    """查询用户代币余额。

    Args:
        openid: 用户的 OpenID

    Returns:
        用户余额信息，包括余额、赠送余额、累计充值等
    """
    # 实际项目中需要从会话或数据库获取 session_key
    session_key = request.args.get("session_key", "")
    access_token = request.args.get("access_token", "")
    user_ip = request.remote_addr

    try:
        balance = xpay.query_user_balance(
            openid=openid,
            access_token=access_token,
            session_key=session_key,
            user_ip=user_ip,
        )
        return jsonify(
            {
                "code": 0,
                "message": "success",
                "data": {
                    "balance": balance.balance,
                    "present_balance": balance.present_balance,
                    "sum_save": balance.sum_save,
                    "sum_present": balance.sum_present,
                    "sum_cost": balance.sum_cost,
                    "first_save_flag": balance.first_save_flag,
                },
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


@app.route("/pay", methods=["POST"])
def currency_pay():
    """代币支付接口。

    扣除用户代币，用于购买游戏内道具或服务。
    请求体示例：
    {
        "openid": "用户openid",
        "session_key": "用户session_key",
        "amount": 100,
        "payitem": "道具信息"
    }
    """
    data = request.get_json()
    openid = data.get("openid")
    session_key = data.get("session_key")
    access_token = data.get("access_token", "")
    amount = data.get("amount", 0)
    payitem = data.get("payitem", "")
    user_ip = request.remote_addr

    # 生成唯一订单号
    order_id = f"ORDER{int(time.time())}{''.join(sample(ascii_letters + digits, 6))}"

    try:
        result = xpay.currency_pay(
            openid=openid,
            access_token=access_token,
            session_key=session_key,
            order_id=order_id,
            amount=amount,
            payitem=payitem,
            user_ip=user_ip,
        )
        return jsonify(
            {
                "code": 0,
                "message": "支付成功",
                "data": {
                    "order_id": result.order_id,
                    "balance": result.balance,
                    "used_present_amount": result.used_present_amount,
                },
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


@app.route("/refund", methods=["POST"])
def cancel_currency_pay():
    """代币支付退款接口。

    对已经完成的代币支付进行退款，将代币返还给用户。
    请求体示例：
    {
        "openid": "用户openid",
        "session_key": "用户session_key",
        "pay_order_id": "原支付订单号",
        "amount": 100
    }
    """
    data = request.get_json()
    openid = data.get("openid")
    session_key = data.get("session_key")
    pay_order_id = data.get("pay_order_id")
    amount = data.get("amount", 0)
    access_token = data.get("access_token", "")
    user_ip = request.remote_addr

    # 生成退款订单号
    order_id = f"REFUND{int(time.time())}{''.join(sample(ascii_letters + digits, 6))}"

    try:
        result = xpay.cancel_currency_pay(
            openid=openid,
            access_token=access_token,
            session_key=session_key,
            pay_order_id=pay_order_id,
            order_id=order_id,
            amount=amount,
            user_ip=user_ip,
        )
        return jsonify(
            {
                "code": 0,
                "message": "退款成功",
                "data": {
                    "refund_order_id": result.order_id,
                },
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


@app.route("/present", methods=["POST"])
def present_currency():
    """赠送代币接口。

    向用户赠送代币（游戏运营活动使用）。
    请求体示例：
    {
        "openid": "用户openid",
        "session_key": "用户session_key",
        "amount": 100
    }
    """
    data = request.get_json()
    openid = data.get("openid")
    session_key = data.get("session_key")
    amount = data.get("amount", 0)

    # 生成赠送订单号
    order_id = f"PRESENT{int(time.time())}{''.join(sample(ascii_letters + digits, 6))}"

    try:
        access_token = data.get("access_token", "")

        result = xpay.present_currency(
            openid=openid,
            access_token=access_token,
            session_key=session_key,
            order_id=order_id,
            amount=amount,
        )
        return jsonify(
            {
                "code": 0,
                "message": "赠送成功",
                "data": {
                    "order_id": result.order_id,
                    "balance": result.balance,
                    "present_balance": result.present_balance,
                },
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


# ============================================================================
# 订单管理接口
# ============================================================================


@app.route("/order/<order_id>")
def query_order(order_id):
    """查询订单详情。

    Args:
        order_id: 订单号

    Returns:
        订单详细信息，包括状态、金额、支付时间等
    """
    openid = request.args.get("openid")
    session_key = request.args.get("session_key")
    access_token = request.args.get("access_token", "")

    try:
        order = xpay.query_order(
            openid=openid,
            access_token=access_token,
            session_key=session_key,
            order_id=order_id,
        )
        return jsonify(
            {
                "code": 0,
                "message": "success",
                "data": {
                    "order_id": order.order_id,
                    "status": order.status,
                    "order_fee": order.order_fee,
                    "paid_fee": order.paid_fee,
                    "create_time": order.create_time,
                    "paid_time": order.paid_time,
                    "provide_time": order.provide_time,
                    "wxpay_order_id": order.wxpay_order_id,
                },
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


@app.route("/refund_cash", methods=["POST"])
def refund_order():
    """现金订单退款接口。

    对现金支付订单进行退款。
    请求体示例：
    {
        "openid": "用户openid",
        "session_key": "用户session_key",
        "order_id": "原订单号",
        "left_fee": 1000,
        "refund_fee": 500,
        "refund_reason": "用户申请退款",
        "req_from": 1
    }
    """
    data = request.get_json()
    openid = data.get("openid")
    session_key = data.get("session_key")
    access_token = data.get("access_token", "")
    order_id = data.get("order_id")
    left_fee = data.get("left_fee", 0)
    refund_fee = data.get("refund_fee", 0)
    refund_reason = data.get("refund_reason", "")
    req_from = data.get("req_from", 1)

    # 生成退款订单号
    refund_order_id = f"REF{int(time.time())}{''.join(sample(ascii_letters + digits, 6))}"

    try:
        result = xpay.refund_order(
            openid=openid,
            access_token=access_token,
            session_key=session_key,
            refund_order_id=refund_order_id,
            left_fee=left_fee,
            refund_fee=refund_fee,
            refund_reason=refund_reason,
            req_from=req_from,
            order_id=order_id,
        )
        return jsonify(
            {
                "code": 0,
                "message": "退款申请已提交",
                "data": {
                    "refund_order_id": result.refund_order_id,
                    "refund_wx_order_id": result.refund_wx_order_id,
                },
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


# ============================================================================
# 道具管理接口
# ============================================================================


@app.route("/goods/upload", methods=["POST"])
def start_upload_goods():
    """启动道具上传。

    将游戏道具信息上传到微信服务器。
    请求体示例：
    {
        "session_key": "用户session_key",
        "upload_item": [
            {
                "id": "item_001",
                "name": "金币",
                "price": 100,
                "remark": "100个金币",
                "item_url": "https://example.com/icon.png"
            }
        ]
    }
    """
    data = request.get_json()
    session_key = data.get("session_key")
    access_token = data.get("access_token", "")
    upload_item = data.get("upload_item", [])

    try:
        xpay.start_upload_goods(
            access_token=access_token,
            session_key=session_key,
            upload_item=upload_item,
        )
        return jsonify(
            {
                "code": 0,
                "message": "道具上传任务已启动",
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


@app.route("/goods/publish", methods=["POST"])
def start_publish_goods():
    """启动道具发布。

    将已上传的道具发布到线上。
    请求体示例：
    {
        "session_key": "用户session_key",
        "publish_item": [
            {"id": "item_001"},
            {"id": "item_002"}
        ]
    }
    """
    data = request.get_json()
    session_key = data.get("session_key")
    publish_item = data.get("publish_item", [])

    access_token = data.get("access_token", "")

    try:
        xpay.start_publish_goods(
            access_token=access_token,
            session_key=session_key,
            publish_item=publish_item,
        )
        return jsonify(
            {
                "code": 0,
                "message": "道具发布任务已启动",
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


@app.route("/goods/upload_status")
def query_upload_goods():
    """查询道具上传状态。"""
    session_key = request.args.get("session_key")

    access_token = request.args.get("access_token", "")

    try:
        status = xpay.query_upload_goods(
            access_token=access_token,
            session_key=session_key,
        )
        return jsonify(
            {
                "code": 0,
                "message": "success",
                "data": {
                    "status": status.status,
                    "upload_item": [
                        {
                            "id": item.id,
                            "name": item.name,
                            "upload_status": item.upload_status,
                            "errmsg": item.errmsg,
                        }
                        for item in status.upload_item
                    ],
                },
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


@app.route("/goods/publish_status")
def query_publish_goods():
    """查询道具发布状态。"""
    session_key = request.args.get("session_key")

    access_token = request.args.get("access_token", "")

    try:
        status = xpay.query_publish_goods(
            access_token=access_token,
            session_key=session_key,
        )
        return jsonify(
            {
                "code": 0,
                "message": "success",
                "data": {
                    "status": status.status,
                    "publish_item": [
                        {
                            "id": item.id,
                            "publish_status": item.publish_status,
                            "errmsg": item.errmsg,
                        }
                        for item in status.publish_item
                    ],
                },
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


# ============================================================================
# 商户提现接口
# ============================================================================


@app.route("/biz_balance")
def query_biz_balance():
    """查询商户可提现余额。"""
    session_key = request.args.get("session_key")

    access_token = request.args.get("access_token", "")

    try:
        balance = xpay.query_biz_balance(
            access_token=access_token,
            session_key=session_key,
        )
        return jsonify(
            {
                "code": 0,
                "message": "success",
                "data": {
                    "amount": balance.balance_available.amount,
                    "currency_code": balance.balance_available.currency_code,
                },
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


@app.route("/withdraw", methods=["POST"])
def create_withdraw_order():
    """创建提现订单。

    请求体示例：
    {
        "session_key": "用户session_key",
        "withdraw_amount": "10000"
    }
    """
    data = request.get_json()
    session_key = data.get("session_key")
    access_token = data.get("access_token", "")
    withdraw_amount = data.get("withdraw_amount")

    # 生成提现单号
    withdraw_no = f"WD{int(time.time())}{''.join(sample(ascii_letters + digits, 6))}"

    try:
        result = xpay.create_withdraw_order(
            access_token=access_token,
            session_key=session_key,
            withdraw_no=withdraw_no,
            withdraw_amount=withdraw_amount,
        )
        return jsonify(
            {
                "code": 0,
                "message": "提现申请已提交",
                "data": {
                    "withdraw_no": result.withdraw_no,
                    "wx_withdraw_no": result.wx_withdraw_no,
                },
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


@app.route("/withdraw/<withdraw_no>")
def query_withdraw_order(withdraw_no):
    """查询提现订单状态。

    Args:
        withdraw_no: 提现单号
    """
    session_key = request.args.get("session_key")

    access_token = request.args.get("access_token", "")

    try:
        order = xpay.query_withdraw_order(
            access_token=access_token,
            session_key=session_key,
            withdraw_no=withdraw_no,
        )
        return jsonify(
            {
                "code": 0,
                "message": "success",
                "data": {
                    "withdraw_no": order.withdraw_no,
                    "status": order.status,
                    "withdraw_amount": order.withdraw_amount,
                    "wx_withdraw_no": order.wx_withdraw_no,
                    "withdraw_success_timestamp": order.withdraw_success_timestamp,
                    "fail_reason": order.fail_reason,
                },
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


# ============================================================================
# 广告金相关接口
# ============================================================================


@app.route("/adver_funds")
def query_adver_funds():
    """查询广告金发放记录。"""
    session_key = request.args.get("session_key")
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 10, type=int)
    settle_begin = request.args.get("settle_begin", 0, type=int)
    settle_end = request.args.get("settle_end", 0, type=int)
    fund_type = request.args.get("fund_type", type=int)

    access_token = request.args.get("access_token", "")

    try:
        result = xpay.query_adver_funds(
            access_token=access_token,
            session_key=session_key,
            page=page,
            page_size=page_size,
            settle_begin=settle_begin,
            settle_end=settle_end,
            fund_type=fund_type,
        )
        return jsonify(
            {
                "code": 0,
                "message": "success",
                "data": {
                    "total_page": result.total_page,
                    "adver_funds_list": [
                        {
                            "fund_id": fund.fund_id,
                            "settle_begin": fund.settle_begin,
                            "settle_end": fund.settle_end,
                            "total_amount": fund.total_amount,
                            "remain_amount": fund.remain_amount,
                            "expire_time": fund.expire_time,
                            "fund_type": fund.fund_type,
                        }
                        for fund in result.adver_funds_list
                    ],
                },
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


@app.route("/adver_funds/recharge", methods=["POST"])
def create_funds_bill():
    """充值广告金。

    请求体示例：
    {
        "session_key": "用户session_key",
        "transfer_amount": 100000,
        "transfer_account_uid": 123456,
        "transfer_account_name": "充值账户名称",
        "transfer_account_agency_id": 789012,
        "settle_begin": 1700000000,
        "settle_end": 1702678400,
        "authorize_advertise": 1,
        "fund_type": 0
    }
    """
    data = request.get_json()
    session_key = data.get("session_key")
    transfer_amount = data.get("transfer_amount", 0)
    transfer_account_uid = data.get("transfer_account_uid", 0)
    transfer_account_name = data.get("transfer_account_name", "")
    transfer_account_agency_id = data.get("transfer_account_agency_id", 0)
    settle_begin = data.get("settle_begin", 0)
    settle_end = data.get("settle_end", 0)
    authorize_advertise = data.get("authorize_advertise", 0)
    fund_type = data.get("fund_type", 0)

    # 生成唯一请求 ID
    request_id = str(uuid.uuid4())

    access_token = data.get("access_token", "")

    try:
        result = xpay.create_funds_bill(
            access_token=access_token,
            session_key=session_key,
            transfer_amount=transfer_amount,
            transfer_account_uid=transfer_account_uid,
            transfer_account_name=transfer_account_name,
            transfer_account_agency_id=transfer_account_agency_id,
            settle_begin=settle_begin,
            settle_end=settle_end,
            authorize_advertise=authorize_advertise,
            fund_type=fund_type,
            request_id=request_id,
        )
        return jsonify(
            {
                "code": 0,
                "message": "充值申请已提交",
                "data": {
                    "bill_id": result.bill_id,
                },
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


@app.route("/adver_funds/bind_account", methods=["POST"])
def bind_transfer_account():
    """绑定广告金充值账户。

    请求体示例：
    {
        "session_key": "用户session_key",
        "transfer_account_uid": 123456,
        "transfer_account_org_name": "账户主体名称"
    }
    """
    data = request.get_json()
    session_key = data.get("session_key")
    transfer_account_uid = data.get("transfer_account_uid", 0)
    transfer_account_org_name = data.get("transfer_account_org_name", "")

    access_token = data.get("access_token", "")

    try:
        xpay.bind_transfer_account(
            access_token=access_token,
            session_key=session_key,
            transfer_account_uid=transfer_account_uid,
            transfer_account_org_name=transfer_account_org_name,
        )
        return jsonify(
            {
                "code": 0,
                "message": "账户绑定成功",
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


# ============================================================================
# 投诉处理接口
# ============================================================================


@app.route("/complaints")
def get_complaint_list():
    """查询投诉列表。

    Query Parameters:
        session_key: 用户 session_key
        begin_date: 开始日期，格式 YYYY-MM-DD
        end_date: 结束日期，格式 YYYY-MM-DD
        offset: 偏移量，默认 0
        limit: 每页数量，默认 10
    """
    session_key = request.args.get("session_key")
    access_token = request.args.get("access_token", "")
    begin_date = request.args.get("begin_date")
    end_date = request.args.get("end_date")
    offset = request.args.get("offset", 0, type=int)
    limit = request.args.get("limit", 10, type=int)

    try:
        result = xpay.get_complaint_list(
            access_token=access_token,
            session_key=session_key,
            begin_date=begin_date,
            end_date=end_date,
            offset=offset,
            limit=limit,
        )
        return jsonify(
            {
                "code": 0,
                "message": "success",
                "data": {
                    "total": result.total,
                    "complaints": [
                        {
                            "complaint_id": c.complaint_id,
                            "complaint_time": c.complaint_time,
                            "complaint_state": c.complaint_state,
                            "complaint_detail": c.complaint_detail,
                            "payer_openid": c.payer_openid,
                        }
                        for c in result.complaints
                    ],
                },
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


@app.route("/complaints/<complaint_id>")
def get_complaint_detail(complaint_id):
    """查询投诉详情。

    Args:
        complaint_id: 投诉单号
    """
    access_token = request.args.get("access_token", "")
    session_key = request.args.get("session_key")

    try:
        complaint = xpay.get_complaint_detail(
            access_token=access_token,
            session_key=session_key,
            complaint_id=complaint_id,
        )
        return jsonify(
            {
                "code": 0,
                "message": "success",
                "data": {
                    "complaint_id": complaint.complaint_id,
                    "complaint_time": complaint.complaint_time,
                    "complaint_state": complaint.complaint_state,
                    "complaint_detail": complaint.complaint_detail,
                    "payer_openid": complaint.payer_openid,
                    "problem_description": complaint.problem_description,
                    "apply_refund_amount": complaint.apply_refund_amount,
                },
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


@app.route("/complaints/<complaint_id>/response", methods=["POST"])
def response_complaint(complaint_id):
    """回复投诉。

    Args:
        complaint_id: 投诉单号

    请求体示例：
    {
        "session_key": "用户session_key",
        "response_content": "感谢您的反馈，我们已经处理...",
        "response_images": ["media_id_1", "media_id_2"]
    }
    """
    data = request.get_json()
    session_key = data.get("session_key")
    response_content = data.get("response_content", "")
    response_images = data.get("response_images", [])

    access_token = data.get("access_token", "")

    try:
        xpay.response_complaint(
            access_token=access_token,
            session_key=session_key,
            complaint_id=complaint_id,
            response_content=response_content,
            response_images=response_images,
        )
        return jsonify(
            {
                "code": 0,
                "message": "回复已提交",
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


@app.route("/complaints/<complaint_id>/complete", methods=["POST"])
def complete_complaint(complaint_id):
    """标记投诉处理完成。

    Args:
        complaint_id: 投诉单号

    请求体示例：
    {
        "session_key": "用户session_key"
    }
    """
    data = request.get_json()
    session_key = data.get("session_key")
    access_token = data.get("access_token", "")

    try:
        xpay.complete_complaint(
            access_token=access_token,
            session_key=session_key,
            complaint_id=complaint_id,
        )
        return jsonify(
            {
                "code": 0,
                "message": "投诉已标记为完成",
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


# ============================================================================
# 微信推送回调处理
# ============================================================================


@app.route("/notify", methods=["POST"])
def notify():
    """处理微信推送的回调通知。

    微信服务器会以 XML 或 JSON 格式向开发者服务器推送以下通知：
      - xpay_goods_deliver_notify  : 道具发货通知（用户购买道具后触发，需发货）
      - xpay_coin_pay_notify       : 代币支付通知（用户消耗代币后触发）
      - xpay_refund_notify         : 退款结果通知
      - xpay_complaint_notify      : 用户投诉通知
    """
    try:
        result = webhook_parser.callback(request.data)
        notification = result.notification

        if isinstance(notification, GoodsDeliverNotify):
            # 道具发货通知：完成发货后调用 notify_provide_goods() 确认
            LOGGER.info(f"收到道具发货通知: {notification.out_trade_no}")

            # TODO: 执行业务发货逻辑
            # 1. 根据 out_trade_no 查询订单
            # 2. 给用户发放道具
            # 3. 返回success_response() 确认发货完成

            return Response(result.success_response(), content_type=result.content_type)

        elif isinstance(notification, CoinPayNotify):
            # 代币支付通知：记录消费流水
            LOGGER.info(f"收到代币支付通知: {notification.out_trade_no}")

            # TODO: 记录消费日志，更新用户资产

            return Response(result.success_response(), content_type=result.content_type)

        elif isinstance(notification, RefundNotify):
            # 退款结果通知：ret_code=0 表示退款成功
            LOGGER.info(f"收到退款通知: {notification.mch_refund_id}")

            if notification.ret_code == 0:
                LOGGER.info(f"退款成功: {notification.refund_fee}")
                # TODO: 更新订单状态，通知用户
            else:
                LOGGER.warning(f"退款失败: {notification.ret_msg}")

            return Response(result.success_response(), content_type=result.content_type)

        elif isinstance(notification, ComplaintNotify):
            # 用户投诉通知：及时回复，避免影响商户评级
            LOGGER.warning(f"收到投诉通知: {notification.request_id}")

            # TODO: 发送告警通知，及时处理投诉
            # 可通过 response_complaint() 回复用户
            # 或通过 complete_complaint() 标记处理完成

            return Response(result.success_response(), content_type=result.content_type)

        else:
            LOGGER.warning(f"未知通知类型: {type(notification)}")
            return Response(
                result.fail_response("未知通知类型"), content_type=result.content_type, status=400
            )

    except Exception as e:
        LOGGER.exception("处理回调通知失败")
        return jsonify({"code": "FAIL", "message": str(e)}), 500


# ============================================================================
# 辅助接口
# ============================================================================


@app.route("/bill/download")
def download_bill():
    """下载对账单。"""
    session_key = request.args.get("session_key")
    access_token = request.args.get("access_token", "")
    begin_ds = request.args.get("begin_ds", type=int)
    end_ds = request.args.get("end_ds", type=int)

    try:
        result = xpay.download_bill(
            access_token=access_token,
            session_key=session_key,
            begin_ds=begin_ds,
            end_ds=end_ds,
        )
        return jsonify(
            {
                "code": 0,
                "message": "success",
                "data": {
                    "url": result.url,
                },
            }
        )
    except XPayError as e:
        return jsonify({"code": e.errcode, "message": e.errmsg}), 400


@app.route("/")
def index():
    """API 索引页。"""
    return jsonify(
        {
            "message": "WeChat XPay SDK Demo",
            "version": "0.6.0",
            "apis": {
                "user_balance": "/balance/<openid>",
                "currency_pay": "/pay (POST)",
                "cancel_pay": "/refund (POST)",
                "present": "/present (POST)",
                "order_query": "/order/<order_id>",
                "refund_cash": "/refund_cash (POST)",
                "goods_upload": "/goods/upload (POST)",
                "goods_publish": "/goods/publish (POST)",
                "biz_balance": "/biz_balance",
                "withdraw": "/withdraw (POST)",
                "adver_funds": "/adver_funds",
                "complaints": "/complaints",
                "webhook": "/notify (POST)",
            },
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
