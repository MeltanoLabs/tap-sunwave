"""Sunwave tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_sunwave import streams


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
    ).to_dict()

    def discover_streams(self) -> list[streams.SunwaveStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.UserStream(self),
        ]


if __name__ == "__main__":
    TapSunwave.cli()
