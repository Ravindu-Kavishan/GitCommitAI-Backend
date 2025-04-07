from fastapi import Form, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from backend.src.dal.user_dal import get_user_by_username
from passlib.context import CryptContext
from backend.src.utils import create_access_token
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# You can move this to your .env file
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_HASHED_PASSWORD = os.getenv("ADMIN_PASSWORD_HASH")
ADMIN_ID = "admin-001"  # Fixed admin ID

@router.post("/login")
async def login(request: Request, username: str = Form(None), password: str = Form(None)):
    # Handle JSON or form data
    try:
        if not username or not password:
            body = await request.json()
            username = body.get("username")
            password = body.get("password")
    except Exception:
        pass

    if not username or not password:
        return JSONResponse(status_code=400, content={"detail": "Username and password required"})

    # ADMIN LOGIN BLOCK
    if username == ADMIN_USERNAME:
        if not ADMIN_HASHED_PASSWORD:
            return JSONResponse(status_code=500, content={"detail": "Admin password not configured"})

        if pwd_context.verify(password, ADMIN_HASHED_PASSWORD):
            token = create_access_token(data={"sub": ADMIN_ID}, expires_delta=timedelta(minutes=30))
            return {
                "userId": ADMIN_ID,
                "message": "Admin login successful",
                "access_token": token,
                "token_type": "bearer",
                "role": "admin"
            }
        else:
            return JSONResponse(status_code=401, content={"detail": "Invalid admin credentials"})

    # NORMAL USER LOGIN BLOCK
    user = await get_user_by_username(username)
    if not user or not pwd_context.verify(password, user["password"]):
        return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})

    token = create_access_token(data={"sub": user["id"]}, expires_delta=timedelta(minutes=30))
    return {
        "userId": user["id"],
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "role": "user"
    }
