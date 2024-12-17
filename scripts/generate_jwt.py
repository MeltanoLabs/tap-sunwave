
import jwt
import datetime
import hashlib
import hmac
import os
import uuid
import base64
from dotenv import load_dotenv

def generate_jwt_token():
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
    hmac_token = hmac.new(
        key=client_secret.encode(),
        msg=seed.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    jwt_token = jwt.encode(
        payload={
            "seed": seed
        },
        key=client_secret,
        algorithm="HS256"
    )
    
    return (f"{seed}:{hmac_token}", f"{seed}:{jwt_token}")

if __name__ == "__main__":
    hmac_token, jwt_token = generate_jwt_token()
    with open(".secrets/token_out.txt", "w") as file:
        file.write(f"HMAC TOKEN:\n{hmac_token}\n\nJWT TOKEN:\n{jwt_token}")
