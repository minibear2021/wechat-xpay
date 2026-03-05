# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目目标

本项目是微信小程序虚拟支付（WeChatPay Virtual Payment）的 Python SDK，基于 `docs/apis.txt` 中描述的服务器端 API，简化服务器端接入虚拟支付及接收推送消息的流程。

## API 核心概念

### 签名体系

API 涉及两种签名，必须正确区分：

1. **支付签名（pay_sig）**：加在 URL query 参数中
   ```
   paySig = HMAC-SHA256(appKey, uri + '&' + post_body).hexdigest()
   ```
   - `uri` 为路径部分，不含 query string，如 `/xpay/query_user_balance`
   - `post_body` 为请求 body 的原始字符串（必须与实际发送完全一致）
   - `appKey` 根据 `env` 参数选择：`env=0` 用现网 AppKey，`env=1` 用沙箱 AppKey

2. **用户态签名（signature）**：加在 URL query 参数中
   ```
   signature = HMAC-SHA256(session_key, post_body).hexdigest()
   ```
   - `session_key` 为当前用户有效的 session_key（来自 `auth.code2Session`）

### 接口签名要求

- 仅需 **支付签名**：`query_order`、`notify_provide_goods`、`present_currency`、`download_bill`、`refund_order`、`create_withdraw_order`、`query_withdraw_order`、`start_upload_goods`、`query_upload_goods`、`start_publish_goods`、`query_publish_goods`、`query_biz_balance`、`query_transfer_account`、`query_adver_funds`、`create_funds_bill`、`bind_transfer_accout`、`query_funds_bill`、`query_recover_bill`、`get_complaint_list`、`get_complaint_detail`、`get_negotiation_history`、`response_complaint`、`complete_complaint`、`upload_vp_file`、`get_upload_file_sign`、`download_adverfunds_order`
- 需要**两种签名**（支付签名 + 用户态签名）：`query_user_balance`、`currency_pay`、`cancel_currency_pay`

### 错误码

API 统一返回 `errcode` 和 `errmsg`，关键错误码：
- `0`：成功
- `-1`：系统错误
- `268490003`：签名错误
- `268490004`：重复操作（幂等请求可安全忽略）
- `268490009`：session_key 过期

## API 接口分类

### 代币操作
- `query_user_balance` - 查询用户代币余额
- `currency_pay` - 扣减代币
- `cancel_currency_pay` - 代币退款
- `present_currency` - 赠送代币（可重试至成功或 268490004）

### 订单管理
- `query_order` - 查询现金订单（含退款单状态流转）
- `refund_order` - 发起退款（异步，需轮询 `query_order` 确认）
- `notify_provide_goods` - 手动通知发货完成（异常补偿用）

### 提现
- `query_biz_balance` - 查询可提现余额
- `create_withdraw_order` - 创建提现单
- `query_withdraw_order` - 查询提现单

### 道具管理
- `start_upload_goods` / `query_upload_goods` - 批量上传道具（异步，需轮询）
- `start_publish_goods` / `query_publish_goods` - 批量发布道具（异步，需轮询）

### 广告金
- `query_transfer_account` / `bind_transfer_accout` - 充值账户管理
- `query_adver_funds` - 查询广告金发放记录
- `create_funds_bill` - 充值广告金
- `query_funds_bill` / `query_recover_bill` - 充值/回收记录查询
- `download_adverfunds_order` - 下载广告金对应订单

### 投诉处理
- `get_complaint_list` / `get_complaint_detail` - 获取投诉列表/详情
- `get_negotiation_history` - 获取协商历史
- `response_complaint` - 回复用户
- `complete_complaint` - 完成投诉处理
- `upload_vp_file` / `get_upload_file_sign` - 媒体文件上传

### 账单
- `download_bill` - 下载账单（异步，首次触发生成，可轮询获取 URL）

## 消息推送处理

微信服务器推送的事件类型（需在 SDK 中解析并回调）：

| 事件 Event 字段 | 说明 |
|---|---|
| `xpay_goods_deliver_notify` | 道具发货通知（需返回发货结果） |
| `xpay_coin_pay_notify` | 代币支付通知 |
| `xpay_refund_notify` | 退款结果通知 |
| `xpay_complaint_notify` | 用户投诉通知 |

推送响应格式（失败则微信最多重试 15 次，间隔为 2/4/8/16...秒）：
- JSON 格式推送 → 响应 `{"ErrCode": 0, "ErrMsg": "success"}`
- XML 格式推送 → 响应对应 XML
- 响应空或 `success` 也视为成功

## 实现注意事项

1. **post_body 一致性**：签名计算所用的 post_body 字符串必须与实际 HTTP 请求发送的 body 完全一致（含空格、字段顺序），建议先序列化再签名
2. **env 参数**：每个请求都必须传入 `env`（0=正式，1=沙箱），并据此选择对应 AppKey
3. **幂等重试**：`present_currency`、`create_funds_bill` 等接口可安全重试至 `errcode=0` 或 `268490004`
4. **异步接口**：`download_bill`、`start_upload_goods`、`start_publish_goods`、`download_adverfunds_order`、`refund_order` 均为异步，需轮询确认结果
