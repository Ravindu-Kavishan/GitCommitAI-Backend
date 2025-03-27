from fastapi import HTTPException, APIRouter, Request
from fastapi.responses import JSONResponse
from src.config import db  

router = APIRouter()

@router.post("/admin/get_projects_and_rules")
async def get_projects_and_rules(request: Request):
    try:
        # Extract the email from the cooki

        # Query the database to find matching projects
        projects = await db.projects.find().to_list(length=None)

        # Extract project names and rules
        result = [
            {"project_name": project["project_name"], "rules": project["rules"]}
            for project in projects
        ]

        if not result:
            return JSONResponse(content={"message": "Project not found."}, status_code=404)

        return JSONResponse(content={"projects": result}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
