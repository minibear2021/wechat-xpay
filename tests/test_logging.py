"""测试日志功能。"""

import logging
from io import StringIO

import pytest
import respx
from httpx import Response

from wechat_xpay import XPayAsyncClient, XPayClient
from wechat_xpay.exceptions import XPayAPIError


class TestLogging:
    """测试日志功能。"""

    def test_sync_client_with_logger(self):
        """测试同步客户端使用 logger。"""
        # 创建内存日志处理器
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        logger = logging.getLogger("test_sync")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        with respx.mock:
            respx.post("https://api.weixin.qq.com/xpay/query_user_balance").mock(
                return_value=Response(
                    200,
                    json={
                        "errcode": 0,
                        "errmsg": "ok",
                        "balance": 1000,
                        "present_balance": 200,
                        "sum_save": 800,
                        "sum_present": 200,
                        "sum_balance": 1000,
                        "sum_cost": 500,
                        "first_save_flag": True,
                    },
                )
            )

            client = XPayClient(
                app_id="wx123",
                app_key="test_key",
                env=1,
                logger=logger,
            )

            client.query_user_balance(
                openid="user_123",
                access_token="test_access_token",
                session_key="session_key_456",
            )

            client.close()

        # 验证日志内容
        log_output = log_stream.getvalue()
        assert "XPay API Request" in log_output
        assert "XPay API Response: Success" in log_output
        assert "/xpay/query_user_balance" in log_output

    def test_sync_client_without_logger(self):
        """测试同步客户端不使用 logger。"""
        with respx.mock:
            respx.post("https://api.weixin.qq.com/xpay/query_user_balance").mock(
                return_value=Response(
                    200,
                    json={
                        "errcode": 0,
                        "errmsg": "ok",
                        "balance": 1000,
                        "present_balance": 200,
                        "sum_save": 800,
                        "sum_present": 200,
                        "sum_balance": 1000,
                        "sum_cost": 500,
                        "first_save_flag": True,
                    },
                )
            )

            # 不传入 logger，应该正常工作
            client = XPayClient(
                app_id="wx123",
                app_key="test_key",
                env=1,
            )

            balance = client.query_user_balance(
                openid="user_123",
                access_token="test_access_token",
                session_key="session_key_456",
            )

            assert balance.balance == 1000
            client.close()

    def test_sync_client_logs_error(self):
        """测试同步客户端记录错误日志。"""
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        logger = logging.getLogger("test_sync_error")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        with respx.mock:
            respx.post("https://api.weixin.qq.com/xpay/query_user_balance").mock(
                return_value=Response(
                    200,
                    json={"errcode": -1, "errmsg": "系统错误"},
                )
            )

            client = XPayClient(
                app_id="wx123",
                app_key="test_key",
                env=1,
                logger=logger,
            )

            with pytest.raises(XPayAPIError):
                client.query_user_balance(
                    openid="user_123",
                    access_token="test_access_token",
                    session_key="session_key_456",
                )

            client.close()

        # 验证错误日志
        log_output = log_stream.getvalue()
        assert "ERROR" in log_output
        assert "XPay API Error" in log_output
        assert "系统错误" in log_output

    @respx.mock
    async def test_async_client_with_logger(self):
        """测试异步客户端使用 logger。"""
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(levelname)s - %(message)s")
        handler.setFormatter(formatter)

        logger = logging.getLogger("test_async")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        respx.post("https://api.weixin.qq.com/xpay/query_user_balance").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "balance": 1000,
                    "present_balance": 200,
                    "sum_save": 800,
                    "sum_present": 200,
                    "sum_balance": 1000,
                    "sum_cost": 500,
                    "first_save_flag": True,
                },
            )
        )

        async with XPayAsyncClient(
            app_id="wx123",
            app_key="test_key",
            env=1,
            logger=logger,
        ) as client:
            await client.query_user_balance(
                openid="user_123",
                access_token="test_access_token",
                session_key="session_key_456",
            )

        # 验证日志内容
        log_output = log_stream.getvalue()
        assert "XPay API Request" in log_output
        assert "XPay API Response: Success" in log_output

    @respx.mock
    async def test_async_client_without_logger(self):
        """测试异步客户端不使用 logger。"""
        respx.post("https://api.weixin.qq.com/xpay/query_user_balance").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "balance": 1000,
                    "present_balance": 200,
                    "sum_save": 800,
                    "sum_present": 200,
                    "sum_balance": 1000,
                    "sum_cost": 500,
                    "first_save_flag": True,
                },
            )
        )

        # 不传入 logger，应该正常工作
        async with XPayAsyncClient(
            app_id="wx123",
            app_key="test_key",
            env=1,
        ) as client:
            balance = await client.query_user_balance(
                openid="user_123",
                access_token="test_access_token",
                session_key="session_key_456",
            )

            assert balance.balance == 1000
