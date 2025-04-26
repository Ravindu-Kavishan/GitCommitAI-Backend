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
            return JSONResponse(content={"message": "Project with this name already exists."}, status_code=400)

        # Check whether all users (emails) exist in the users collection
        existing_users = await db.users.find({"email": {"$in": data.users}}).to_list(length=None)
        existing_emails = {user["email"] for user in existing_users}

        missing_users = [email for email in data.users if email not in existing_emails]
        if missing_users:
            return JSONResponse(
                content={"message": "Some users not found.", "missing_users": missing_users},
                status_code=404
            )

        # Insert the new project if no duplicate and users exist
        new_project = {
            "project_name": data.project_name,
            "rules": data.rules,
            "users": data.users
        }
        await db.projects.insert_one(new_project)

        return JSONResponse(content={"message": "Project added successfully."}, status_code=201)

    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
