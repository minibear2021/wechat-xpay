"""日志功能使用示例。"""

import logging

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
        app_id="wx1234567890",
        app_key="your_app_key",
        env=0,  # 沙箱环境
        logger=logger,
    ) as client:
        try:
            # 查询用户余额
            balance = client.query_user_balance(
                openid="user_openid",
                session_key="user_session_key",
            )
            print(f"用户余额: {balance.balance}")

            # 查询订单
            order = client.query_order(
                openid="user_openid",
                session_key="user_session_key",
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
        app_id="wx1234567890",
        app_key="your_app_key",
        env=0,  # 沙箱环境
        logger=logger,
    ) as client:
        try:
            # 查询用户余额
            balance = await client.query_user_balance(
                openid="user_openid",
                session_key="user_session_key",
            )
            print(f"用户余额: {balance.balance}")

            # 查询订单
            order = await client.query_order(
                openid="user_openid",
                session_key="user_session_key",
                order_id="order_123",
            )
            print(f"订单状态: {order.status}")

        except Exception as e:
            logger.exception("API 调用失败")
            print(f"错误: {e}")


def example_without_logging():
    """不使用日志的示例（默认行为）。"""
    with XPayClient(
        app_id="wx1234567890",
        app_key="your_app_key",
        env=0,
    ) as client:
        # 不传入 logger 参数，不会记录任何日志
        balance = client.query_user_balance(
            openid="user_openid",
            session_key="user_session_key",
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
