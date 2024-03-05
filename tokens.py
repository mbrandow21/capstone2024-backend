import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
load_dotenv()
from jwt import ExpiredSignatureError


def assign_token(user_ID, username):
    payload = {
        "user_id": user_ID,
        "email": username,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    encoded = jwt.encode(payload, os.environ.get("TOKEN_SECRET"), algorithm="HS256")
    return encoded, 200

def authenticateToken(token):
    
    if not token:
        print('No token you fool')
        return ({'message': 'Token is missing'}), 401
        
    try:
        data = jwt.decode(token, os.environ.get("TOKEN_SECRET"), algorithms=["HS256"])
        current_user = data["user_id"]
        print(current_user)
    except ExpiredSignatureError:
        print('This token has expired get a new one!')
        return (None, 401)
    except:
        print('This isn\'t a real token nice try')
        return (None, 401)
    
    return (current_user, 200)