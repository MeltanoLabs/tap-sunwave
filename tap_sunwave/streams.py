"""Stream type classes for tap-sunwave."""

from __future__ import annotations

import typing as t
from importlib import resources
from tap_sunwave.client import SunwaveStream
from datetime import datetime
import json
import requests

SCHEMAS_DIR = resources.files(__package__) / "schemas"


class UserStream(SunwaveStream):

    name = "user"
    path = "/api/users"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / f"{name}.json"

class ReferralStream(SunwaveStream):

    name = "referral"
    path = "/api/referrals/status/{status}"
    primary_keys: t.ClassVar[list[str]] = ["id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / f"{name}.json"


class FormsStream(SunwaveStream):
    """Stream for retrieving forms data from Sunwave."""
    
    name = "form"
    path = "/api/forms"
    primary_keys = ["id"]
    replication_key = None

    @property
    def schema(self):
        """
        Retrieve the schema for Forms directly from Swagger at:
        #/components/schemas/FormStandardResponse
        """
        return self._get_swagger_schema("#/components/schemas/FormStandardResponse")
    

class OpportunitiesStream(SunwaveStream):
    """
    Stream for retrieving data about opportunities from Sunwave.
    """
    name = "opportunity"
    primary_keys = ["opportunity_id"]
    replication_key = None
    
    @property
    def schema(self):
        return self._get_swagger_schema("#/components/schemas/Opportunities")
   
    @property
    def path(self):
        # Use strptime() instead of fromisoformat() for broader Python version support
        start_date_str = self.config["start_date"]
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.now()  # or datetime.today(), depending on your needs
        return f"/api/opportunities/createdon/from/{start_date.strftime('%Y-%m-%d')}/until/{end_date.strftime('%Y-%m-%d')}"
    
    def get_child_context(self, record: dict, context: dict) -> dict:
        if "opportunity_id" in record:
            return {
                "opportunity_id": record["opportunity_id"]
            }
        else:
            return None

class OpportunityTimelineStream(SunwaveStream):
    """
    Stream for retrieving data about opportunities from Sunwave.
    """
    name = "opportunity_timeline"
    primary_keys = ["id"]
    replication_key = None
    parent_stream_type = OpportunitiesStream
    path =  "/api/opportunities/{opportunity_id}/timeline"
    
    @property
    def schema(self):
        return self._get_swagger_schema("#/components/schemas/OpportunitiesTimeline")

    def parse_response(self, response: requests.Response) -> t.Iterable[dict]:
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
    path = "/api/census"
    partitions = [{"census_status":"active"}, {"census_status":"admitted"}, {"census_status":"discharged"}]
    primary_keys = ["Account Id"]
    replication_key = None

    @property
    def path(self):
        start_date_str = self.config["start_date"]
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.now()
        return "/api/census/{census_status}/from/{start}/until/{end}".format(
            census_status="{census_status}",
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d')
        )

    @property
    def schema(self):
        return self._get_swagger_schema("#/components/schemas/Census")
    
    def get_child_context(self, record: dict, context: dict) -> dict:
        return {
            "account_id": record["Account Id"]
        }

class TimelineActivityStream(SunwaveStream):
    """
    Stream for retrieving timeline activity data from Sunwave.
    """
    name = "timeline_activity"
    path = "/api/account/{account_id}/timeline"
    primary_keys = ["id"]
    replication_key = None
    parent_stream_type = CensusStream

    @property
    def schema(self):
        return self._get_swagger_schema("#/components/schemas/TimelineActivity")
    