from backend.src.config import db
from backend.src.models.userModel import User
from bson import ObjectId

def user_serializer(user) -> dict:
    return{
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"]
    }

