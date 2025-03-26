from fastapi import APIRouter, HTTPException, status, Response
from pydantic import BaseModel
from src.config import db  # Assuming db is your MongoDB instance
from fastapi.responses import JSONResponse
from bson import ObjectId

# Router Initialization
router = APIRouter()

# Define the User Pydantic model
class LoginData(BaseModel):
    username: str
    password: str

# Endpoint to log in and create a cookie
@router.post("/login")
async def login(data: LoginData, response: Response):
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

        # Set the cookie with the user ID
        response.set_cookie(
            key="email", 
            value=str(user["email"]), 
            httponly=True,  # Prevents JavaScript access to the cookie
            secure=True,    # Ensures the cookie is sent only over HTTPS
            samesite="Strict"  # Prevents cross-site request forgery (CSRF)
        )
        admin = False  # Default to False
        if "admin" in user and user["admin"]:
            admin = True

        # Successful login response
        return {
            "message": "Login successful",
            "user_id": str(user["_id"]),
            "username": user["username"],
            "admin":admin
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
