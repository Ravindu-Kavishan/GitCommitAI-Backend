from fastapi import APIRouter, HTTPException, Depends
from backend.src.dal.user_dal import create_user, get_all_users, get_user_by_id, update_user, delete_user
from backend.src.models.userModel import User
from backend.src.dependencies.auth_dependancy import get_current_user  
from fastapi import Depends


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

@router.put("/users/{user_id}")
async def update_user_data(user_id: str, user: User, current_user: dict = Depends(get_current_user)):
    result = await update_user(user_id, user)
    if result["message"] == "User not found":
        raise HTTPException(status_code=404, detail="User not found")
    return result

@router.delete("/users/{user_id}")
async def delete_user_data(user_id: str):
    result = await delete_user(user_id)
    if result["message"] == "User not found":
        raise HTTPException(status_code=404, detail="User not found")
    return result
