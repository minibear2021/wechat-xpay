# SDK 与 API 文档一致性检查报告

> 检查日期：2026-03-12
> 对比文件：`docs/apis.md` vs `wechat_xpay/models.py` + `wechat_xpay/client.py` + `wechat_xpay/async_client.py` + `wechat_xpay/base.py`

## 总结

| 类别 | 数量 |
|------|------|
| API 接口总数（文档） | 24 |
| SDK 实现接口数 | 24 |
| 完全一致 | 12 |
| 存在问题 | 12 |

### 问题分级

| 严重程度 | 数量 | 说明 |
|----------|------|------|
| **严重** (会导致运行时错误) | 3 | 参数完全错误或返回值解析会崩溃 |
| **高** (功能缺失/参数错误) | 5 | 缺少必要参数、参数名错误、返回值模型不匹配 |
| **中** (签名/逻辑不一致) | 2 | 签名类型可能不正确 |
| **低** (无影响的冗余) | 2 | 多余的返回字段但不会导致崩溃 |

---

## 逐接口检查

---

### 1. query_user_balance - 查询用户代币余额

**结果：✅ 一致**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | openid, env(自动), user_ip(可选) |
| 返回模型 `UserBalance` | ✅ | balance, present_balance, sum_save, sum_present, sum_balance, sum_cost, first_save_flag |
| 签名类型 | ✅ | `needs_user_sig=True`，文档要求"用户态签名与支付签名" |

---

### 2. currency_pay - 扣减代币

**结果：✅ 一致**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | openid, env(自动), user_ip(可选), amount, order_id, payitem, remark(可选) |
| 返回模型 `CurrencyPayResult` | ✅ | order_id, balance, used_present_amount |
| 签名类型 | ✅ | `needs_user_sig=True`，文档要求"用户态签名与支付签名" |

---

### 3. cancel_currency_pay - 代币支付退款

**结果：⚠️ 中等问题**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | openid, env(自动), user_ip(可选), pay_order_id, order_id, amount |
| 返回模型 `CancelCurrencyPayResult` | ✅ | order_id |
| 签名类型 | ⚠️ | SDK 未设置 `needs_user_sig=True`，但文档备注写"需要支付签名与用户态签名"。不过文档 URL 示例中只有 `pay_sig` 没有 `signature`，文档本身存在矛盾 |

**问题详情：**
- `client.py:260` — 调用 `_http_post` 时未传 `needs_user_sig=True`
- 文档备注（第166行）："需要支付签名与用户态签名"
- 文档 URL（第137行）：仅包含 `pay_sig=xxx`，无 `signature=xxx`
- **建议：** 与微信官方文档确认是否需要用户态签名。文档URL和备注矛盾。

---

### 4. notify_provide_goods - 发货完成通知

**结果：❌ 高 — 返回模型不匹配**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | order_id(可选), wx_order_id(可选), env(自动) |
| 返回模型 `NotifyProvideGoodsResult` | ❌ | SDK 模型包含 order_id, out_trade_no, provide_status 三个字段，但文档返回值只有 errcode 和 errmsg |
| 签名类型 | ✅ | `needs_user_sig=False`，文档仅要求"支付签名" |

**问题详情：**
- `models.py:387-390` — `NotifyProvideGoodsResult` 定义了 `order_id`, `out_trade_no`, `provide_status` 三个字段
- API 文档（第193-196行）返回值仅有 `errcode` 和 `errmsg`
- **实际影响：** `_handle_response` 去掉 errcode/errmsg 后返回空字典，`NotifyProvideGoodsResult(**{})` 会因缺少必填字段而抛出 `TypeError`
- **建议：** 该接口应返回 `bool`（类似 `response_complaint`），或修改模型为无字段模型

---

### 5. present_currency - 代币赠送

**结果：✅ 一致**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | openid, env(自动), order_id, amount |
| 返回模型 `PresentCurrencyResult` | ✅ | balance, order_id, present_balance |
| 签名类型 | ✅ | URL 仅含 pay_sig |

---

### 6. query_order - 查询订单

**结果：❌ 严重 — 返回值解析错误**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | openid, env(自动), order_id(可选), wx_order_id(可选) |
| 返回模型 `Order` | ✅ | 所有字段匹配 |
| 返回值解析 | ❌ | 文档返回 `{"errcode":0, "errmsg":"", "order": {...}}`，但 SDK 直接 `Order(**response)`，实际应该是 `Order(**response["order"])` |
| 签名类型 | ✅ | 仅支付签名 |

