# 服务器 API 文档

## 签名方法

### 用户态签名

签名参数为 `signature`，加在 query 后面。

**示例：**
- 原接口地址：`https://api.weixin.qq.com/xpay/query_user_balance?access_token=xxxx`
- 加上签名后：`https://api.weixin.qq.com/xpay/query_user_balance?access_token=xxxx&signature=xxx`

### 支付签名

签名参数为 `pay_sig`，加在 query 后面。

**示例：**
- 原接口地址：`https://api.weixin.qq.com/xpay/query_user_balance?access_token=xxxx`
- 加上签名后：`https://api.weixin.qq.com/xpay/query_user_balance?access_token=xxxx&pay_sig=xxx`

## 错误码

| 错误码 | 描述 |
|--------|------|
| -1 | 系统错误 |
| 268490001 | openid错误 |
| 268490002 | 请求参数字段错误，具体看errmsg |
| 268490003 | 签名错误 |
| 268490004 | 重复操作（赠送和代币支付和充值广告金相关接口会返回，表示之前的操作已经成功） |
| 268490005 | 订单已经通过cancel_currency_pay接口退款，不支持再退款 |
| 268490006 | 代币的退款/支付操作金额不足 |
| 268490007 | 图片或文字存在敏感内容，禁止使用 |
| 268490008 | 代币未发布，不允许进行代币操作 |
| 268490009 | 用户session_key不存在或已过期，请重新登录 |
| 268490011 | 数据生成中，请稍后调用本接口获取 |
| 268490012 | 批量任务运行中，请等待完成后才能再次运行 |
| 268490013 | 禁止对核销状态的单进行退款 |
| 268490014 | 退款操作进行中，稍后可以使用相同参数重试 |
| 268490015 | 频率限制 |
| 268490016 | 退款的left_fee字段与实际不符，请通过query_order接口查询确认 |
| 268490018 | 广告金充值帐户行业 id 不匹配 |
| 268490019 | 广告金充值帐户 id已绑定其他 appid |
| 268490020 | 广告金充值帐户主体名称错误 |
| 268490021 | 账户未完成进件 |
| 268490022 | 广告金充值账户无效 |
| 268490023 | 广告金余额不足 |
| 268490024 | 广告金充值金额必须大于 0 |

---

## API 接口

### query_user_balance

**地址：**
```
https://api.weixin.qq.com/xpay/query_user_balance?access_token=xxx&pay_sig=xxx
```

**描述：**
查询用户代币余额

**请求方法：**
POST，请求参数为 JSON 字符串，Content-Type 为 application/json

**请求参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| openid | string | 用户的openid |
| env | int | 0-正式环境 1-沙箱环境 |
| user_ip | string | 用户ip，例如:1.1.1.1 |

**返回参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | int | 错误码 |
| errmsg | string | 错误信息 |
| balance | int | 代币总余额，包括有价和赠送部分 |
| present_balance | int | 赠送账户的代币余额 |
| sum_save | int | 累计有价货币充值数量 |
| sum_present | int | 累计赠送无价货币数量 |
| sum_balance | int | 历史总增加的代币金额 |
| sum_cost | int | 历史总消耗代币金额 |
| first_save_flag | bool | 是否满足首充活动标记。0:不满足。1:满足 |

**备注：**
1. 需要用户态签名与支付签名

---

### currency_pay

**地址：**
```
https://api.weixin.qq.com/xpay/currency_pay?access_token=xxx&pay_sig=xxx&signature=xxx
```

**描述：**
扣减代币（一般用于代币支付）

**请求方法：**
POST，请求参数为 JSON 字符串，Content-Type 为 application/json

**请求参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| openid | string | 用户的openid |
| env | int | 0-正式环境 1-沙箱环境 |
| user_ip | string | 用户ip，例如:1.1.1.1 |
| amount | int | 支付的代币数量 |
| order_id | string | 订单号 |
| payitem | string | 物品信息。记录到账户流水中。如:[{"productid":"物品id", "unit_price": 单价, "quantity": 数量}] |
| remark | string | 备注 |
| device_type | string | 设备类型，安卓：android，苹果：ios |
| platform | string | 平台，安卓：android，苹果：ios |

**返回参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | int | 错误码 |
| errmsg | string | 错误信息 |
| balance | int | 代币总余额，包括有价和赠送部分 |
| used_present_amount | int | 本次使用的赠送代币数量 |
| used_gen_amount | int | 本次使用的有价代币数量 |
| order_id | string | 订单号 |
| bill_no | string | 平台单号 |

**备注：**
1. 需要用户态签名与支付签名
2. order_id 需要保证唯一性，重复的 order_id 会返回 268490004 错误码

---

### cancel_currency_pay

