from backend.src.config import db
from backend.src.models.userModel import User
from bson import ObjectId

def user_serializer(user) -> dict:
    return{
        "id": str(user["_id"]),
        "name": user["username"],
        "email": user["email"]
    }

#create a new user
async def create_user(user: User):
    user_dict = user.dict(exclude={"id"})
    result = await db.users.insert_one(user_dict)
    return str(result.inserted_id)

#get all users
async def get_all_users():
    users = await db.users.find().to_list(100)
    return [user_serializer(user) for user in users]

#get user by id
async def get_user_by_id(user_id: str):
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        return user_serializer(user)
    return None