**问题详情：**
- `client.py:318-319` — `return models.Order(**response)`
- `_handle_response` 去掉 errcode/errmsg 后得到 `{"order": {...}}`
- `Order(order={...})` 会抛出 `TypeError`，因为 Order 没有 `order` 字段
- 同样问题存在于 `async_client.py:322-323`
- **建议：** 改为 `models.Order(**response.get("order", {}))`

---

### 7. download_bill - 下载账单

**结果：✅ 一致**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | begin_ds, end_ds, env(自动) |
| 返回模型 `BillDownload` | ✅ | url |
| 签名类型 | ✅ | 仅支付签名 |

---

### 8. refund_order - 现金订单退款

**结果：⚠️ 中等问题**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | openid, refund_order_id, left_fee, refund_fee, refund_reason, req_from, order_id(可选), wx_order_id(可选), biz_meta(可选), env(自动) |
| 返回模型 `RefundOrderResult` | ✅ | refund_order_id, refund_wx_order_id, pay_order_id, pay_wx_order_id |
| 签名类型 | ⚠️ | SDK `needs_user_sig=False`，文档仅说"使用支付签名"，但文档 URL 也无 signature — 应该是正确的 |

**注意：** `refund_reason` 和 `req_from` 在文档中的类型是 `string`，SDK 中也是 `str`，一致 ✅

---

### 9. create_withdraw_order - 创建提现单

**结果：✅ 一致**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | withdraw_no, withdraw_amount(可选, string), env(自动) |
| 返回模型 `WithdrawOrderResult` | ✅ | withdraw_no, wx_withdraw_no |
| 签名类型 | ✅ | 仅支付签名 |

---

### 10. query_withdraw_order - 查询提现单

**结果：✅ 一致**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | withdraw_no, env(自动) |
| 返回模型 `WithdrawOrder` | ✅ | withdraw_no, status, withdraw_amount, wx_withdraw_no, withdraw_success_timestamp(可选), create_time(可选), fail_reason(可选) |
| 签名类型 | ✅ | 仅支付签名 |

---

### 11. start_upload_goods - 启动批量上传道具

**结果：❌ 高 — 请求参数名错误 + 返回值不匹配**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ❌ | SDK 使用 `{"goods": goods}`，文档要求 `{"upload_item": [...], "env": ...}` |
| 返回值 | ❌ | 文档仅返回 errcode 和 errmsg，SDK 却尝试解析 status 和 upload_item |
| 签名类型 | ✅ | 仅支付签名 |

**问题详情：**
- `client.py:694` — `payload = {"goods": goods}`，应为 `{"upload_item": goods}`
- `client.py:696-701` — 尝试从响应解析 status 和 upload_item，但文档只返回 errcode/errmsg
- 同样问题在 `async_client.py:710-719`
- **建议：** 参数名改为 `upload_item`，返回值改为 `bool`

---

### 12. query_upload_goods - 查询批量上传道具任务

**结果：✅ 一致**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | env(自动) |
| 返回模型 `GoodsUploadStatus` | ✅ | status, upload_item(含 GoodsUploadItem 列表) |
| 签名类型 | ✅ | 仅支付签名 |

---

### 13. start_publish_goods - 启动批量发布道具

**结果：❌ 高 — 请求参数名错误 + 返回值不匹配**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ❌ | SDK 使用 `{"goods": goods}`，文档要求 `{"publish_item": [...], "env": ...}` |
| 返回值 | ❌ | 文档仅返回 errcode 和 errmsg，SDK 却尝试解析 status 和 publish_item |
| 签名类型 | ✅ | 仅支付签名 |

**问题详情：**
- `client.py:740` — `payload = {"goods": goods}`，应为 `{"publish_item": goods}`
- `client.py:742-747` — 尝试从响应解析 status 和 publish_item，但文档只返回 errcode/errmsg
- 同样问题在 `async_client.py:760-769`
- **建议：** 参数名改为 `publish_item`，返回值改为 `bool`

---

### 14. query_publish_goods - 查询批量发布道具任务

**结果：✅ 一致**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | env(自动) |
| 返回模型 `GoodsPublishStatus` | ✅ | status, publish_item(含 GoodsPublishItem 列表) |
| 签名类型 | ✅ | 仅支付签名 |

---

### 15. query_biz_balance - 查询商家可提现余额

**结果：✅ 一致**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | env(自动) |
| 返回模型 `BizBalance` | ✅ | balance_available → BizBalanceAvailable(amount, currency_code) |
| 返回值解析 | ✅ | 正确处理嵌套 balance_available 对象 |
| 签名类型 | ✅ | 仅支付签名 |

---

