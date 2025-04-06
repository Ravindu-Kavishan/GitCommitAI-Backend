from jose import JWTError, jwt
from datetime import datetime, timedelta

# Secret key & algorithm
SECRET_KEY = "BcCATq44RyIOj5KHySHtoEBIyM4DWERxVnIekYgiqyU"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Decode & verify JWT
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Or extract user_id from payload if needed
    except JWTError:
        return None
