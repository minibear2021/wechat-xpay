# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
