"""REST client handling, including SunwaveStream base class."""

from __future__ import annotations

import sys
from functools import cached_property
from http import HTTPStatus
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import requests
from singer_sdk import SchemaDirectory, StreamSchema
from singer_sdk.exceptions import FatalAPIError
from singer_sdk.streams import RESTStream

from tap_sunwave import schemas
from tap_sunwave.auth import SunwaveAuthenticator

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from singer_sdk.helpers.types import Auth, Context


SCHEMAS_DIR = SchemaDirectory(schemas)


class SunwaveStream(RESTStream):
    """Sunwave stream class."""

    url_base = "https://emr.sunwavehealth.com/SunwaveEMR"
    schema = StreamSchema(SCHEMAS_DIR)

    @override
    def _request(self, prepared_request: requests.PreparedRequest, context: Context | None) -> requests.Response:
        """Auth wasn't getting ran for every retried request, so we need to do it here"""
        # Manually run authenticator before sending the request
        reauthed_request = self.authenticator.authenticate_request(prepared_request)
        # Then call the parent's method with our newly authenticated request
        return super()._request(reauthed_request, context)

    @override
    @cached_property
    def authenticator(self) -> Auth:
        return SunwaveAuthenticator(
            user_id=self.config["user_id"],
            client_id=self.config["client_id"],
            client_secret=self.config["client_secret"],
            clinic_id=self.config["clinic_id"],
        )

    @override
    def validate_response(self, response: requests.Response) -> None:
        """Validate HTTP response.
        Raises:
            FatalAPIError: If the request is not retriable.
            RetriableAPIError: If the request is retriable.
        """
        super().validate_response(response)

        try:
            json_response = response.json()
            # Check if response is a dict and has error
            if isinstance(json_response, dict) and json_response.get("error"):
                error_msg = self.response_error_message(response)
                raise FatalAPIError(error_msg)
        except requests.exceptions.JSONDecodeError as err:
            # Their API returns a 200 status code when there's an error
            # We detect that by noticing the response isn't valid JSON
            msg = self.response_error_message(response)
            raise FatalAPIError(msg) from err
