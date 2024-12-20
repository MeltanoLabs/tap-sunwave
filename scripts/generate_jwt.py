
import jwt
import datetime
import hashlib
import hmac
import os
import uuid
import base64
import requests
from dotenv import load_dotenv

def generate_token():
    """
    Docs: https://emr.sunwavehealth.com/SunwaveEMR/swagger/
    """

    load_dotenv()
    
    user_id = os.getenv("TAP_SUNWAVE_USER_ID")
    client_id = os.getenv("TAP_SUNWAVE_CLIENT_ID") 
    client_secret = os.getenv("TAP_SUNWAVE_CLIENT_SECRET")
    dateTimeBase64 = base64.b64encode(datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000").encode()).decode()
    clinic_id = os.getenv("TAP_SUNWAVE_CLINIC_ID")
    unique_transaction_id = str(uuid.uuid4())

    seed = f"{user_id}:{client_id}:{dateTimeBase64}:{clinic_id}:{unique_transaction_id}"

    jwt_token = jwt.encode(
        payload={
            seed: client_secret
        },
        key=seed,
        algorithm="HS256"
    )
    
    return f"{jwt_token}"

if __name__ == "__main__":

    url_base = "https://emr.sunwavehealth.com/SunwaveEMR"
    url_path = "/api/users"
    response = requests.get(url_base + url_path, headers={"Authorization": f"Digest {generate_token()}"})
    print(response.json())
    print(response.status_code) # 200's when token is invalid {'error': 'invalid token'} in respons
    print(response.headers)
