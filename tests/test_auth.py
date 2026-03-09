"""Tests for authentication module."""

import pytest

from wechat_xpay.auth import calc_pay_sig, calc_signature


class TestAuth:
    """Test suite for authentication functions."""

    def test_calc_pay_sig(self):
        """Test pay_sig calculation."""
        uri = "/xpay/query_user_balance"
        post_body = '{"openid":"test_openid","appid":"wx123","env":0}'
        app_key = "test_app_key"

        result = calc_pay_sig(uri, post_body, app_key)

        # Verify it's a valid hex string
        assert len(result) == 64  # SHA-256 produces 32 bytes = 64 hex chars
        int(result, 16)  # Should not raise

    def test_calc_signature(self):
        """Test signature calculation."""
        post_body = '{"openid":"test_openid","appid":"wx123","env":0}'
        session_key = "test_session_key"

        result = calc_signature(post_body, session_key)

        # Verify it's a valid hex string
        assert len(result) == 64
        int(result, 16)

    def test_pay_sig_consistency(self):
        """Test that pay_sig is consistent for same input."""
        uri = "/xpay/query_user_balance"
        post_body = '{"openid":"test_openid"}'
        app_key = "test_key"

        sig1 = calc_pay_sig(uri, post_body, app_key)
        sig2 = calc_pay_sig(uri, post_body, app_key)

        assert sig1 == sig2

    def test_signature_consistency(self):
        """Test that signature is consistent for same input."""
        post_body = '{"openid":"test_openid"}'
        session_key = "test_key"

        sig1 = calc_signature(post_body, session_key)
        sig2 = calc_signature(post_body, session_key)

        assert sig1 == sig2
