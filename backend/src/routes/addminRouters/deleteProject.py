from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from backend.src.config import db  

router = APIRouter()

# Pydantic model for the request body
class ProjectDeleteRequest(BaseModel):
    project_name: str

@router.delete("/delete_project")
async def delete_project(data: ProjectDeleteRequest):
    try:
        # Attempt to delete the project
        result = await db.projects.delete_one({"project_name": data.project_name})

        if result.deleted_count == 0:
            return JSONResponse(content={"message": "Project not found."}, status_code=404)

        
        return JSONResponse(content={"message": "Project deleted successfully."}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