**地址：**
```
https://api.weixin.qq.com/xpay/cancel_currency_pay?access_token=xxx&pay_sig=xxx
```

**描述：**
取消代币支付（一般用于退款）

**请求方法：**
POST，请求参数为 JSON 字符串，Content-Type 为 application/json

**请求参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| openid | string | 用户的openid |
| env | int | 0-正式环境 1-沙箱环境 |
| user_ip | string | 用户ip，例如:1.1.1.1 |
| order_id | string | 订单号 |
| refund_order_id | string | 退款订单号 |
| payitem | string | 物品信息。记录到账户流水中。如:[{"productid":"物品id", "unit_price": 单价, "quantity": 数量}] |
| remark | string | 备注 |

**返回参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | int | 错误码 |
| errmsg | string | 错误信息 |
| balance | int | 代币总余额，包括有价和赠送部分 |
| refund_order_id | string | 退款订单号 |
| bill_no | string | 平台单号 |

**备注：**
1. 需要支付签名
2. refund_order_id 需要保证唯一性，重复的 refund_order_id 会返回 268490004 错误码

---

### present_currency

**地址：**
```
https://api.weixin.qq.com/xpay/present_currency?access_token=xxx&pay_sig=xxx
```

**描述：**
赠送代币

**请求方法：**
POST，请求参数为 JSON 字符串，Content-Type 为 application/json

**请求参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| openid | string | 用户的openid |
| env | int | 0-正式环境 1-沙箱环境 |
| user_ip | string | 用户ip，例如:1.1.1.1 |
| present_counts | int | 赠送的代币数量 |
| bill_no | string | 单号 |
| payitem | string | 物品信息。记录到账户流水中。如:[{"productid":"物品id", "unit_price": 单价, "quantity": 数量}] |
| remark | string | 备注 |

**返回参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | int | 错误码 |
| errmsg | string | 错误信息 |
| balance | int | 代币总余额，包括有价和赠送部分 |
| bill_no | string | 单号 |

**备注：**
1. 需要支付签名
2. bill_no 需要保证唯一性，重复的 bill_no 会返回 268490004 错误码

---

### query_order

**地址：**
```
https://api.weixin.qq.com/xpay/query_order?access_token=xxx&pay_sig=xxx
```

**描述：**
查询订单

**请求方法：**
POST，请求参数为 JSON 字符串，Content-Type 为 application/json

**请求参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| openid | string | 用户的openid |
| env | int | 0-正式环境 1-沙箱环境 |
| user_ip | string | 用户ip，例如:1.1.1.1 |
| order_id | string | 订单号 |

**返回参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | int | 错误码 |
| errmsg | string | 错误信息 |
| order_id | string | 订单号 |
| status | int | 订单状态。0:未支付 1:已支付 2:已退款 |
| create_time | int | 订单创建时间戳 |
| pay_time | int | 订单支付时间戳 |
| refund_time | int | 订单退款时间戳 |
| total_fee | int | 订单总金额 |
| refund_fee | int | 订单退款金额 |
| left_fee | int | 订单剩余金额 |

**备注：**
1. 需要支付签名

---

### provide_currency

**地址：**
```
https://api.weixin.qq.com/xpay/provide_currency?access_token=xxx&pay_sig=xxx
```

**描述：**
发放代币（用于补偿等场景）

**请求方法：**
POST，请求参数为 JSON 字符串，Content-Type 为 application/json

**请求参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| openid | string | 用户的openid |
| env | int | 0-正式环境 1-沙箱环境 |
| user_ip | string | 用户ip，例如:1.1.1.1 |
| amount | int | 发放的代币数量 |
| bill_no | string | 单号 |
| payitem | string | 物品信息。记录到账户流水中。如:[{"productid":"物品id", "unit_price": 单价, "quantity": 数量}] |
| remark | string | 备注 |

**返回参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | int | 错误码 |
| errmsg | string | 错误信息 |
| balance | int | 代币总余额，包括有价和赠送部分 |
| bill_no | string | 单号 |

**备注：**
1. 需要支付签名
2. bill_no 需要保证唯一性，重复的 bill_no 会返回 268490004 错误码

---

### download_bill

**地址：**
```
https://api.weixin.qq.com/xpay/download_bill?access_token=xxx&pay_sig=xxx
```

**描述：**
下载账单

**请求方法：**
POST，请求参数为 JSON 字符串，Content-Type 为 application/json

**请求参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| env | int | 0-正式环境 1-沙箱环境 |
| begin_ds | string | 开始日期，格式：20210101 |
| end_ds | string | 结束日期，格式：20210101 |

**返回参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | int | 错误码 |
| errmsg | string | 错误信息 |
| download_url | string | 下载地址 |

**备注：**
1. 需要支付签名
2. 下载地址有效期为 1 小时

---

### refund_currency_pay

