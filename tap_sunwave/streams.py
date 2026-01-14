"""Stream type classes for tap-sunwave."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from typing import TYPE_CHECKING, ClassVar

from tap_sunwave.client import SunwaveStream

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from collections.abc import Iterable

    import requests
    from singer_sdk.helpers.types import Context


class UserStream(SunwaveStream):
    name = "user"
    path = "/api/users"
    primary_keys = ("id",)
    replication_key = None


class ReferralStream(SunwaveStream):
    name = "referral"
    path = "/api/referrals/status/{status}"
    primary_keys = ("id",)
    replication_key = None


class FormsStream(SunwaveStream):
    """Stream for retrieving forms data from Sunwave."""

    name = "form"
    path = "/api/forms"
    primary_keys = ("id",)
    replication_key = None


class OpportunitiesStream(SunwaveStream):
    """
    Stream for retrieving data about opportunities from Sunwave.
    """

    name = "opportunity"
    primary_keys = ("opportunity_id",)
    replication_key = None

    @property
    def path(self) -> str:
        # Use strptime() instead of fromisoformat() for broader Python version support
        start_date_str = self.config["start_date"]
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")  # noqa: DTZ007
        end_date = datetime.now(tz=timezone.utc)  # or datetime.today(), depending on your needs
        return (
            f"/api/opportunities/createdon/from/{start_date.strftime('%Y-%m-%d')}/until/{end_date.strftime('%Y-%m-%d')}"
        )

    @override
    def get_child_context(self, record: dict, context: Context | None) -> Context | None:
        if "opportunity_id" in record:
            return {"opportunity_id": record["opportunity_id"]}
        return None


class OpportunityTimelineStream(SunwaveStream):
    """
    Stream for retrieving data about opportunities from Sunwave.
    """

    name = "opportunity_timeline"
    primary_keys = ("id",)
    replication_key = None
    parent_stream_type = OpportunitiesStream
    path = "/api/opportunities/{opportunity_id}/timeline"

    @override
    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: A raw :class:`requests.Response`

        Yields:
            One item for every item found in the response.
        """
        if isinstance(response.json(), list):
            yield from super().parse_response(response)


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
        start_date_str = self.config["start_date"]
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")  # noqa: DTZ007
        end_date = datetime.now(tz=timezone.utc)
        return "/api/census/{census_status}/from/{start}/until/{end}".format(
            census_status="{census_status}",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
        )
