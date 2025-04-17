from fastapi import HTTPException, APIRouter, Request
from fastapi.responses import JSONResponse
from backend.src.config import db  

router = APIRouter()

@router.post("/get_projects")
async def get_projects(request: Request):
    try:
        projects = await db.projects.find().to_list(length=None)

        # Extract project names and rules
        result = [
            project["project_name"]
            for project in projects
        ]

        if not result:
            return JSONResponse(content={"message": "Project not found."}, status_code=404)

        return JSONResponse(content={"projects": result}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
