"""Sunwave Authentication."""

from __future__ import annotations
import base64
from datetime import datetime, timezone
import hashlib
import hmac
import uuid
import typing as t

import requests
from singer_sdk.authenticators import APIAuthenticatorBase, SingletonMeta

if t.TYPE_CHECKING:
    from tap_sunwave.client import SunwaveStream

class SunwaveAuthenticator(APIAuthenticatorBase, metaclass=SingletonMeta):
    """Authenticator class for Sunwave."""


    def authenticate_request(
        self,
        request: requests.PreparedRequest,
    ) -> requests.PreparedRequest:
        
        request_body = request.body if request.body else ""

        date_calc = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
        dateTimeBase64 = base64.b64encode(date_calc.encode('utf-8')).decode('utf-8')
        unique_transaction_id = str(uuid.uuid4())

        md5_payload = hashlib.md5(request_body.encode('utf-8')).hexdigest() # For GET requests this isn't needed, but an empty string md5'd works
        base64md5Payload_bytes = base64.b64encode(md5_payload.encode('utf-8'))
        base64md5Payload = base64md5Payload_bytes.decode('utf-8').replace('/', '_').replace('+', '-')

        seed_string = f"{self.config['user_id']}:{self.config['client_id']}:{dateTimeBase64}:{self.config['clinic_id']}:{unique_transaction_id}:{base64md5Payload}"
        seed_bytes = seed_string.encode('utf-8')

        hmac_digest = hmac.new(self.config['client_secret'].encode('utf-8'), seed_bytes, hashlib.sha512).digest()
        hmacBase64_bytes = base64.b64encode(hmac_digest)
        hmacBase64 = hmacBase64_bytes.decode('utf-8').replace('/', '_').replace('+', '-')

        request.headers.update({"Authorization": f"Digest {seed_string}:{hmacBase64}"})

        return request

    @classmethod
    def create_for_stream(cls, stream: SunwaveStream) -> SunwaveAuthenticator:  # noqa: ANN001
        return cls(stream=stream)
