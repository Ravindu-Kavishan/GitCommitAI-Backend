from fastapi import APIRouter, HTTPException, Depends
from backend.src.dal.user_dal import create_user, get_all_users, get_user_by_id
from backend.src.models.userModel import User

router = APIRouter()

@router.post("/users/")
async def add_user(user: User):
    user_id = await create_user(user)
    return {"message": "User created", "id": user_id}

@router.get("/users/")
async def fetch_users():
    return await get_all_users()

@router.get("/users/{user_id}")
async def fetch_user(user_id: str):
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user