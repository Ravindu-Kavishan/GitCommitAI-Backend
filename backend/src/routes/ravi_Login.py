from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from src.config import db  # Assuming db is your MongoDB instance
from fastapi.security import OAuth2PasswordBearer
from bson import ObjectId

# Router Initialization
router = APIRouter()

# OAuth2 scheme for security
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Define the User Pydantic model
class LoginData(BaseModel):
    username: str
    password: str

# Endpoint to log in using username and password
@router.post("/login")
async def login(data: LoginData):
    try:
        # Search for the user in the database
        user = await db.users.find_one({"username": data.username})
        
        # If user not found
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Password verification (assuming passwords are stored in plain text)
        if user["password"] != data.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        # Successful login response
        return {
            "message": "Login successful",
            "user_id": str(user["_id"]),
            "username": user["username"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
