"""Stream type classes for tap-sunwave."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from typing import TYPE_CHECKING, ClassVar

from tap_sunwave.client import SunwaveStream

if sys.version_info >= (3, 11):
    pass
else:
    from backports.datetime_fromisoformat import MonkeyPatch

    MonkeyPatch.patch_fromisoformat()

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Iterable

    import requests
    from singer_sdk.helpers.types import Context


SUNWAVE_DATETIME_FORMAT = "%m/%d/%Y %I:%M:%S %p"


def _normalize_sunwave_datetime(value: str | None) -> str | None:
    """Convert Sunwave datetime format to ISO 8601."""
    if not value:
        return value
    try:
        return (
            datetime.strptime(value, SUNWAVE_DATETIME_FORMAT)
            .replace(tzinfo=timezone.utc)
            .isoformat()
        )
    except ValueError:
        return value


class UserStream(SunwaveStream):
    name = "user"
    path = "/api/users"
    primary_keys = ("id",)
    replication_key = None

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        row["created_on"] = _normalize_sunwave_datetime(row.get("created_on"))
        return row


class ReferralStream(SunwaveStream):
    name = "referral"
    path = "/api/referrals/status/{status}"
    primary_keys = ("id",)
    replication_key = None

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        row["created_on"] = _normalize_sunwave_datetime(row.get("created_on"))
        return row


class FormsStream(SunwaveStream):
    """Stream for retrieving forms data from Sunwave."""

    name = "form"
    path = "/api/forms"
    primary_keys = ("id",)
    replication_key = None


class OpportunitiesStream(SunwaveStream):
    """Stream for retrieving data about opportunities from Sunwave."""

    name = "opportunity"
    primary_keys = ("opportunity_id",)
    replication_key = "created_on"

    @property
    def path(self) -> str:
        bookmark = self.get_starting_replication_key_value(None)
        start_date = datetime.fromisoformat(bookmark or self.config["start_date"])
        end_date = datetime.now(tz=timezone.utc)
        return (
            f"/api/opportunities/createdon/from/{start_date.strftime('%Y-%m-%d')}/until/{end_date.strftime('%Y-%m-%d')}"
        )

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        row["created_on"] = _normalize_sunwave_datetime(row.get("created_on"))
        return row

    @override
    def get_child_context(self, record: dict, context: Context | None) -> Context | None:
        if "opportunity_id" in record:
            return {"opportunity_id": record["opportunity_id"]}
        return None


class OpportunityTimelineStream(SunwaveStream):
    """Stream for retrieving timeline data for opportunities from Sunwave."""

    name = "opportunity_timeline"
    records_jsonpath = "$[*]"
    primary_keys = ("id",)
    replication_key = "created_on"
    state_partitioning_keys: ClassVar[list[str]] = []
    ignore_parent_replication_keys = True
    parent_stream_type = OpportunitiesStream
    path = "/api/opportunities/{opportunity_id}/timeline"

    @override
    def post_process(self, row: dict, context: Context | None = None) -> dict | None:
        row["created_on"] = _normalize_sunwave_datetime(row.get("created_on"))
        return row


class CensusStream(SunwaveStream):
    """
    Stream for retrieving census data from Sunwave.
    """

    name = "census"
    partitions: ClassVar[list[dict]] = [
        {"census_status": "active"},
        {"census_status": "admitted"},
        {"census_status": "discharged"},
    ]
    primary_keys = ("Account Id",)
    replication_key = None

    @property
    def path(self) -> str:
        start_date = datetime.fromisoformat(self.config["start_date"])
        end_date = datetime.now(tz=timezone.utc)
        return "/api/census/{census_status}/from/{start}/until/{end}".format(
            census_status="{census_status}",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
        )
