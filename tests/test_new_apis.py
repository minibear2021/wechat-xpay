"""测试新增的 API 实现。"""

import pytest
import respx
from httpx import Response

from wechat_xpay import XPayClient, XPayAsyncClient
from wechat_xpay import models


class TestNotifyProvideGoods:
    """测试发货完成通知 API。"""

    @respx.mock
    def test_notify_provide_goods_sync(self):
        """测试同步发货通知。"""
        client = XPayClient(
            app_id="wx123",
            app_key="test_key",
            env=0,
        )
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/notify_provide_goods").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "order_id": "order_123",
                    "out_trade_no": "OUT_001",
                    "provide_status": 1,
                },
            )
        )

        result = client.notify_provide_goods(
            session_key="session_key_456",
            order_id="order_123",
        )

        assert isinstance(result, models.NotifyProvideGoodsResult)
        assert result.order_id == "order_123"
        assert result.out_trade_no == "OUT_001"
        assert result.provide_status == 1
        assert route.called

    @respx.mock
    async def test_notify_provide_goods_async(self):
        """测试异步发货通知。"""
        client = XPayAsyncClient(
            app_id="wx123",
            app_key="test_key",
            env=0,
        )
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/notify_provide_goods").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "order_id": "order_123",
                    "out_trade_no": "OUT_001",
                    "provide_status": 1,
                },
            )
        )

        result = await client.notify_provide_goods(
            session_key="session_key_456",
            wx_order_id="wx_order_123",
        )

        assert isinstance(result, models.NotifyProvideGoodsResult)
        assert result.provide_status == 1
        assert route.called
        await client.close()


class TestGoodsManagement:
    """测试道具管理 API。"""

    @respx.mock
    def test_start_upload_goods_sync(self):
        """测试同步启动道具上传。"""
        client = XPayClient(
            app_id="wx123",
            app_key="test_key",
            env=0,
        )
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/start_upload_goods").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "status": 1,
                    "upload_item": [
                        {
                            "id": "goods_001",
                            "name": "道具1",
                            "price": 100,
                            "remark": "测试道具",
                            "item_url": "https://example.com/item1",
                            "upload_status": 0,
                        }
                    ],
                },
            )
        )

        result = client.start_upload_goods(
            session_key="session_key_456",
            goods=[
                {
                    "id": "goods_001",
                    "name": "道具1",
                    "price": 100,
                    "remark": "测试道具",
                    "item_url": "https://example.com/item1",
                }
            ],
        )

        assert isinstance(result, models.GoodsUploadStatus)
        assert result.status == 1
        assert len(result.upload_item) == 1
        assert result.upload_item[0].id == "goods_001"
        assert route.called

    @respx.mock
    def test_query_upload_goods_sync(self):
        """测试同步查询道具上传状态。"""
        client = XPayClient(
            app_id="wx123",
            app_key="test_key",
            env=0,
        )
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/query_upload_goods").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "status": 2,
                    "upload_item": [
                        {
                            "id": "goods_001",
                            "name": "道具1",
                            "price": 100,
                            "remark": "测试道具",
                            "item_url": "https://example.com/item1",
                            "upload_status": 1,
                        }
                    ],
                },
            )
        )

        result = client.query_upload_goods(session_key="session_key_456")

        assert isinstance(result, models.GoodsUploadStatus)
        assert result.status == 2
        assert result.upload_item[0].upload_status == 1
        assert route.called

    @respx.mock
    def test_start_publish_goods_sync(self):
        """测试同步启动道具发布。"""
        client = XPayClient(
            app_id="wx123",
            app_key="test_key",
            env=0,
        )
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/start_publish_goods").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "status": 1,
                    "publish_item": [
                        {"id": "goods_001", "publish_status": 0},
                        {"id": "goods_002", "publish_status": 0},
                    ],
                },
            )
        )

        result = client.start_publish_goods(
            session_key="session_key_456",
            goods=[{"id": "goods_001"}, {"id": "goods_002"}],
        )

        assert isinstance(result, models.GoodsPublishStatus)
        assert result.status == 1
        assert len(result.publish_item) == 2
        assert route.called

    @respx.mock
    def test_query_publish_goods_sync(self):
        """测试同步查询道具发布状态。"""
        client = XPayClient(
            app_id="wx123",
            app_key="test_key",
            env=0,
        )
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/query_publish_goods").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "status": 2,
                    "publish_item": [
                        {"id": "goods_001", "publish_status": 1},
                    ],
                },
            )
        )

        result = client.query_publish_goods(session_key="session_key_456")

        assert isinstance(result, models.GoodsPublishStatus)
        assert result.status == 2
        assert result.publish_item[0].publish_status == 1
        assert route.called


