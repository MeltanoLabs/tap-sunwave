import base64
import datetime
import hashlib
import hmac
import os
import uuid

import requests
from dotenv import load_dotenv


def generate_token(request_body):
    load_dotenv()

    user_id = os.getenv("TAP_SUNWAVE_USER_ID")  # This is the user's email address
    client_id = os.getenv("TAP_SUNWAVE_CLIENT_ID")
    client_secret = os.getenv("TAP_SUNWAVE_CLIENT_SECRET")
    clinic_id = os.getenv("TAP_SUNWAVE_CLINIC_ID")
    assert user_id is not None, "TAP_SUNWAVE_USER_ID is not set"
    assert client_id is not None, "TAP_SUNWAVE_CLIENT_ID is not set"
    assert client_secret is not None, "TAP_SUNWAVE_CLIENT_SECRET is not set"
    assert clinic_id is not None, "TAP_SUNWAVE_CLINIC_ID is not set"

    date_calc = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
    dateTimeBase64 = base64.b64encode(date_calc.encode("utf-8")).decode("utf-8")
    unique_transaction_id = str(uuid.uuid4())

    md5_payload = hashlib.md5(
        request_body.encode("utf-8")
    ).hexdigest()  # For gets this isn't needed, but an empty string md5'd works
    base64md5Payload_bytes = base64.b64encode(md5_payload.encode("utf-8"))
    base64md5Payload = base64md5Payload_bytes.decode("utf-8").replace("/", "_").replace("+", "-")

    seed_string = f"{user_id}:{client_id}:{dateTimeBase64}:{clinic_id}:{unique_transaction_id}:{base64md5Payload}"
    seed_bytes = seed_string.encode("utf-8")

    hmac_digest = hmac.new(client_secret.encode("utf-8"), seed_bytes, hashlib.sha512).digest()
    hmacBase64_bytes = base64.b64encode(hmac_digest)
    hmacBase64 = hmacBase64_bytes.decode("utf-8").replace("/", "_").replace("+", "-")

    full_seed = f"{seed_string}:{hmacBase64}"
    return full_seed


if __name__ == "__main__":
    url_base = "https://emr.sunwavehealth.com/SunwaveEMR"
    url_path = "/api/users"
    request_body_data = ""
    # Note that the response code is a 200 when the token is invalid

    token = generate_token(request_body_data)
    response = requests.get(url_base + url_path, headers={"Authorization": f"Digest {token}"})
    print(response.json())
    print(response.status_code)
