from fastapi import HTTPException, APIRouter, Request
from fastapi.responses import JSONResponse
from backend.src.config import db  

router = APIRouter()

@router.post("/admin/get_projects_and_rules")
async def get_projects_and_rules(request: Request):
    try:
        # Query the database to find matching projects
        projects = await db.projects.find({}, {"project_name": 1, "rules": 1}).to_list(length=None)
        result = [
            {
                "project_name": project.get("project_name", "Unnamed Project"),
                "rules": project.get("rules", [])
            }
            for project in projects
        ]

        if not result:
            return JSONResponse(content={"message": "Project not found."}, status_code=404)

        return JSONResponse(content={"projects": result}, status_code=200)

    except Exception as e:
        # Optionally, log the exception
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
