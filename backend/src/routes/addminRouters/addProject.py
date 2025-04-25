from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.src.config import db  

router = APIRouter()

# Pydantic model for the request body
class ProjectAddRequest(BaseModel):
    project_name: str
    rules: list[str]
    users: list[str]

@router.post("/add_project")
async def add_project(data: ProjectAddRequest):
    try:
        # Check if a project with the same name already exists
        existing_project = await db.projects.find_one({"project_name": data.project_name})
        if existing_project:
            return JSONResponse(content={"message": "Project with this name already exists.."}, status_code=400)
        
        
        # Insert the new project if no duplicate is found
        new_project = {
            "project_name": data.project_name,
            "rules": data.rules,
            "users": data.users
        }
        await db.projects.insert_one(new_project)
        
        return JSONResponse(content={"message": "Project added successfully."}, status_code=201)

    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
