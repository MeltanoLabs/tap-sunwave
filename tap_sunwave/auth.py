"""Sunwave Authentication."""

from __future__ import annotations

import base64
import hashlib
import hmac
import sys
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

from singer_sdk.authenticators import APIAuthenticatorBase, SingletonMeta

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    import requests


class SunwaveAuthenticator(APIAuthenticatorBase, metaclass=SingletonMeta):
    """Authenticator class for Sunwave."""

    @override
    def __init__(
        self,
        *args: Any,
        user_id: str,
        clinic_id: str,
        client_id: str,
        client_secret: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the authenticator.

        Args:
            user_id: The user's email address.
            clinic_id: The clinic ID.
            client_id: The client ID.
            client_secret: The client secret.
        """
        super().__init__(*args, **kwargs)
        self.user_id = user_id
        self.clinic_id = clinic_id
        self.client_id = client_id
        self.client_secret = client_secret

    @override
    def authenticate_request(
        self,
        request: requests.PreparedRequest,
    ) -> requests.PreparedRequest:
        date_calc = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
        datetime_base_64 = base64.b64encode(date_calc.encode("utf-8")).decode("utf-8")
        unique_transaction_id = str(uuid.uuid4())

        # For GET requests this isn't needed, but an empty string md5'd works
        match request.body:
            case str(val):
                md5_payload = hashlib.md5(val.encode("utf-8")).hexdigest()  # noqa: S324
            case bytes(val):
                md5_payload = hashlib.md5(val).hexdigest()  # noqa: S324
            case _:
                md5_payload = hashlib.md5(b"").hexdigest()  # noqa: S324

        base64_md5_payload_bytes = base64.b64encode(md5_payload.encode("utf-8"))
        base64_md5_payload = base64_md5_payload_bytes.decode("utf-8").replace("/", "_").replace("+", "-")

        seed_string = (
            f"{self.user_id}:{self.client_id}:{datetime_base_64}:"
            f"{self.clinic_id}:{unique_transaction_id}:{base64_md5_payload}"
        )
        seed_bytes = seed_string.encode("utf-8")

        hmac_digest = hmac.new(self.client_secret.encode("utf-8"), seed_bytes, hashlib.sha512).digest()
        hmac_base64_bytes = base64.b64encode(hmac_digest)
        hmac_base64 = hmac_base64_bytes.decode("utf-8").replace("/", "_").replace("+", "-")

        request.headers.update({"Authorization": f"Digest {seed_string}:{hmac_base64}"})

        return request
