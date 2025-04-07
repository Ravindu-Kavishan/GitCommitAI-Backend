from backend.src.config import db
from backend.src.models.userModel import User
from bson import ObjectId
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def user_serializer(user) -> dict:
    return{
        "id": str(user["_id"]),
        "username": user["username"],
        "contact": user["contact"],
        "email": user["email"],
        "password": user["password"]
    }

#create a new user
async def create_user(user: User):
    user_dict = user.dict(exclude={"id"})
    user_dict["password"] = pwd_context.hash(user_dict["password"])  # Hash password here
    result = await db.users.insert_one(user_dict)
    print("Hashed password:", user_dict["password"])

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

#get user by username
async def get_user_by_username(username: str):
    user = await db.users.find_one({"username": username})
    if user:
        return user_serializer(user)
    return None

#update a user
async def update_user(user_id: str, user_data: User):
    user_dict = user_data.dict(exclude={"id"})
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": user_dict}
    )
    if result.matched_count:
        return {"message": "User updated successfully"}
    return {"message": "User not found"}

#delete a user
async def delete_user(user_id: str):
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count:
        return {"message": "User Deleted SUccessfully"}
    return {"message": "User not found"}

