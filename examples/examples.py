"""日志功能使用示例。"""

import logging

from config import ACCESS_TOKEN, APP_SECRET, APPID, ENV, OPENID, SESSION_KEY, USER_IP
from wechat_xpay import XPayAsyncClient, XPayClient


def setup_logger() -> logging.Logger:
    """配置日志记录器。"""
    logger = logging.getLogger("wechat_xpay")
    logger.setLevel(logging.DEBUG)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # 文件处理器
    file_handler = logging.FileHandler("xpay.log", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    # 格式化器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def sync_example_with_logging():
    """同步客户端使用日志示例。"""
    logger = setup_logger()

    with XPayClient(
        app_id=APPID,
        app_key=APP_SECRET,
        env=ENV,
        logger=logger,
    ) as client:
        try:
            # 查询用户余额
            balance = client.query_user_balance(
                openid=OPENID, access_token=ACCESS_TOKEN, session_key=SESSION_KEY, user_ip=USER_IP
            )
            print(f"用户余额: {balance.balance}")

            # 查询商户余额
            biz_balance = client.query_biz_balance(
                access_token=ACCESS_TOKEN,
                session_key=SESSION_KEY
            )
            print(f"商户余额: {biz_balance.balance_available}")

            # 查询广告资金列表
            adver_funds_list = client.query_adver_funds(
                access_token=ACCESS_TOKEN,
                session_key=SESSION_KEY
            )
            print("广告资金列表:")
            for adver_funds in adver_funds_list.adver_funds_list:
                print(f"  - 广告ID: {adver_funds.fund_id}, 可用余额: {adver_funds.remain_amount}")

            # 查询订单
            order = client.query_order(
                openid=OPENID,
                access_token=ACCESS_TOKEN,
                session_key=SESSION_KEY,
                order_id="order_123",
            )
            print(f"订单状态: {order.status}")

        except Exception as e:
            logger.exception("API 调用失败")
            print(f"错误: {e}")


async def async_example_with_logging():
    """异步客户端使用日志示例。"""
    logger = setup_logger()

    async with XPayAsyncClient(
        app_id=APPID,
        app_key=APP_SECRET,
        env=ENV,
        logger=logger,
    ) as client:
        try:
            # 查询用户余额
            balance = await client.query_user_balance(
                openid=OPENID,
                access_token=ACCESS_TOKEN,
                session_key=SESSION_KEY,
            )
            print(f"用户余额: {balance.balance}")

            # 查询商户余额
            biz_balance = await client.query_biz_balance(
                access_token=ACCESS_TOKEN,
                session_key=SESSION_KEY
            )
            print(f"商户余额: {biz_balance.balance_available}")

            # 查询广告资金列表
            adver_funds_list = await client.query_adver_funds(
                access_token=ACCESS_TOKEN,
                session_key=SESSION_KEY
            )
            print("广告资金列表:")
            for adver_funds in adver_funds_list.adver_funds_list:
                print(f"  - 广告ID: {adver_funds.fund_id}, 可用余额: {adver_funds.remain_amount}")

            # 查询订单
            order = await client.query_order(
                openid=OPENID,
                access_token=ACCESS_TOKEN,
                session_key=SESSION_KEY,
                order_id="order_123",
            )
            print(f"订单状态: {order.status}")

        except Exception as e:
            logger.exception("API 调用失败")
            print(f"错误: {e}")


def example_without_logging():
    """不使用日志的示例（默认行为）。"""
    with XPayClient(
        app_id=APPID,
        app_key=APP_SECRET,
        env=ENV,
    ) as client:
        # 不传入 logger 参数，不会记录任何日志
        balance = client.query_user_balance(
            openid=OPENID,
            access_token=ACCESS_TOKEN,
            session_key=SESSION_KEY,
        )
        print(f"用户余额: {balance.balance}")


if __name__ == "__main__":
    print("=== 同步客户端日志示例 ===")
    sync_example_with_logging()

    print("\n=== 异步客户端日志示例 ===")
    import asyncio

    asyncio.run(async_example_with_logging())

    print("\n=== 不使用日志示例 ===")
    example_without_logging()
