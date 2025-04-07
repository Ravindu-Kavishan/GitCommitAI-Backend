from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.src.config import db  

router = APIRouter()

# Pydantic model for the request body
class UserAddRequest(BaseModel):
    project_name: str
    user: str

@router.post("/add_user")
async def add_user(data: UserAddRequest):
    try:
        # Attempt to update the project by adding the new user
        result = await db.projects.update_one(
            {"project_name": data.project_name},
            {"$addToSet": {"users": data.user}}  # Prevents duplicates
        )

        if result.matched_count == 0:
            return JSONResponse(content={"message": "Project not found."}, status_code=404)
        
        if result.modified_count == 0:
            return JSONResponse(content={"message": "User already exists in the project."}, status_code=400)
        
        return JSONResponse(content={"message": "User added successfully."}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
