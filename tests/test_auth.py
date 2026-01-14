"""Test the custom SunwaveAuthenticator."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from tap_sunwave.auth import SunwaveAuthenticator


@pytest.fixture
def authenticator() -> SunwaveAuthenticator:
    """Create an authenticator instance for testing."""
    return SunwaveAuthenticator(
        user_id="test@example.com",
        clinic_id="clinic123",
        client_id="client456",
        client_secret="secret789",  # noqa: S106
    )


@pytest.fixture
def mock_request() -> MagicMock:
    """Create a mock request object."""
    request = MagicMock(spec=requests.PreparedRequest)
    request.body = None
    request.headers = {}
    return request


class TestSunwaveAuthenticator:
    """Tests for SunwaveAuthenticator."""

    def test_authenticate_request_sets_authorization_header(
        self,
        authenticator: SunwaveAuthenticator,
        mock_request: MagicMock,
    ) -> None:
        """Test that authenticate_request sets the Authorization header."""
        result = authenticator.authenticate_request(mock_request)

        assert "Authorization" in result.headers
        assert result.headers["Authorization"].startswith("Digest ")

    def test_authenticate_request_includes_credentials_in_header(
        self,
        authenticator: SunwaveAuthenticator,
        mock_request: MagicMock,
    ) -> None:
        """Test that the Authorization header contains the expected credentials."""
        result = authenticator.authenticate_request(mock_request)

        auth_header = result.headers["Authorization"]
        assert "test@example.com" in auth_header
        assert "client456" in auth_header
        assert "clinic123" in auth_header

    def test_authenticate_request_different_bodies_produce_different_signatures(
        self,
        authenticator: SunwaveAuthenticator,
    ) -> None:
        """Test that different request bodies produce different signatures."""
        request1 = MagicMock(spec=requests.PreparedRequest)
        request1.body = '{"key": "value1"}'
        request1.headers = {}

        request2 = MagicMock(spec=requests.PreparedRequest)
        request2.body = '{"key": "value2"}'
        request2.headers = {}

        # Use same fixed uuid for both to isolate body difference
        fixed_uuid = "550e8400-e29b-41d4-a716-446655440000"

        with patch("tap_sunwave.auth.uuid.uuid4", return_value=fixed_uuid):
            authenticator.authenticate_request(request1)
            header1 = request1.headers["Authorization"]

            authenticator.authenticate_request(request2)
            header2 = request2.headers["Authorization"]

        # Headers should differ because the MD5 of the body differs
        assert header1 != header2

    @pytest.mark.parametrize(
        "body",
        [
            pytest.param('{"key": "value"}', id="string"),
            pytest.param(b'{"key": "value"}', id="bytes"),
            pytest.param(None, id="none"),
        ],
    )
    def test_authenticate_request_with_body(
        self,
        body: str | bytes | None,
        authenticator: SunwaveAuthenticator,
        mock_request: MagicMock,
    ) -> None:
        """Test authentication with all supported request body types."""
        mock_request.body = body
        result = authenticator.authenticate_request(mock_request)

        assert "Authorization" in result.headers
        assert result.headers["Authorization"].startswith("Digest ")

    def test_authenticate_request_header_format(
        self,
        authenticator: SunwaveAuthenticator,
        mock_request: MagicMock,
    ) -> None:
        """Test that the Authorization header has the correct format."""
        result = authenticator.authenticate_request(mock_request)

        auth_header = result.headers["Authorization"]
        # Format: Digest user_id:client_id:datetime_b64:clinic_id:uuid:md5_b64:hmac_b64
        assert auth_header.startswith("Digest ")
        seed_and_hmac = auth_header[7:]  # Remove "Digest " prefix
        parts = seed_and_hmac.split(":")
        # Should have 7 parts: user_id, client_id, datetime, clinic_id, uuid, md5, hmac
        assert len(parts) == 7  # noqa: PLR2004