**地址：**
```
https://api.weixin.qq.com/xpay/refund_currency_pay?access_token=xxx&pay_sig=xxx
```

**描述：**
部分退款

**请求方法：**
POST，请求参数为 JSON 字符串，Content-Type 为 application/json

**请求参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| openid | string | 用户的openid |
| env | int | 0-正式环境 1-沙箱环境 |
| user_ip | string | 用户ip，例如:1.1.1.1 |
| order_id | string | 订单号 |
| refund_order_id | string | 退款订单号 |
| refund_amount | int | 退款金额 |
| left_fee | int | 订单剩余金额（用于校验） |
| payitem | string | 物品信息。记录到账户流水中。如:[{"productid":"物品id", "unit_price": 单价, "quantity": 数量}] |
| remark | string | 备注 |

**返回参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | int | 错误码 |
| errmsg | string | 错误信息 |
| balance | int | 代币总余额，包括有价和赠送部分 |
| refund_order_id | string | 退款订单号 |
| bill_no | string | 平台单号 |

**备注：**
1. 需要支付签名
2. refund_order_id 需要保证唯一性，重复的 refund_order_id 会返回 268490004 错误码
3. left_fee 用于校验订单剩余金额，如果不匹配会返回 268490016 错误码

---

### start_upload_goods

**地址：**
```
https://api.weixin.qq.com/xpay/start_upload_goods?access_token=xxx&pay_sig=xxx
```

**描述：**
开始上传商品

**请求方法：**
POST，请求参数为 JSON 字符串，Content-Type 为 application/json

**请求参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| env | int | 0-正式环境 1-沙箱环境 |
| upload_type | int | 上传类型。1:全量上传 2:增量上传 |

**返回参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | int | 错误码 |
| errmsg | string | 错误信息 |
| upload_batch | string | 上传批次号 |

**备注：**
1. 需要支付签名

---

### upload_goods

**地址：**
```
https://api.weixin.qq.com/xpay/upload_goods?access_token=xxx&pay_sig=xxx
```

**描述：**
上传商品

**请求方法：**
POST，请求参数为 JSON 字符串，Content-Type 为 application/json

**请求参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| env | int | 0-正式环境 1-沙箱环境 |
| upload_batch | string | 上传批次号 |
| upload_item | array | 商品列表 |

**upload_item 字段说明：**

| 字段 | 类型 | 说明 |
|------|------|------|
| item_code | string | 商品编码 |
| item_name | string | 商品名称 |
| item_price | int | 商品价格（单位：代币） |
| item_url | string | 商品图片url |
| item_desc | string | 商品描述 |

**返回参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | int | 错误码 |
| errmsg | string | 错误信息 |

**备注：**
1. 需要支付签名
2. 每次最多上传 200 个商品

---

### publish_goods

**地址：**
```
https://api.weixin.qq.com/xpay/publish_goods?access_token=xxx&pay_sig=xxx
```

**描述：**
发布商品

**请求方法：**
POST，请求参数为 JSON 字符串，Content-Type 为 application/json

**请求参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| env | int | 0-正式环境 1-沙箱环境 |
| upload_batch | string | 上传批次号 |

**返回参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | int | 错误码 |
| errmsg | string | 错误信息 |

**备注：**
1. 需要支付签名

---

### query_upload_goods_status

**地址：**
```
https://api.weixin.qq.com/xpay/query_upload_goods_status?access_token=xxx&pay_sig=xxx
```

**描述：**
查询商品上传状态

**请求方法：**
POST，请求参数为 JSON 字符串，Content-Type 为 application/json

**请求参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| env | int | 0-正式环境 1-沙箱环境 |
| upload_batch | string | 上传批次号 |

**返回参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | int | 错误码 |
| errmsg | string | 错误信息 |
| status | int | 状态。0:上传中 1:上传完成 2:发布中 3:发布完成 |

**备注：**
1. 需要支付签名

---

### notify_provide_currency

**地址：**
```
https://api.weixin.qq.com/xpay/notify_provide_currency?access_token=xxx&pay_sig=xxx
```

**描述：**
通知发放代币（用于广告金充值）

**请求方法：**
POST，请求参数为 JSON 字符串，Content-Type 为 application/json

**请求参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| openid | string | 用户的openid |
| env | int | 0-正式环境 1-沙箱环境 |
| user_ip | string | 用户ip，例如:1.1.1.1 |
| amount | int | 发放的代币数量 |
| bill_no | string | 单号 |
| wecoin_bill_no | string | 微信代币单号 |
| ts | int | 时间戳 |
| payitem | string | 物品信息。记录到账户流水中。如:[{"productid":"物品id", "unit_price": 单价, "quantity": 数量}] |
| remark | string | 备注 |
| ad_account_id | string | 广告账户id |
| ad_industry_id | int | 广告行业id |
| ad_account_name | string | 广告账户名称 |

