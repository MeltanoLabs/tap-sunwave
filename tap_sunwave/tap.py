"""Sunwave tap class."""

from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_sunwave import streams

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

if TYPE_CHECKING:
    from singer_sdk import Stream


def _default_date() -> str:
    return (datetime.now(tz=timezone.utc).date() - timedelta(365)).isoformat()


class TapSunwave(Tap):
    """Sunwave tap class."""

    name = "tap-sunwave"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "user_id",
            th.StringType,
            required=True,
            description="Email address of the user to authenticate with.",
        ),
        th.Property(
            "client_id",
            th.StringType,
            required=True,
            description="Client ID, obtained from Sunwave support staff.",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            required=True,
            description="Client secret, obtained from Sunwave support staff.",
        ),
        th.Property(
            "clinic_id",
            th.StringType,
            required=True,
            description="Clinic ID, obtained by inspecting requests in the browser.",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            required=True,
            description=(
                "Start date for the data to be retrieved. If a date-time is provided, "
                "only the date portion will be used."
            ),
            default=_default_date(),
        ),
    ).to_dict()

    @override
    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.FormsStream(tap=self),
            streams.UserStream(self),
            streams.OpportunitiesStream(self),
            streams.OpportunityTimelineStream(self),
            streams.CensusStream(self),
        ]


if __name__ == "__main__":
    TapSunwave.cli()
