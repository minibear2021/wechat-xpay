# WeChat XPay SDK 接口文档

本文档详细介绍 WeChat XPay Python SDK 的所有接口、数据模型和使用方法。

---

## 目录

- [快速开始](#快速开始)
- [客户端](#客户端)
  - [XPayClient (同步客户端)](#xpayclient-同步客户端)
  - [XPayAsyncClient (异步客户端)](#xpayasyncclient-异步客户端)
- [数据模型](#数据模型)
- [API 接口详解](#api-接口详解)
- [Webhook 处理](#webhook-处理)
- [认证工具](#认证工具)
- [异常处理](#异常处理)
- [错误码常量](#错误码常量)

---

## 快速开始

```python
from wechat_xpay import XPayClient, models

# 使用上下文管理器（推荐）
with XPayClient(
    app_id="wx1234567890",
    app_key="your_app_key",
    env=1,  # 0=正式, 1=沙箱
) as client:
    # 查询用户余额
    balance = client.query_user_balance(
        openid="user_openid",
        access_token="your_access_token",
        session_key="user_session_key",
    )
    print(f"余额: {balance.balance}")
```

---

## 客户端

### XPayClient (同步客户端)

同步 HTTP 客户端，基于 `httpx.Client` 实现。

#### 初始化参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `app_id` | `str` | 是 | 小程序 AppID |
| `app_key` | `str` | 是 | 用于计算 pay_sig 的 AppKey |
| `env` | `int` | 否 | 环境，0=生产(默认)，1=沙箱 |
| `base_url` | `str` | 否 | 自定义基础 URL |
| `logger` | `logging.Logger` | 否 | 日志记录器 |

#### 使用方式

**方式 1：上下文管理器（推荐）**
```python
with XPayClient(app_id="...", app_key="...") as client:
    result = client.query_user_balance(...)
```

**方式 2：手动管理**
```python
client = XPayClient(app_id="...", app_key="...")
result = client.query_user_balance(...)
client.close()
```

---

### XPayAsyncClient (异步客户端)

异步 HTTP 客户端，基于 `httpx.AsyncClient` 实现。所有方法与同步客户端相同，但返回 `Awaitable`。

#### 初始化参数

与 `XPayClient` 相同。

#### 使用方式

```python
async with XPayAsyncClient(app_id="...", app_key="...") as client:
    result = await client.query_user_balance(...)
```

---

## 数据模型

### UserBalance

用户代币余额信息。

| 字段 | 类型 | 说明 |
|------|------|------|
| `balance` | `int` | 代币总余额（包括有价和赠送） |
| `present_balance` | `int` | 赠送账户的代币余额 |
| `sum_save` | `int` | 累计有价货币充值数量 |
| `sum_present` | `int` | 累计赠送无价货币数量 |
| `sum_balance` | `int` | 历史总增加的代币金额 |
| `sum_cost` | `int` | 历史总消耗代币金额 |
| `first_save_flag` | `bool` | 是否满足首充活动标记 |

---

### CurrencyPayResult

代币支付结果。

| 字段 | 类型 | 说明 |
|------|------|------|
| `order_id` | `str` | 订单号 |
| `balance` | `int` | 支付后账户余额 |
| `used_present_amount` | `int` | 使用赠送金金额 |

---

### CancelCurrencyPayResult

取消代币支付结果。

| 字段 | 类型 | 说明 |
|------|------|------|
| `order_id` | `str` | 退款订单号 |

---

### PresentCurrencyResult

赠送代币结果。

| 字段 | 类型 | 说明 |
|------|------|------|
| `balance` | `int` | 赠送后账户总余额 |
| `order_id` | `str` | 赠送订单号 |
| `present_balance` | `int` | 赠送后赠送金余额 |

---

### Order

订单详情。

| 字段 | 类型 | 说明 |
|------|------|------|
| `order_id` | `str` | 订单号 |
| `create_time` | `int` | 创建时间戳 |
| `update_time` | `int` | 更新时间戳 |
| `status` | `int` | 订单状态 |
| `biz_type` | `int` | 业务类型 |
| `order_fee` | `int` | 订单金额（分） |
| `paid_fee` | `int` | 实付金额（分） |
| `order_type` | `int` | 订单类型 |
| `env_type` | `int` | 环境类型 |
| `coupon_fee` | `int \| None` | 优惠金额 |
| `refund_fee` | `int \| None` | 已退款金额 |
| `paid_time` | `int \| None` | 支付时间 |
| `provide_time` | `int \| None` | 发货时间 |
| `biz_meta` | `str \| None` | 业务元数据 |
| `token` | `str \| None` | 订单 Token |
| `left_fee` | `int \| None` | 剩余可退金额 |
| `wx_order_id` | `str \| None` | 微信订单号 |
| `channel_order_id` | `str \| None` | 渠道订单号 |
| `wxpay_order_id` | `str \| None` | 微信支付订单号 |
| `sett_time` | `int \| None` | 结算时间 |
| `sett_state` | `int \| None` | 结算状态 |
| `platform_fee_fen` | `int \| None` | 平台手续费（分） |
| `cps_fee_fen` | `int \| None` | CPS 费用（分） |

---

### RefundOrderResult

现金订单退款结果。

| 字段 | 类型 | 说明 |
|------|------|------|
| `refund_order_id` | `str` | 退款订单号 |
| `refund_wx_order_id` | `str` | 微信退款单号 |
| `pay_order_id` | `str` | 原支付订单号 |
| `pay_wx_order_id` | `str` | 原微信订单号 |

---

### WithdrawOrderResult

创建提现订单结果。

| 字段 | 类型 | 说明 |
|------|------|------|
| `withdraw_no` | `str` | 商户提现单号 |
| `wx_withdraw_no` | `str` | 微信提现单号 |

---

### WithdrawOrder

提现订单详情。

| 字段 | 类型 | 说明 |
|------|------|------|
| `withdraw_no` | `str` | 商户提现单号 |
| `status` | `int` | 提现状态 |
| `withdraw_amount` | `str` | 提现金额 |
| `wx_withdraw_no` | `str` | 微信提现单号 |
| `withdraw_success_timestamp` | `str \| None` | 提现成功时间 |
| `create_time` | `str \| None` | 创建时间 |
| `fail_reason` | `str \| None` | 失败原因 |

---

### BillDownload

账单下载信息。

| 字段 | 类型 | 说明 |
|------|------|------|
| `url` | `str` | 账单下载 URL（30 分钟有效） |

---

### BizBalance

商家可提现余额。

| 字段 | 类型 | 说明 |
|------|------|------|
| `balance_available` | `BizBalanceAvailable` | 可用余额详情 |

### BizBalanceAvailable

| 字段 | 类型 | 说明 |
|------|------|------|
| `amount` | `str` | 可用金额 |
| `currency_code` | `str` | 货币代码 |

---

### TransferAccount

广告金充值账户。

| 字段 | 类型 | 说明 |
|------|------|------|
| `transfer_account_name` | `str` | 账户名称 |
| `transfer_account_uid` | `int` | 账户 UID |
| `transfer_account_agency_id` | `int` | 代理 ID |
| `transfer_account_agency_name` | `str` | 代理名称 |
| `state` | `int` | 状态 |
| `bind_result` | `int` | 绑定结果 |
| `error_msg` | `str \| None` | 错误信息 |

---

### AdverFund

广告金发放记录。

| 字段 | 类型 | 说明 |
|------|------|------|
| `settle_begin` | `int` | 结算开始时间 |
| `settle_end` | `int` | 结算结束时间 |
| `total_amount` | `int` | 总金额 |
| `remain_amount` | `int` | 剩余金额 |
| `expire_time` | `int` | 过期时间 |
| `fund_type` | `int` | 资金类型 |
| `fund_id` | `str` | 资金记录 ID |

### AdverFundList

| 字段 | 类型 | 说明 |
|------|------|------|
| `adver_funds_list` | `list[AdverFund]` | 发放记录列表 |
| `total_page` | `int` | 总页数 |

---

### FundsBillResult

创建广告金账单结果。

| 字段 | 类型 | 说明 |
|------|------|------|
| `bill_id` | `str` | 账单 ID |

---

### FundsBillItem

广告金账单项。

| 字段 | 类型 | 说明 |
|------|------|------|
| `bill_id` | `str` | 账单 ID |
| `oper_time` | `int` | 操作时间 |
| `settle_begin` | `int` | 结算开始 |
| `settle_end` | `int` | 结算结束 |
| `fund_id` | `str` | 资金 ID |
| `transfer_account_name` | `str` | 转账账户名 |
| `transfer_account_uid` | `int` | 转账账户 UID |
| `transfer_amount` | `int` | 转账金额 |
| `status` | `int` | 状态 |
| `request_id` | `str` | 请求 ID |

### FundsBillList

| 字段 | 类型 | 说明 |
|------|------|------|
| `bill_list` | `list[FundsBillItem]` | 账单列表 |
| `total_page` | `int` | 总页数 |

---

### RecoverBillItem

回收账单项。

| 字段 | 类型 | 说明 |
|------|------|------|
| `bill_id` | `str` | 账单 ID |
| `recover_time` | `int` | 回收时间 |
| `settle_begin` | `int` | 结算开始 |
| `settle_end` | `int` | 结算结束 |
| `fund_id` | `str` | 资金 ID |
| `recover_account_name` | `str` | 回收账户名 |
| `recover_amount` | `int` | 回收金额 |
| `refund_order_list` | `list[str]` | 退款订单列表 |

### RecoverBillList

| 字段 | 类型 | 说明 |
|------|------|------|
| `bill_list` | `list[RecoverBillItem]` | 账单列表 |
| `total_page` | `int` | 总页数 |

---

### GoodsUploadItem

道具上传项。

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `str` | 道具 ID |
| `name` | `str` | 道具名称 |
| `price` | `int` | 价格 |
| `remark` | `str` | 备注 |
| `item_url` | `str` | 图片 URL |
| `upload_status` | `int \| None` | 上传状态 |
| `errmsg` | `str \| None` | 错误信息 |

### GoodsUploadStatus

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | `int` | 任务状态 |
| `upload_item` | `list[GoodsUploadItem]` | 上传项列表 |

---

### GoodsPublishItem

道具发布项。

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | `str` | 道具 ID |
| `publish_status` | `int \| None` | 发布状态 |
| `errmsg` | `str \| None` | 错误信息 |

### GoodsPublishStatus

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | `int` | 任务状态 |
| `publish_item` | `list[GoodsPublishItem]` | 发布项列表 |

---

### Complaint

投诉信息。

| 字段 | 类型 | 说明 |
|------|------|------|
| `complaint_id` | `str` | 投诉 ID |
| `complaint_time` | `str` | 投诉时间 |
| `complaint_detail` | `str` | 投诉详情 |
| `complaint_state` | `str` | 投诉状态 |
| `payer_openid` | `str` | 投诉人 OpenID |
| `complaint_order_info` | `list[ComplaintOrderInfo]` | 订单信息 |
| `complaint_full_refunded` | `bool` | 是否全额退款 |
| `incoming_user_response` | `bool` | 是否有用户回应 |
| `user_complaint_times` | `int` | 投诉次数 |
| `complaint_media_list` | `list[ComplaintMedia]` | 媒体列表 |
| `problem_description` | `str \| None` | 问题描述 |
| `problem_type` | `str \| None` | 问题类型 |
| `apply_refund_amount` | `int \| None` | 申请退款金额 |
| `user_tag_list` | `list[str]` | 用户标签 |
| `service_order_info` | `list[ServiceOrderInfo]` | 服务订单信息 |
| `payer_phone` | `str \| None` | 投诉人电话 |

### ComplaintList

| 字段 | 类型 | 说明 |
|------|------|------|
| `total` | `int` | 总数 |
| `complaints` | `list[Complaint]` | 投诉列表 |

---

### ComplaintOrderInfo

| 字段 | 类型 | 说明 |
|------|------|------|
| `transaction_id` | `str` | 交易 ID |
| `out_trade_no` | `str` | 商户订单号 |
| `amount` | `int` | 金额 |
| `wxa_out_trade_no` | `str` | 小程序订单号 |
| `wx_order_id` | `str` | 微信订单号 |

---

### ComplaintMedia

| 字段 | 类型 | 说明 |
|------|------|------|
| `media_type` | `str` | 媒体类型 |
| `media_url` | `list[str]` | 媒体 URL 列表 |

---

### ServiceOrderInfo

| 字段 | 类型 | 说明 |
|------|------|------|
| `order_id` | `str` | 订单 ID |
| `out_order_no` | `str` | 商户订单号 |
| `state` | `str` | 状态 |

---

### NegotiationRecord

协商记录。

| 字段 | 类型 | 说明 |
|------|------|------|
| `log_id` | `str` | 日志 ID |
| `operator` | `str` | 操作人 |
| `operate_time` | `str` | 操作时间 |
| `operate_type` | `str` | 操作类型 |
| `operate_details` | `str` | 操作详情 |
| `complaint_media_list` | `list[ComplaintMedia]` | 媒体列表 |

### NegotiationHistory

| 字段 | 类型 | 说明 |
|------|------|------|
| `total` | `int` | 总数 |
| `history` | `list[NegotiationRecord]` | 历史记录 |

---

### UploadFileResult

上传文件结果。

| 字段 | 类型 | 说明 |
|------|------|------|
| `file_id` | `str` | 文件 ID |

---

### UploadFileSign

上传文件签名。

| 字段 | 类型 | 说明 |
|------|------|------|
| `sign` | `str` | 签名 |
| `cos_url` | `str \| None` | COS 上传 URL |

---

### NotifyProvideGoodsResult

发货通知结果。

| 字段 | 类型 | 说明 |
|------|------|------|
| `order_id` | `str` | 订单号 |
| `out_trade_no` | `str` | 商户订单号 |
| `provide_status` | `int` | 发货状态 |

---

## API 接口详解

### 用户代币管理

#### query_user_balance

查询用户代币余额。

```python
def query_user_balance(
    self,
    openid: str,
    access_token: str,
    session_key: str,
    user_ip: str | None = None,
) -> UserBalance
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `openid` | `str` | 是 | 用户的 OpenID |
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `user_ip` | `str` | 否 | 用户 IP，如 "1.1.1.1" |

**返回值：** `UserBalance`

---

#### currency_pay

扣除代币进行支付。

```python
def currency_pay(
    self,
    openid: str,
    access_token: str,
    session_key: str,
    order_id: str,
    amount: int,
    payitem: str,
    user_ip: str | None = None,
    remark: str | None = None,
) -> CurrencyPayResult
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `openid` | `str` | 是 | 用户的 OpenID |
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `order_id` | `str` | 是 | 订单号 |
| `amount` | `int` | 是 | 支付的代币数量 |
| `payitem` | `str` | 是 | 物品信息，JSON 格式 |
| `user_ip` | `str` | 否 | 用户 IP |
| `remark` | `str` | 否 | 备注 |

**payitem 示例：**
```json
[{"productid":"item1", "unit_price": 100, "quantity": 2}]
```

**返回值：** `CurrencyPayResult`

---

#### cancel_currency_pay

取消代币支付（退款）。

```python
def cancel_currency_pay(
    self,
    openid: str,
    access_token: str,
    session_key: str,
    pay_order_id: str,
    order_id: str,
    amount: int,
    user_ip: str | None = None,
) -> CancelCurrencyPayResult
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `openid` | `str` | 是 | 用户的 OpenID |
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `pay_order_id` | `str` | 是 | 原代币支付订单号 |
| `order_id` | `str` | 是 | 本次退款单号 |
| `amount` | `int` | 是 | 退款金额 |
| `user_ip` | `str` | 否 | 用户 IP |

**返回值：** `CancelCurrencyPayResult`

---

#### present_currency

赠送代币给用户。

```python
def present_currency(
    self,
    openid: str,
    access_token: str,
    session_key: str,
    order_id: str,
    amount: int,
) -> PresentCurrencyResult
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `openid` | `str` | 是 | 用户的 OpenID |
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `order_id` | `str` | 是 | 赠送订单 ID |
| `amount` | `int` | 是 | 赠送金额 |

**返回值：** `PresentCurrencyResult`

---

### 订单管理

#### query_order

查询订单详情。

```python
def query_order(
    self,
    openid: str,
    access_token: str,
    session_key: str,
    order_id: str | None = None,
    wx_order_id: str | None = None,
) -> Order
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `openid` | `str` | 是 | 用户的 OpenID |
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `order_id` | `str` | 否 | 订单号（与 wx_order_id 二选一） |
| `wx_order_id` | `str` | 否 | 微信内部单号（与 order_id 二选一） |

**返回值：** `Order`

---

#### refund_order

现金订单退款。

```python
def refund_order(
    self,
    openid: str,
    access_token: str,
    session_key: str,
    refund_order_id: str,
    left_fee: int,
    refund_fee: int,
    refund_reason: str,
    req_from: str,
    order_id: str | None = None,
    wx_order_id: str | None = None,
    biz_meta: str | None = None,
) -> RefundOrderResult
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `openid` | `str` | 是 | 用户的 OpenID |
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `refund_order_id` | `str` | 是 | 退款订单 ID（8-32 位） |
| `left_fee` | `int` | 是 | 当前可退金额 |
| `refund_fee` | `int` | 是 | 退款金额（0 < refund_fee <= left_fee） |
| `refund_reason` | `str` | 是 | 退款原因："0"-无, "1"-商品问题, "2"-服务, "3"-用户请求, "4"-价格, "5"-其他 |
| `req_from` | `str` | 是 | 请求来源："1"-人工, "2"-用户发起, "3"-其他 |
| `order_id` | `str` | 否 | 订单号（与 wx_order_id 二选一） |
| `wx_order_id` | `str` | 否 | 微信单号（与 order_id 二选一） |
| `biz_meta` | `str` | 否 | 自定义数据（0-1024 字符） |

**返回值：** `RefundOrderResult`

---

### 提现管理

#### create_withdraw_order

创建提现订单。

```python
def create_withdraw_order(
    self,
    access_token: str,
    session_key: str,
    withdraw_no: str,
    withdraw_amount: str | None = None,
) -> WithdrawOrderResult
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `withdraw_no` | `str` | 是 | 提现订单号（8-32 位） |
| `withdraw_amount` | `str` | 否 | 提现金额（元，如 "0.01"），省略表示全额 |

**返回值：** `WithdrawOrderResult`

---

#### query_withdraw_order

查询提现订单。

```python
def query_withdraw_order(
    self,
    access_token: str,
    session_key: str,
    withdraw_no: str,
) -> WithdrawOrder
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `withdraw_no` | `str` | 是 | 提现订单号 |

**返回值：** `WithdrawOrder`

---

#### download_bill

下载小程序账单。

```python
def download_bill(
    self,
    access_token: str,
    session_key: str,
    begin_ds: int,
    end_ds: int,
) -> BillDownload
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `begin_ds` | `int` | 是 | 开始日期（如 20230801） |
| `end_ds` | `int` | 是 | 结束日期（如 20230810） |

**返回值：** `BillDownload`

---

### 商家余额和广告金

#### query_biz_balance

查询商家可提现余额。

```python
def query_biz_balance(
    self,
    access_token: str,
    session_key: str,
) -> BizBalance
```

**返回值：** `BizBalance`

---

#### query_transfer_account

查询广告金充值账户。

```python
def query_transfer_account(
    self,
    access_token: str,
    session_key: str,
) -> list[TransferAccount]
```

**返回值：** `TransferAccount` 对象列表

---

#### query_adver_funds

查询广告金发放记录。

```python
def query_adver_funds(
    self,
    access_token: str,
    session_key: str,
    page: int = 1,
    page_size: int = 10,
) -> AdverFundList
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `page` | `int` | 否 | 页码（>= 1） |
| `page_size` | `int` | 否 | 每页记录数 |

**返回值：** `AdverFundList`

---

#### create_funds_bill

创建广告金账单。

```python
def create_funds_bill(
    self,
    access_token: str,
    session_key: str,
    transfer_account_uid: int,
    transfer_account_agency_id: int,
    transfer_amount: int,
    fund_id: str,
    settle_begin: int,
    settle_end: int,
    request_id: str | None = None,
) -> FundsBillResult
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `transfer_account_uid` | `int` | 是 | 转账账户 UID |
| `transfer_account_agency_id` | `int` | 是 | 转账账户代理 ID |
| `transfer_amount` | `int` | 是 | 转账金额（分） |
| `fund_id` | `str` | 是 | 广告金发放记录 ID |
| `settle_begin` | `int` | 是 | 结算开始时间戳 |
| `settle_end` | `int` | 是 | 结算结束时间戳 |
| `request_id` | `str` | 否 | 请求 ID（幂等控制） |

**返回值：** `FundsBillResult`

---

#### bind_transfer_account

绑定转账账户。

```python
def bind_transfer_account(
    self,
    access_token: str,
    session_key: str,
    transfer_account_uid: int,
    transfer_account_agency_id: int,
) -> bool
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `transfer_account_uid` | `int` | 是 | 转账账户 UID |
| `transfer_account_agency_id` | `int` | 是 | 转账账户代理 ID |

**返回值：** `True` 表示成功

---

#### query_funds_bill

查询资金账单。

```python
def query_funds_bill(
    self,
    access_token: str,
    session_key: str,
    page: int = 1,
    page_size: int = 10,
) -> FundsBillList
```

**返回值：** `FundsBillList`

---

#### query_recover_bill

查询回收账单。

```python
def query_recover_bill(
    self,
    access_token: str,
    session_key: str,
    page: int = 1,
    page_size: int = 10,
) -> RecoverBillList
```

**返回值：** `RecoverBillList`

---

#### download_adverfunds_order

下载广告金订单账单。

```python
def download_adverfunds_order(
    self,
    access_token: str,
    session_key: str,
    begin_ds: int,
    end_ds: int,
) -> AdverfundsOrderDownload
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `begin_ds` | `int` | 是 | 开始日期（如 20230801） |
| `end_ds` | `int` | 是 | 结束日期（如 20230810） |

**返回值：** `AdverfundsOrderDownload`

---

### 投诉管理

#### get_complaint_list

获取投诉列表。

```python
def get_complaint_list(
    self,
    access_token: str,
    session_key: str,
    begin_date: str,
    end_date: str,
    offset: int = 0,
    limit: int = 10,
) -> ComplaintList
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `begin_date` | `str` | 是 | 开始日期（yyyy-mm-dd） |
| `end_date` | `str` | 是 | 结束日期（yyyy-mm-dd） |
| `offset` | `int` | 否 | 分页偏移量（从 0 开始） |
| `limit` | `int` | 否 | 最大返回记录数 |

**返回值：** `ComplaintList`

---

#### get_complaint_detail

获取投诉详情。

```python
def get_complaint_detail(
    self,
    access_token: str,
    session_key: str,
    complaint_id: str,
) -> Complaint
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `complaint_id` | `str` | 是 | 投诉 ID |

**返回值：** `Complaint`

---

#### response_complaint

回复投诉。

```python
def response_complaint(
    self,
    access_token: str,
    session_key: str,
    complaint_id: str,
    response_content: str,
    response_images: list | None = None,
) -> bool
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `complaint_id` | `str` | 是 | 投诉 ID |
| `response_content` | `str` | 是 | 回复内容 |
| `response_images` | `list` | 否 | 图片文件 ID 列表（来自 upload_vp_file） |

**返回值：** `True` 表示成功

---

#### complete_complaint

完成投诉处理。

```python
def complete_complaint(
    self,
    access_token: str,
    session_key: str,
    complaint_id: str,
) -> bool
```

**返回值：** `True` 表示成功

---

#### upload_vp_file

上传媒体文件（图片、凭证等）。

```python
def upload_vp_file(
    self,
    access_token: str,
    session_key: str,
    file_name: str,
    base64_img: str | None = None,
    img_url: str | None = None,
) -> UploadFileResult
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `file_name` | `str` | 是 | 文件名称 |
| `base64_img` | `str` | 否 | Base64 编码的图片（最大 1MB） |
| `img_url` | `str` | 否 | 图片 URL（最大 2MB，推荐） |

**返回值：** `UploadFileResult`

---

#### get_negotiation_history

获取协商历史。

```python
def get_negotiation_history(
    self,
    access_token: str,
    session_key: str,
    complaint_id: str,
    offset: int = 0,
    limit: int = 10,
) -> NegotiationHistory
```

**返回值：** `NegotiationHistory`

---

### 发货管理

#### notify_provide_goods

发货完成通知。

```python
def notify_provide_goods(
    self,
    access_token: str,
    session_key: str,
    order_id: str | None = None,
    wx_order_id: str | None = None,
) -> NotifyProvideGoodsResult
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `order_id` | `str` | 否 | 订单号（与 wx_order_id 二选一） |
| `wx_order_id` | `str` | 否 | 微信内部单号（与 order_id 二选一） |

**返回值：** `NotifyProvideGoodsResult`

---

### 道具管理

#### start_upload_goods

启动道具上传。

```python
def start_upload_goods(
    self,
    access_token: str,
    session_key: str,
    goods: list[dict[str, Any]],
) -> GoodsUploadStatus
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `goods` | `list[dict]` | 是 | 道具列表 |

**goods 项格式：**
```python
{
    "id": str,       # 道具 ID
    "name": str,     # 道具名称
    "price": int,    # 价格（分）
    "remark": str,   # 备注
    "item_url": str  # 图片 URL
}
```

**返回值：** `GoodsUploadStatus`

---

#### query_upload_goods

查询道具上传状态。

```python
def query_upload_goods(
    self,
    access_token: str,
    session_key: str,
) -> GoodsUploadStatus
```

**返回值：** `GoodsUploadStatus`

---

#### start_publish_goods

启动道具发布。

```python
def start_publish_goods(
    self,
    access_token: str,
    session_key: str,
    goods: list[dict[str, Any]],
) -> GoodsPublishStatus
```

**goods 项格式：**
```python
{
    "id": str  # 道具 ID
}
```

**返回值：** `GoodsPublishStatus`

---

#### query_publish_goods

查询道具发布状态。

```python
def query_publish_goods(
    self,
    access_token: str,
    session_key: str,
) -> GoodsPublishStatus
```

**返回值：** `GoodsPublishStatus`

---

### 文件上传签名

#### get_upload_file_sign

获取上传文件签名。

```python
def get_upload_file_sign(
    self,
    access_token: str,
    session_key: str,
    file_name: str,
    file_type: str,
) -> UploadFileSign
```

**参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `access_token` | `str` | 是 | 接口调用凭证 |
| `session_key` | `str` | 是 | 用户的 session_key |
| `file_name` | `str` | 是 | 文件名称 |
| `file_type` | `str` | 是 | 文件类型，如 "image/jpeg", "image/png" |

**返回值：** `UploadFileSign`

---

## Webhook 处理

### WebhookParser

解析微信 XPay 推送通知。

```python
from wechat_xpay import WebhookParser

parser = WebhookParser()
result = parser.callback(request_body)

# 获取解析后的通知对象
notification = result.notification

# 返回成功响应
return result.success_response()

# 或返回失败响应
return result.fail_response("处理失败")
```

### CallbackResult

`callback()` 方法的返回结果。

| 属性 | 类型 | 说明 |
|------|------|------|
| `notification` | `GoodsDeliverNotify \| CoinPayNotify \| RefundNotify \| ComplaintNotify` | 解析后的通知对象 |
| `content_type` | `str` | 响应 Content-Type |

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `success_response()` | `str` | 成功应答字符串 |
| `fail_response(message="FAIL")` | `str` | 失败应答字符串 |

### 通知类型

#### GoodsDeliverNotify

发货通知。

| 字段 | 类型 | 说明 |
|------|------|------|
| `to_user_name` | `str` | 接收者 |
| `from_user_name` | `str` | 发送者 |
| `create_time` | `int` | 创建时间 |
| `msg_type` | `str` | 消息类型 |
| `event` | `str` | 事件类型 |
| `open_id` | `str` | 用户 OpenID |
| `out_trade_no` | `str` | 商户订单号 |
| `env` | `int` | 环境 |
| `wechat_pay_info` | `WechatPayInfo \| None` | 支付信息 |
| `goods_info` | `GoodsInfo \| None` | 商品信息 |
| `team_info` | `TeamInfo \| None` | 拼团信息 |

#### CoinPayNotify

代币支付通知。

| 字段 | 类型 | 说明 |
|------|------|------|
| `to_user_name` | `str` | 接收者 |
| `from_user_name` | `str` | 发送者 |
| `create_time` | `int` | 创建时间 |
| `msg_type` | `str` | 消息类型 |
| `event` | `str` | 事件类型 |
| `open_id` | `str` | 用户 OpenID |
| `out_trade_no` | `str` | 商户订单号 |
| `env` | `int` | 环境 |
| `wechat_pay_info` | `WechatPayInfo \| None` | 支付信息 |
| `coin_info` | `CoinInfo \| None` | 代币信息 |

#### RefundNotify

退款通知。

| 字段 | 类型 | 说明 |
|------|------|------|
| `to_user_name` | `str` | 接收者 |
| `from_user_name` | `str` | 发送者 |
| `create_time` | `int` | 创建时间 |
| `msg_type` | `str` | 消息类型 |
| `event` | `str` | 事件类型 |
| `open_id` | `str` | 用户 OpenID |
| `wx_refund_id` | `str` | 微信退款单号 |
| `mch_refund_id` | `str` | 商户退款单号 |
| `wx_order_id` | `str` | 微信订单号 |
| `mch_order_id` | `str` | 商户订单号 |
| `refund_fee` | `int` | 退款金额 |
| `ret_code` | `int` | 返回码 |
| `ret_msg` | `str` | 返回消息 |
| `refund_start_timestamp` | `int` | 退款开始时间 |
| `refund_succ_timestamp` | `int` | 退款成功时间 |
| `wxpay_refund_transaction_id` | `str` | 微信支付退款单号 |
| `retry_times` | `int` | 重试次数 |
| `team_info` | `TeamInfo \| None` | 拼团信息 |

#### ComplaintNotify

投诉通知。

| 字段 | 类型 | 说明 |
|------|------|------|
| `to_user_name` | `str` | 接收者 |
| `from_user_name` | `str` | 发送者 |
| `create_time` | `int` | 创建时间 |
| `msg_type` | `str` | 消息类型 |
| `event` | `str` | 事件类型 |
| `open_id` | `str` | 用户 OpenID |
| `wx_order_id` | `str` | 微信订单号 |
| `mch_order_id` | `str` | 商户订单号 |
| `complaint_time` | `int` | 投诉时间 |
| `retry_times` | `int` | 重试次数 |
| `request_id` | `str` | 请求 ID |

---

## 认证工具

### calc_pay_sig

计算支付签名 pay_sig。

```python
from wechat_xpay import calc_pay_sig

pay_sig = calc_pay_sig(
    app_id="wx123456",
    session_key="...",
    path="/xpay/query_user_balance",
    json_body='{"openid": "xxx"}',
    env=0,
)
```

### calc_signature

计算用户态签名 signature。

```python
from wechat_xpay import calc_signature

signature = calc_signature(
    session_key="...",
    json_body='{"openid": "xxx"}',
)
```

### generate_request_signature

生成请求签名（包含时间戳和随机串）。

```python
from wechat_xpay import generate_request_signature

sign, timestamp, nonce_str = generate_request_signature(
    api_key="...",
    params={"key": "value"},
)
```

### verify_webhook_signature

验证 Webhook 签名。

```python
from wechat_xpay import verify_webhook_signature

is_valid = verify_webhook_signature(
    api_key="...",
    signature="...",
    timestamp="...",
    nonce_str="...",
    body="...",
)
```

### generate_timestamp

生成时间戳。

```python
from wechat_xpay import generate_timestamp

timestamp = generate_timestamp()  # 返回 str 类型时间戳
```

### generate_nonce_str

生成随机字符串。

```python
from wechat_xpay import generate_nonce_str

nonce = generate_nonce_str(length=32)
```

---

## 异常处理

### XPayError

所有 SDK 异常的基类。

```python
from wechat_xpay import XPayError
```

### XPayAPIError

API 返回非零错误码时抛出。

```python
from wechat_xpay import XPayAPIError

try:
    result = client.query_user_balance(...)
except XPayAPIError as e:
    print(f"错误码: {e.errcode}")
    print(f"错误信息: {e.errmsg}")
```

| 属性 | 类型 | 说明 |
|------|------|------|
| `errcode` | `int` | 微信错误码 |
| `errmsg` | `str` | 错误描述 |

---

## 错误码常量

SDK 提供了所有微信 XPay 错误码的常量定义：

```python
from wechat_xpay import (
    ERR_SYSTEM_ERROR,              # -1: 系统错误
    ERR_INVALID_OPENID,            # 268490001: openid 错误
    ERR_BAD_REQUEST_PARAMS,        # 268490002: 请求参数字段错误
    ERR_SIGNATURE_ERROR,           # 268490003: 签名错误
    ERR_DUPLICATE_OPERATION,       # 268490004: 重复操作
    ERR_ORDER_ALREADY_REFUNDED,    # 268490005: 订单已退款
    ERR_INSUFFICIENT_TOKEN_BALANCE, # 268490006: 代币余额不足
    ERR_SENSITIVE_CONTENT,         # 268490007: 敏感内容
    ERR_TOKEN_NOT_PUBLISHED,       # 268490008: 代币未发布
    ERR_SESSION_KEY_EXPIRED,       # 268490009: session_key 过期
    # ... 更多错误码
)
```

### 完整错误码列表

| 常量名 | 错误码 | 描述 |
|--------|--------|------|
| `ERR_SYSTEM_ERROR` | -1 | 系统错误 |
| `ERR_INVALID_OPENID` | 268490001 | openid 错误 |
| `ERR_BAD_REQUEST_PARAMS` | 268490002 | 请求参数字段错误 |
| `ERR_SIGNATURE_ERROR` | 268490003 | 签名错误 |
| `ERR_DUPLICATE_OPERATION` | 268490004 | 重复操作 |
| `ERR_ORDER_ALREADY_REFUNDED` | 268490005 | 订单已退款 |
| `ERR_INSUFFICIENT_TOKEN_BALANCE` | 268490006 | 代币余额不足 |
| `ERR_SENSITIVE_CONTENT` | 268490007 | 敏感内容 |
| `ERR_TOKEN_NOT_PUBLISHED` | 268490008 | 代币未发布 |
| `ERR_SESSION_KEY_EXPIRED` | 268490009 | session_key 过期 |
| `ERR_DATA_GENERATING` | 268490011 | 数据生成中 |
| `ERR_BATCH_TASK_RUNNING` | 268490012 | 批量任务运行中 |
| `ERR_CANNOT_REFUND_VERIFIED_ORDER` | 268490013 | 不能退款已核销订单 |
| `ERR_REFUND_IN_PROGRESS` | 268490014 | 退款进行中 |
| `ERR_RATE_LIMIT_EXCEEDED` | 268490015 | 频率限制 |
| `ERR_LEFT_FEE_MISMATCH` | 268490016 | 可退金额不匹配 |
| `ERR_INVALID_ENV` | 268447747 | 无效环境 |
| `ERR_INVALID_APPID` | 268447748 | 无效 AppID |
| `ERR_MCH_NO_PERMISSION` | 268447749 | 商户无权限 |
| `ERR_USER_NOT_REGISTERED` | 268500000 | 用户未注册 |
| `ERR_INVALID_SIGN_TYPE` | 268500001 | 无效签名类型 |
| `ERR_INVALID_BODY_PARAM` | 268500002 | 无效 body 参数 |
| `ERR_APPID_MCHID_MISMATCH` | 268500003 | AppID 与商户号不匹配 |
| `ERR_RESOURCE_NOT_EXIST` | 268500004 | 资源不存在 |
| `ERR_SIGN_VERIFICATION_FAILED` | 268500005 | 签名验证失败 |
| `ERR_MCH_NOT_EXISTS` | 268500006 | 商户不存在 |
| `ERR_MCH_ACCOUNT_ABNORMAL` | 268500007 | 商户账户异常 |
| `ERR_AMOUNT_MISMATCH` | 268500008 | 金额不匹配 |
| `ERR_SERVICE_NOT_ENABLED` | 268500009 | 服务未启用 |
| `ERR_REFUND_FEE_EXCEEDED` | 268500010 | 退款金额超过订单金额 |
| `ERR_ORDER_PAID` | 268500011 | 订单已支付 |
| `ERR_ORDER_CLOSED` | 268500012 | 订单已关闭 |
| `ERR_MCH_CONFIG_LIMITED` | 268500013 | 商户配置受限 |
| `ERR_REAL_NAME_REQUIRED` | 268500014 | 需要实名认证 |
| `ERR_BANK_CARD_NOT_SUPPORTED` | 268500015 | 银行卡不支持 |
| `ERR_ACCOUNT_FROZEN` | 268500016 | 账户被冻结 |
| `ERR_ORDER_NOT_EXIST` | 268500017 | 订单不存在 |
| `ERR_REFUND_NOT_EXIST` | 268500018 | 退款不存在 |
| `ERR_REFUND_AMOUNT_LIMIT` | 268500019 | 退款金额限制 |
| `ERR_INVALID_TRANSACTION_ID` | 268500020 | 无效交易 ID |
| `ERR_BALANCE_NOT_ENOUGH` | 268500021 | 余额不足 |
| `ERR_REFUND_FEE_LIMIT` | 268500022 | 退款费用限制 |
| `ERR_SYSTEM_BUSY` | 268500023 | 系统繁忙 |
| `ERR_UPLOAD_FILE_FAILED` | 268500024 | 上传文件失败 |
| `ERR_INVALID_FILE_TYPE` | 268500025 | 无效文件类型 |
| `ERR_FILE_SIZE_EXCEEDED` | 268500026 | 文件大小超出限制 |
| `ERR_INVALID_GOODS_CONFIG` | 268500027 | 无效商品配置 |
| `ERR_GOODS_NOT_PUBLISHED` | 268500028 | 商品未发布 |
| `ERR_BATCH_TASK_FAILED` | 268500029 | 批量任务失败 |
| `ERR_WITHDRAW_AMOUNT_LIMIT` | 268500030 | 提现金额限制 |
| `ERR_WITHDRAW_FEE_LIMIT` | 268500031 | 提现费用限制 |
| `ERR_WITHDRAW_COUNT_LIMIT` | 268500032 | 提现次数限制 |
| `ERR_TRANSFER_ACCOUNT_NOT_BOUND` | 268500033 | 转账账户未绑定 |
| `ERR_ADVER_FUNDS_NOT_ENOUGH` | 268500034 | 广告金不足 |
| `ERR_BILL_GENERATING` | 268500035 | 账单生成中 |
| `ERR_REFUND_APPLICATION_EXIST` | 268500036 | 退款申请已存在 |
| `ERR_COMPLAINT_NOT_EXIST` | 268500037 | 投诉不存在 |
| `ERR_NEGOTIATION_FAILED` | 268500038 | 协商失败 |
| `ERR_INVALID_MEDIA_TYPE` | 268500039 | 无效媒体类型 |
| `ERR_MEDIA_UPLOAD_FAILED` | 268500040 | 媒体上传失败 |
| `ERR_IMAGE_SIZE_EXCEEDED` | 268500041 | 图片大小超出限制 |
| `ERR_IMAGE_FORMAT_NOT_SUPPORTED` | 268500042 | 不支持的图片格式 |
| `ERR_VIDEO_SIZE_EXCEEDED` | 268500043 | 视频大小超出限制 |
| `ERR_VIDEO_FORMAT_NOT_SUPPORTED` | 268500044 | 不支持的视频格式 |
