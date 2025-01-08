from tap_sunwave.client import SunwaveStream


class FormsStream(SunwaveStream):
    """Stream for retrieving forms data from Sunwave."""
    
    name = "forms"
    path = "/api/forms"
    primary_keys = ["id"]  # Assuming forms have an ID field
    replication_key = None  # Add if forms have a modified/created timestamp
    
    schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "name": {"type": "string"},
            "description": {"type": "string"},
            "status": {"type": "string"},
            "createdDate": {"type": "string", "format": "date-time"},
            "modifiedDate": {"type": "string", "format": "date-time"},
            # Add other form properties based on API response
        }
    } 