# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.1] - 2026-03-12

### Added
- `CallbackResult` 新增 `content_type` 属性，根据请求格式自动返回 `application/json` 或 `application/xml`，避免在框架层硬编码 MIME 类型

## [0.5.0] - 2026-03-12

### Added
- 新增 `CallbackResult` 类，作为 `callback()` 的返回结果
  - 将解析后的通知对象与 `success_response()` / `fail_response()` 绑定在同一实例
  - 每次 `callback()` 调用创建独立实例，并发环境下不存在格式状态竞争
  - 自动识别请求格式（JSON / XML），应答格式与请求保持一致
- 新增 `WebhookParser.callback(body)` 统一回调处理入口
  - 支持 `str` 或 `bytes` 输入（可直接传入 Flask `request.data`）
  - 自动识别 JSON 和 XML 格式（以 `<` 开头视为 XML，否则视为 JSON）
- 新增 `examples/examples.py`，包含完整的 API 调用和 Webhook 回调处理示例

### Changed
- README Webhook 章节更新为基于 `callback()` 的 Flask 集成示例

## [0.4.1] - 2026-03-11

### Added
- `calc_pay_sig` 和 `calc_signature` 已在包级别导出，可直接用于计算前端 `wx.requestVirtualPayment` 所需的签名参数

### Changed
- 签名函数参数 `post_body` 统一重命名为 `signData`，与微信官方 API 文档保持一致
  - `calc_pay_sig(uri, signData, appkey)`
  - `calc_signature(signData, session_key)`

### Fixed
- 修复 CI ruff / mypy 检查问题（`N803` 命名规范、类型注解补全）
- 将 `examples/` 目录加入 ruff 排除列表，解决本地与 CI 环境 isort 分组不一致的问题

### Documentation
- README 新增签名工具函数使用说明及前端签名计算示例

## [0.4.0] - 2026-03-10

### Added
- 所有 API 接口新增 `access_token` 参数，在每次调用时传入而非客户端初始化时绑定，支持令牌到期后的灵活更新和多用户复用同一客户端实例

### Fixed
- 修正 API 基础 URL 为 `https://api.weixin.qq.com`（原为错误的 `api.xpay.weixin.qq.com`）
- 修正签名计算中 JSON 序列化格式：使用 Python 默认格式（字段间含空格），与微信服务器验签逻辑保持一致
- 移除请求体中多余的 `appid` 字段（该字段不在微信 XPay API 规范内）
- 仅 `query_user_balance` 和 `currency_pay` 接口附加用户态 `signature`，其他接口不再错误附加

### Documentation
- README 更新，说明 `access_token` 和 `session_key` 均为每次调用时传入的参数及其原因

## [0.3.0] - 2026-03-10

### Added
- 可选的日志支持功能
  - 在客户端初始化时可传入 `logger` 参数
  - 记录 API 请求信息（端点、URL、参数）
  - 记录 API 响应信息（成功和错误）
  - 不记录敏感的签名信息
  - 完全向后兼容，不传入 logger 时不会记录日志
- 新增 `examples/logging_example.py` 示例文件
- 新增 5 个日志功能测试用例

### Changed
- 改进 GitHub Actions 发布流程
  - 先发布到 TestPyPI 进行验证
  - 测试从 TestPyPI 安装
  - 验证通过后才发布到正式 PyPI

### Documentation
- README 新增日志功能使用文档
- 添加日志配置和使用示例

## [0.2.0] - 2026-03-10

### Added
- 实现了所有 29 个微信 XPay API 端点（100% 覆盖）
  - 用户代币管理（4个）
  - 订单管理（2个）
  - 退款与提现（4个）
  - 商家余额与广告金（8个）
  - 道具管理（4个）
  - 投诉管理（6个）
  - 文件上传（1个）

### Changed
- **重大变更**：修正 API 参数命名以匹配官方文档
  - `currency_pay`: `out_trade_no` → `order_id`, `order_fee` → `amount`, `pay_item` → `payitem`
  - `cancel_currency_pay`: `order_fee` → `amount`
  - `present_currency`: `pay_present` → `amount`
  - `query_user_balance`: 新增 `user_ip` 可选参数
  - `query_order`: 移除 `out_trade_no`，使用 `order_id` 或 `wx_order_id`
  - `refund_order`: 移除 `out_trade_no`，使用 `order_id` 或 `wx_order_id`
  - `notify_provide_goods`: 简化参数为 `order_id` 或 `wx_order_id`

### Fixed
- 修复所有代码质量检查问题
  - Black 格式化（Python 3.12 兼容）
  - Ruff linting（158 个问题）
  - Mypy 类型检查（2 个错误）
- 现代化类型注解（`Optional[X]` → `X | None`, `List[X]` → `list[X]`）
- 修复导入排序问题

### Documentation
- 更新 README.md 示例代码
- 更新 examples/basic_usage.py
- 所有测试用例已更新（51 个测试全部通过）

## [0.1.0] - 2026-03-09

### Added
- 初始版本发布
- 基础 XPay 客户端实现
- 同步和异步客户端支持
- 基础 API 端点实现