class TestFundsBillAPIs:
    """测试广告金账单 API。"""

    @respx.mock
    def test_create_funds_bill_sync(self):
        """测试同步创建广告金账单。"""
        client = XPayClient(
            app_id="wx123",
            app_key="test_key",
            env=0,
        )
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/create_funds_bill").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "bill_id": "bill_123",
                },
            )
        )

        result = client.create_funds_bill(
            session_key="session_key_456",
            transfer_account_uid=12345,
            transfer_account_agency_id=67890,
            transfer_amount=10000,
            fund_id="fund_001",
            settle_begin=1700000000,
            settle_end=1700086400,
        )

        assert isinstance(result, models.FundsBillResult)
        assert result.bill_id == "bill_123"
        assert route.called

    @respx.mock
    def test_bind_transfer_account_sync(self):
        """测试同步绑定转账账户。"""
        client = XPayClient(
            app_id="wx123",
            app_key="test_key",
            env=0,
        )
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/bind_transfer_accout").mock(
            return_value=Response(
                200,
                json={"errcode": 0, "errmsg": "ok"},
            )
        )

        result = client.bind_transfer_account(
            session_key="session_key_456",
            transfer_account_uid=12345,
            transfer_account_agency_id=67890,
        )

        assert result is True
        assert route.called

    @respx.mock
    def test_query_funds_bill_sync(self):
        """测试同步查询资金账单。"""
        client = XPayClient(
            app_id="wx123",
            app_key="test_key",
            env=0,
        )
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/query_funds_bill").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "total_page": 1,
                    "bill_list": [
                        {
                            "bill_id": "bill_001",
                            "oper_time": 1700000000,
                            "settle_begin": 1700000000,
                            "settle_end": 1700086400,
                            "fund_id": "fund_001",
                            "transfer_account_name": "Account 1",
                            "transfer_account_uid": 12345,
                            "transfer_amount": 10000,
                            "status": 1,
                            "request_id": "req_001",
                        }
                    ],
                },
            )
        )

        result = client.query_funds_bill(
            session_key="session_key_456",
            page=1,
            page_size=10,
        )

        assert isinstance(result, models.FundsBillList)
        assert result.total_page == 1
        assert len(result.bill_list) == 1
        assert result.bill_list[0].bill_id == "bill_001"
        assert route.called

    @respx.mock
    def test_query_recover_bill_sync(self):
        """测试同步查询回收账单。"""
        client = XPayClient(
            app_id="wx123",
            app_key="test_key",
            env=0,
        )
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/query_recover_bill").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "total_page": 1,
                    "bill_list": [
                        {
                            "bill_id": "recover_001",
                            "recover_time": 1700000000,
                            "settle_begin": 1700000000,
                            "settle_end": 1700086400,
                            "fund_id": "fund_001",
                            "recover_account_name": "Account 1",
                            "recover_amount": 5000,
                            "refund_order_list": ["order_001", "order_002"],
                        }
                    ],
                },
            )
        )

        result = client.query_recover_bill(
            session_key="session_key_456",
            page=1,
            page_size=10,
        )

        assert isinstance(result, models.RecoverBillList)
        assert result.total_page == 1
        assert len(result.bill_list) == 1
        assert result.bill_list[0].bill_id == "recover_001"
        assert len(result.bill_list[0].refund_order_list) == 2
        assert route.called

    @respx.mock
    def test_download_adverfunds_order_sync(self):
        """测试同步下载广告金订单账单。"""
        client = XPayClient(
            app_id="wx123",
            app_key="test_key",
            env=0,
        )
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/download_adverfunds_order").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "url": "https://example.com/adverfunds_order.csv",
                },
            )
        )

        result = client.download_adverfunds_order(
            session_key="session_key_456",
            begin_ds=20230801,
            end_ds=20230810,
        )

        assert isinstance(result, models.AdverfundsOrderDownload)
        assert result.url == "https://example.com/adverfunds_order.csv"
        assert route.called


class TestNegotiationHistory:
    """测试协商历史 API。"""

    @respx.mock
    def test_get_negotiation_history_sync(self):
        """测试同步获取协商历史。"""
        client = XPayClient(
            app_id="wx123",
            app_key="test_key",
            env=0,
        )
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/get_negotiation_history").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "total": 2,
                    "history": [
                        {
                            "log_id": "log_001",
                            "operator": "user",
                            "operate_time": "2023-11-28T10:00:00+08:00",
                            "operate_type": "APPLY_REFUND",
                            "operate_details": "申请退款",
                        },
                        {
                            "log_id": "log_002",
                            "operator": "mch",
                            "operate_time": "2023-11-28T11:00:00+08:00",
                            "operate_type": "RESPONSE",
                            "operate_details": "商家回复",
                        },
                    ],
                },
            )
        )

        result = client.get_negotiation_history(
            session_key="session_key_456",
            complaint_id="complaint_123",
            offset=0,
            limit=10,
        )

        assert isinstance(result, models.NegotiationHistory)
        assert result.total == 2
        assert len(result.history) == 2
        assert result.history[0].log_id == "log_001"
        assert route.called


class TestUploadFileSign:
    """测试上传文件签名 API。"""

    @respx.mock
    def test_get_upload_file_sign_sync(self):
        """测试同步获取上传文件签名。"""
        client = XPayClient(
            app_id="wx123",
            app_key="test_key",
            env=0,
        )
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/get_upload_file_sign").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "sign": "abc123signature",
                    "cos_url": "https://cos.example.com/upload",
                },
            )
        )

        result = client.get_upload_file_sign(
            session_key="session_key_456",
            file_name="test.jpg",
            file_type="image/jpeg",
        )

        assert isinstance(result, models.UploadFileSign)
        assert result.sign == "abc123signature"
        assert result.cos_url == "https://cos.example.com/upload"
        assert route.called

    @respx.mock
    async def test_get_upload_file_sign_async(self):
        """测试异步获取上传文件签名。"""
        client = XPayAsyncClient(
            app_id="wx123",
            app_key="test_key",
            env=0,
        )
        route = respx.post("https://api.xpay.weixin.qq.com/xpay/get_upload_file_sign").mock(
            return_value=Response(
                200,
                json={
                    "errcode": 0,
                    "errmsg": "ok",
                    "sign": "abc123signature",
                    "cos_url": "https://cos.example.com/upload",
                },
            )
        )

        result = await client.get_upload_file_sign(
            session_key="session_key_456",
            file_name="test.png",
            file_type="image/png",
        )

        assert isinstance(result, models.UploadFileSign)
        assert result.sign == "abc123signature"
        assert route.called
        await client.close()