**返回参数：**

| 字段 | 类型 | 说明 |
|------|------|------|
| errcode | int | 错误码 |
| errmsg | string | 错误信息 |
| balance | int | 代币总余额，包括有价和赠送部分 |
| bill_no | string | 单号 |

**备注：**
1. 需要支付签名
2. bill_no 需要保证唯一性，重复的 bill_no 会返回 268490004 错误码

---

## 代码示例

### Python 示例

```python
import hashlib
import hmac
import json

def calc_pay_sig(uri, post_body, appkey):
    """
    计算支付签名

    Args:
        uri: 请求的URI（不包含参数）
        post_body: POST请求体
        appkey: 应用密钥

    Returns:
        签名字符串
    """
    # 拼接签名字符串
    sign_str = uri + "&" + post_body

    # 使用HMAC-SHA256算法计算签名
    signature = hmac.new(
        appkey.encode('utf-8'),
        sign_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return signature

def calc_signature(post_body, session_key):
    """
    计算用户态签名

    Args:
        post_body: POST请求体
        session_key: 用户会话密钥

    Returns:
        签名字符串
    """
    # 使用HMAC-SHA256算法计算签名
    signature = hmac.new(
        session_key.encode('utf-8'),
        post_body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return signature

# 示例使用
if __name__ == "__main__":
    # 示例参数
    uri = "/xpay/query_user_balance"
    appkey = "test_appkey_123456"

    # 注意：JSON数据序列化结果，不同语言/版本结果可能不同
    # 所以示例为了保证稳定性，直接用其中一个序列化的版本
    # 实际使用时只需要保证，参与签名的post_body和真正发起http请求的一致即可

    # 不同接口要求的Post Body参数不一样，此处以query_user_balance接口为例(和uri对应）
    post_body = json.dumps({
        "openid": "xxx",
        "user_ip": "127.0.0.1",
        "env": 0
    })

    post_body = '{"openid": "xxx", "user_ip": "127.0.0.1", "env": 0}'

    # step1. pay_sig签名计算（支付请求签名算法）
    pay_sig = calc_pay_sig(uri, post_body, appkey)
    print("pay_sig:", pay_sig)

    # 若实际请求返回pay_sig签名不对，根据以下步骤排查：
    # 1. 确认算法：uri、post_body、appkey写死以上参数，确保你的签名算法和示例calc_pay_sig结果完全一致
    # 2. 确认参数：
    #    - uri不可带参数（即"?"及后续部分全部舍去）
    #    - post_body必须和真正发起HTTP请求的post body完全一致
    #    - appkey必须是与请求中对应的环境匹配（env参数决定）
    assert pay_sig == "c37809f27c6d7fd1837ad2500a04512b66b34fd793a39a385fade56dca89a4b5"

    # step2. signature签名计算（用户登录态签名算法）
    # session_key需要为当前用户有效session_key（参考auth.code2Session接口获取）
    # 此处写死方便复现算法
    session_key = "9hAb/NEYUlkaMBEsmFgzig=="
    signature = calc_signature(post_body, session_key)
    print("signature:", signature)

    # 若实际请求返回signature签名不对，参考随后的"90010-signature签名错误问题排查思路"进行排查
    assert signature == "089d9e8dc5d308977360c4b79ec600a93d736802802a807d634192328032f6c7"
```

### 签名排查说明

#### pay_sig 签名错误排查

1. **确认算法**：使用示例中的固定参数（uri、post_body、appkey），确保你的签名算法和示例 `calc_pay_sig` 结果完全一致
2. **确认参数**：
   - uri 不可带参数（即 "?" 及后续部分全部舍去）
   - post_body 必须和真正发起 HTTP 请求的 post body 完全一致
   - appkey 必须是与请求中对应的环境匹配（env 参数决定）

#### signature 签名错误排查

1. 确保 post_body 和真正发起 HTTP 请求的 post body 完全一致
2. 确保 session_key 是当前用户有效的 session_key（参考 auth.code2Session 接口获取）
3. 使用示例中的固定参数验证签名算法是否正确

---

## 注意事项

1. 所有接口都需要在 query 参数中传入 `access_token`
2. 需要支付签名的接口，需要在 query 参数中传入 `pay_sig`
3. 需要用户态签名的接口，需要在 query 参数中传入 `signature`
4. 所有金额单位均为代币
5. 订单号（order_id）、退款订单号（refund_order_id）、单号（bill_no）需要保证唯一性
6. JSON 序列化结果在不同语言/版本中可能不同，需要确保参与签名的 post_body 和真正发起 HTTP 请求的一致
7. 环境参数（env）：0-正式环境，1-沙箱环境
