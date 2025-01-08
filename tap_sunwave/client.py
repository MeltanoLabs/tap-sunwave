"""REST client handling, including SunwaveStream base class."""

from __future__ import annotations

import typing as t
import requests
import json
from pathlib import Path
from functools import cached_property
from importlib import resources

from singer_sdk.streams import RESTStream

from tap_sunwave.auth import SunwaveAuthenticator
from http import HTTPStatus
from urllib.parse import urlparse

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Auth


SCHEMAS_DIR = resources.files(__package__) / "schemas"


class SunwaveStream(RESTStream):
    """Sunwave stream class."""

    url_base = "https://emr.sunwavehealth.com/SunwaveEMR"

    @cached_property
    def authenticator(self) -> Auth:
        return SunwaveAuthenticator.create_for_stream(self)

    def response_error_message(self, response: requests.Response) -> str:
        """Build error message for invalid http statuses.

        WARNING - Override this method when the URL path may contain secrets or PII

        Args:
            response: A :class:`requests.Response` object.

        Returns:
            str: The error message
        """
        full_path = urlparse(response.url).path or self.path
        error_type = (
            "Client"
            if HTTPStatus.BAD_REQUEST
            <= response.status_code
            < HTTPStatus.INTERNAL_SERVER_ERROR
            else "Server"
        )

        return (
            f"{response.status_code} {error_type} Error: "
            f"{response.reason} for path: {full_path}. "
            f"{response.text=} for path: {full_path}"
        )

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: A raw :class:`requests.Response`

        Yields:
            One item for every item found in the response.
        """
        try:
            yield from super().parse_response(response)
        except requests.exceptions.JSONDecodeError as e:
            # Their API returns a 200 status code when there's an error
            # We detect that by noticing the response isn't valid JSON
            self.logger.info(self.response_error_message(response))
            raise e

    def _cleanup_schema(self, schema_fragment):
        if isinstance(schema_fragment, dict):
            # remove 'example' if present
            schema_fragment.pop("example", None)

            # if there's a 'type' and it's a string, make it ["null", type]
            if "type" in schema_fragment and isinstance(schema_fragment["type"], list):
                schema_fragment["type"].append("null")
            if "type" in schema_fragment and isinstance(schema_fragment["type"], str):
                schema_fragment["type"] = ["null", schema_fragment["type"]]

            # recursively process sub-objects
            for value in schema_fragment.values():
                self._cleanup_schema(value)

        elif isinstance(schema_fragment, list):
            for item in schema_fragment:
                self._cleanup_schema(item)

    def _get_swagger_schema(self, ref: str) -> dict:
        """
        Could be more efficient, but it works.
        """

        # Adjust the path to your swagger.json file as needed
        swagger_path = Path("docs/swagger.json")

        with open(swagger_path, "r", encoding="utf-8") as f:
            swagger_doc = json.load(f)

        # Example: ref => "#/components/schemas/FormStandardResponse"
        # Strip the leading "#/" and split by "/"
        path_parts = ref.lstrip("#/").split("/")

        # Travserse the swagger doc to get the nested object
        data = swagger_doc
        for part in path_parts:
            data = data[part]
        
        cleaned_schema = self._cleanup_schema(data["properties"])
        assert len(data["properties"]) > 1, "No properties found in schema"
        return data