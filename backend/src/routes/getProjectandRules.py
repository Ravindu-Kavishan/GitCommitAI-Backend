from fastapi import HTTPException, APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel  # Added for request body validation
from src.config import db  

router = APIRouter()

# Define the request body model
class EmailRequest(BaseModel):
    email: str

@router.post("/get_projects_and_rules")  # Changed to POST to accept body data
async def get_user_projects(request_data: EmailRequest):
    try:
        # Extract the email from the request body
        user_email = request_data.email

        if not user_email:
            return JSONResponse(content={"message": "User email not provided."}, status_code=400)
        
        # Query the database to find matching projects
        projects = await db.projects.find({"users": user_email}).to_list(length=None)

        # Extract project names and rules
        result = [
            {"project_name": project["project_name"], "rules": project["rules"]}
            for project in projects
        ]

        if not result:
            return JSONResponse(content={"message": "No projects found for this user."}, status_code=404)

        return JSONResponse(content={"projects": result}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
