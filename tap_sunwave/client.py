"""REST client handling, including SunwaveStream base class."""

from __future__ import annotations

import typing as t
from functools import cached_property
from importlib import resources

from singer_sdk.streams import RESTStream

from tap_sunwave.auth import SunwaveAuthenticator

if t.TYPE_CHECKING:
    from singer_sdk.helpers.types import Auth


SCHEMAS_DIR = resources.files(__package__) / "schemas"


class SunwaveStream(RESTStream):
    """Sunwave stream class."""

    url_base = "https://emr.sunwavehealth.com/SunwaveEMR"

    @cached_property
    def authenticator(self) -> Auth:
        return SunwaveAuthenticator.create_for_stream(self)
