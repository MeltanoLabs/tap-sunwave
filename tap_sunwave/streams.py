"""Stream type classes for tap-sunwave."""

from __future__ import annotations

import typing as t
from importlib import resources

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_sunwave.client import SunwaveStream

SCHEMAS_DIR = resources.files(__package__) / "schemas"


class UserStream(SunwaveStream):

    name = "user"
    path = "/api/users"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / f"{name}.json"