### 16. query_transfer_account - 查询广告金充值账户

**结果：✅ 一致**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | env(自动) |
| 返回模型 `TransferAccount` | ✅ | transfer_account_name, transfer_account_uid, transfer_account_agency_id, transfer_account_agency_name, state, bind_result, error_msg(可选) |
| 返回值解析 | ✅ | 正确从 acct_list 中解析列表 |
| 签名类型 | ✅ | 仅支付签名 |

---

### 17. query_adver_funds - 查询广告金发放记录

**结果：❌ 高 — 缺少 filter 参数**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ❌ | SDK 缺少 `filter` 参数（settle_begin, settle_end, fund_type） |
| 返回模型 `AdverFundList` | ✅ | adver_funds_list, total_page |
| 签名类型 | ✅ | 仅支付签名 |

**问题详情：**
- `client.py:504-507` — payload 只有 page 和 page_size，缺少 filter 对象
- API 文档要求 filter 包含 settle_begin(int), settle_end(int), fund_type(int, 可选)
- **建议：** 添加 `settle_begin`, `settle_end`, `fund_type` 参数，构造 filter 对象

---

### 18. create_funds_bill - 充值广告金

**结果：❌ 高 — 请求参数不匹配**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ❌ | 多个参数不匹配 |
| 返回模型 `FundsBillResult` | ✅ | bill_id |
| 签名类型 | ✅ | 仅支付签名 |

**参数对比：**

| 文档参数 | 文档类型 | SDK 参数 | SDK 类型 | 状态 |
|----------|----------|----------|----------|------|
| transfer_amount | int | transfer_amount | int | ✅ |
| transfer_account_uid | int | transfer_account_uid | int | ✅ |
| transfer_account_name | string | — | — | ❌ 缺失 |
| transfer_account_agency_id | int | transfer_account_agency_id | int | ✅ |
| request_id | string | request_id | str \| None | ✅ |
| settle_begin | int | settle_begin | int | ✅ |
| settle_end | int | settle_end | int | ✅ |
| env | int | — | — | ✅ 自动添加 |
| authorize_advertise | int | — | — | ❌ 缺失 |
| fund_type | int | — | — | ❌ 缺失 |
| — | — | fund_id | str | ❌ 文档无此参数 |

**建议：** 添加缺失参数 `transfer_account_name`, `authorize_advertise`, `fund_type`；移除不存在的 `fund_id`

---

### 19. bind_transfer_account - 绑定广告金充值账户

**结果：❌ 严重 — 请求参数完全错误**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ❌ | SDK 参数与文档不匹配 |
| 返回值 | ✅ | 返回 bool（文档仅 errcode/errmsg） |
| 签名类型 | ✅ | 仅支付签名 |

**参数对比：**

| 文档参数 | 文档类型 | SDK 参数 | SDK 类型 | 状态 |
|----------|----------|----------|----------|------|
| transfer_account_uid | int | transfer_account_uid | int | ✅ |
| transfer_account_org_name | string | — | — | ❌ 缺失 |
| env | int | — | — | ✅ 自动添加 |
| — | — | transfer_account_agency_id | int | ❌ 文档无此参数 |

**问题详情：**
- `client.py:819-820` — SDK 使用 `transfer_account_agency_id`，文档要求 `transfer_account_org_name`
- **建议：** 将 `transfer_account_agency_id` 替换为 `transfer_account_org_name: str`

---

### 20. query_funds_bill - 查询广告金充值记录

**结果：❌ 高 — 缺少 filter 参数**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ❌ | SDK 缺少 `filter` 参数 |
| 返回模型 `FundsBillList` | ✅ | bill_list(FundsBillItem), total_page |
| 签名类型 | ✅ | 仅支付签名 |

**问题详情：**
- 文档要求 filter 对象包含 oper_time_begin(int), oper_time_end(int), bill_id(string, 可选), request_id(string, 可选)
- SDK `client.py:856-858` — payload 只有 page 和 page_size
- **建议：** 添加 filter 相关参数

---

### 21. query_recover_bill - 查询广告金回收记录

**结果：❌ 高 — 缺少 filter 参数**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ❌ | SDK 缺少 `filter` 参数 |
| 返回模型 `RecoverBillList` | ✅ | bill_list(RecoverBillItem), total_page |
| 签名类型 | ✅ | 仅支付签名 |

**问题详情：**
- 文档要求 filter 对象包含 recover_time_begin(int), recover_time_end(int), bill_id(string, 可选)
- SDK `client.py:883-885` — payload 只有 page 和 page_size
- **建议：** 添加 filter 相关参数

