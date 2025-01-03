"""REST client handling, including SunwaveStream base class."""

from __future__ import annotations

import decimal
import typing as t
from functools import cached_property
from importlib import resources

from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import BaseAPIPaginator  # noqa: TC002
from singer_sdk.streams import RESTStream

from tap_sunwave.auth import SunwaveAuthenticator

if t.TYPE_CHECKING:
    import requests
    from singer_sdk.helpers.types import Auth, Context


SCHEMAS_DIR = resources.files(__package__) / "schemas"


class SunwaveStream(RESTStream):
    """Sunwave stream class."""

    records_jsonpath = "$[*]"
    next_page_token_jsonpath = "$.next_page"  # noqa: S105
    url_base = "https://emr.sunwavehealth.com/SunwaveEMR"

    @cached_property
    def authenticator(self) -> Auth:
        return SunwaveAuthenticator.create_for_stream(self)

    @property
    def http_headers(self) -> dict:
        return {}

    def get_new_paginator(self) -> BaseAPIPaginator:
        return super().get_new_paginator()

    def get_url_params(
        self,
        context: Context | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ANN401
    ) -> dict[str, t.Any]:

        params: dict = {}
        return params

    def prepare_request_payload(
        self,
        context: Context | None,  # noqa: ARG002
        next_page_token: t.Any | None,  # noqa: ARG002, ANN401
    ) -> dict | None:
        return None
