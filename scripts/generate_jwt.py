import datetime
import hashlib
import hmac
import os
import uuid
import base64
import requests
from dotenv import load_dotenv

def generate_token(request_body):
    load_dotenv()

    user_id = os.getenv("TAP_SUNWAVE_USER_ID")
    client_id = os.getenv("TAP_SUNWAVE_CLIENT_ID")
    client_secret = os.getenv("TAP_SUNWAVE_CLIENT_SECRET").encode('utf-8')
    date_calc = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
    print(f"{date_calc=}")
    dateTimeBase64 = base64.b64encode(date_calc.encode('utf-8')).decode('utf-8')
    print(f"{dateTimeBase64=}")
    clinic_id = os.getenv("TAP_SUNWAVE_CLINIC_ID")
    unique_transaction_id = str(uuid.uuid4())

    md5_payload = hashlib.md5(request_body.encode('utf-8')).hexdigest()
    print(f"{md5_payload=}")
    base64md5Payload_bytes = base64.b64encode(md5_payload.encode('utf-8'))
    base64md5Payload = base64md5Payload_bytes.decode('utf-8').replace('/', '_').replace('+', '-')
    print(f"{base64md5Payload=}")

    seed_string = f"{user_id}:{client_id}:{dateTimeBase64}:{clinic_id}:{unique_transaction_id}:{base64md5Payload}"
    print(f"{seed_string=}")
    seed_bytes = seed_string.encode('utf-8')

    hmac_digest = hmac.new(client_secret, seed_bytes, hashlib.sha512).digest()
    hmacBase64_bytes = base64.b64encode(hmac_digest)
    hmacBase64 = hmacBase64_bytes.decode('utf-8').replace('/', '_').replace('+', '-')
    print(f"{hmacBase64=}")

    full_seed = f"{seed_string}:{hmacBase64}"
    print(f"{full_seed=}")
    return full_seed

if __name__ == "__main__":
    url_base = "https://emr.sunwavehealth.com/SunwaveEMR"
    url_path = "/api/users"
    request_body_data = ""

    token = generate_token(request_body_data)
    print(f"Token: {token}")
    response = requests.get(url_base + url_path, headers={"Authorization": f"Digest {token}"})
    print(response.json())
    print(response.status_code)
    print(response.headers)