---

### 22. get_complaint_list - 获取投诉列表

**结果：✅ 一致**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | env(自动), begin_date, end_date, offset, limit |
| 返回模型 `ComplaintList` | ✅ | total, complaints(Complaint 列表) |
| Complaint 嵌套模型 | ✅ | 所有嵌套类型(ComplaintOrderInfo, ComplaintMedia, ServiceOrderInfo)均已定义 |
| 签名类型 | ✅ | 仅支付签名 |

---

### 23. get_complaint_detail - 获取投诉详情

**结果：✅ 一致**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | env(自动), complaint_id |
| 返回值解析 | ✅ | 正确从 `response.get("complaint", {})` 中提取 |
| 签名类型 | ✅ | 仅支付签名 |

---

### 24. get_negotiation_history - 获取协商历史

**结果：✅ 一致**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | env(自动), complaint_id, offset, limit |
| 返回模型 `NegotiationHistory` | ✅ | total, history(NegotiationRecord 列表) |
| 签名类型 | ✅ | 仅支付签名 |

---

### 25. response_complaint - 回复投诉

**结果：✅ 一致**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | env(自动), complaint_id, response_content, response_images(可选) |
| 返回值 | ✅ | 返回 bool（文档仅 errcode/errmsg） |
| 签名类型 | ✅ | 仅支付签名 |

---

### 26. complete_complaint - 完成投诉处理

**结果：✅ 一致**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | env(自动), complaint_id |
| 返回值 | ✅ | 返回 bool |
| 签名类型 | ✅ | 仅支付签名 |

---

### 27. upload_vp_file - 上传媒体文件

**结果：✅ 一致**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ✅ | env(自动), base64_img(可选), img_url(可选), file_name |
| 返回模型 `UploadFileResult` | ✅ | file_id |
| 签名类型 | ✅ | 仅支付签名 |

---

### 28. get_upload_file_sign - 获取上传文件签名

**结果：❌ 严重 — 请求参数完全错误**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ❌ | SDK 参数与文档完全不匹配 |
| 返回模型 `UploadFileSign` | ✅ | sign, cos_url(可选) |
| 签名类型 | ✅ | 仅支付签名 |

**参数对比：**

| 文档参数 | 文档类型 | SDK 参数 | SDK 类型 | 状态 |
|----------|----------|----------|----------|------|
| env | int | — | — | ✅ 自动添加 |
| wxpay_url | string | — | — | ❌ 缺失 |
| convert_cos | bool | — | — | ❌ 缺失 |
| complaint_id | string | — | — | ❌ 缺失 |
| — | — | file_name | str | ❌ 文档无此参数 |
| — | — | file_type | str | ❌ 文档无此参数 |

**问题详情：**
- `client.py:963-964` — SDK 使用 `file_name` 和 `file_type`，但文档要求 `wxpay_url`, `convert_cos`, `complaint_id`
- 此接口用于获取微信支付反馈投诉图片的签名头部，SDK 实现的功能与文档描述完全不同
- **建议：** 按文档重写，参数改为 `wxpay_url`, `convert_cos`, `complaint_id`

---

### 29. download_adverfunds_order - 下载广告金对应商户订单

**结果：❌ 严重 — 请求参数完全错误**

| 检查项 | 状态 | 说明 |
|--------|------|------|
| 请求参数 | ❌ | SDK 参数与文档完全不匹配 |
| 返回模型 `AdverfundsOrderDownload` | ✅ | url |
| 签名类型 | ✅ | 仅支付签名 |

**参数对比：**

| 文档参数 | 文档类型 | SDK 参数 | SDK 类型 | 状态 |
|----------|----------|----------|----------|------|
| fund_id | string | — | — | ❌ 缺失 |
| env | int | — | — | ✅ 自动添加 |
| — | — | begin_ds | int | ❌ 文档无此参数 |
| — | — | end_ds | int | ❌ 文档无此参数 |

**问题详情：**
- `client.py:897-898` / `async_client.py:927-928` — SDK 使用 `begin_ds` 和 `end_ds`（与 download_bill 相同），但文档要求 `fund_id`
- 此接口是下载指定广告金对应的商户订单，需要通过 fund_id 指定
- **建议：** 将参数改为 `fund_id: str`

---

## 模型一致性检查

### 模型字段完整性

| 模型 | 对应接口 | 状态 | 问题 |
|------|----------|------|------|
| `UserBalance` | query_user_balance | ✅ | — |
| `CurrencyPayResult` | currency_pay | ✅ | — |
| `CancelCurrencyPayResult` | cancel_currency_pay | ✅ | — |
| `Order` | query_order | ✅ | 字段完整，但客户端解析方式有 bug |
| `PresentCurrencyResult` | present_currency | ✅ | — |
| `BillDownload` | download_bill | ✅ | — |
| `RefundOrderResult` | refund_order | ✅ | — |
| `WithdrawOrderResult` | create_withdraw_order | ✅ | — |
| `WithdrawOrder` | query_withdraw_order | ✅ | — |
| `GoodsUploadItem` | query_upload_goods | ✅ | — |
| `GoodsUploadStatus` | query_upload_goods | ✅ | — |
| `GoodsPublishItem` | query_publish_goods | ✅ | — |
| `GoodsPublishStatus` | query_publish_goods | ✅ | — |
| `BizBalanceAvailable` | query_biz_balance | ✅ | — |
| `BizBalance` | query_biz_balance | ✅ | — |
| `TransferAccount` | query_transfer_account | ✅ | — |
| `AdverFund` | query_adver_funds | ✅ | — |
| `AdverFundList` | query_adver_funds | ✅ | — |
| `FundsBillResult` | create_funds_bill | ✅ | — |
| `FundsBillItem` | query_funds_bill | ✅ | — |
| `FundsBillList` | query_funds_bill | ✅ | — |
| `RecoverBillItem` | query_recover_bill | ✅ | — |
| `RecoverBillList` | query_recover_bill | ✅ | — |
| `ComplaintOrderInfo` | get_complaint_list | ✅ | — |
| `ComplaintMedia` | get_complaint_list | ✅ | — |
| `ServiceOrderInfo` | get_complaint_list | ✅ | — |
| `Complaint` | get_complaint_list/detail | ✅ | — |
| `ComplaintList` | get_complaint_list | ✅ | — |
| `NegotiationRecord` | get_negotiation_history | ✅ | — |
| `NegotiationHistory` | get_negotiation_history | ✅ | — |
| `UploadFileResult` | upload_vp_file | ✅ | — |
| `UploadFileSign` | get_upload_file_sign | ✅ | — |
| `NotifyProvideGoodsResult` | notify_provide_goods | ❌ | 文档无此返回结构 |
| `AdverfundsOrderDownload` | download_adverfunds_order | ✅ | — |

---

## 同步/异步客户端一致性

同步客户端 (`XPayClient`) 和异步客户端 (`XPayAsyncClient`) 的 API 方法签名和逻辑完全一致，仅区别在于 `async/await`。两者存在的问题完全相同。

---

## 问题汇总及修复优先级

### 严重（会导致运行时错误）

| # | 接口 | 问题 | 位置 |
|---|------|------|------|
| 1 | `query_order` | 返回值解析错误，应该从 `response["order"]` 取数据 | client.py:319, async_client.py:323 |
| 2 | `get_upload_file_sign` | 请求参数完全错误（file_name/file_type → wxpay_url/convert_cos/complaint_id） | client.py:976-978, async_client.py:1006-1008 |
| 3 | `download_adverfunds_order` | 请求参数完全错误（begin_ds/end_ds → fund_id） | client.py:910-912, async_client.py:940-942 |

### 高（功能缺失/参数错误）

| # | 接口 | 问题 | 位置 |
|---|------|------|------|
| 4 | `notify_provide_goods` | 返回模型包含文档不存在的字段，会导致 TypeError | models.py:387-390 |
| 5 | `start_upload_goods` | 参数名 `goods` 应为 `upload_item` | client.py:694, async_client.py:710 |
| 6 | `start_publish_goods` | 参数名 `goods` 应为 `publish_item` | client.py:740, async_client.py:760 |
| 7 | `bind_transfer_account` | 参数 `transfer_account_agency_id` 应为 `transfer_account_org_name` | client.py:819, async_client.py:845 |
| 8 | `create_funds_bill` | 缺少 transfer_account_name, authorize_advertise, fund_type；多了 fund_id | client.py:802-809, async_client.py:826-833 |
| 9 | `query_adver_funds` | 缺少 filter 参数 | client.py:504-507, async_client.py:512-514 |
| 10 | `query_funds_bill` | 缺少 filter 参数 | client.py:856-858, async_client.py:882-884 |
| 11 | `query_recover_bill` | 缺少 filter 参数 | client.py:883-885, async_client.py:911-913 |

### 中等（签名/逻辑）

| # | 接口 | 问题 | 位置 |
|---|------|------|------|
| 12 | `cancel_currency_pay` | 文档备注要求用户态签名但 URL 未包含，需确认 | client.py:260, async_client.py:260 |
