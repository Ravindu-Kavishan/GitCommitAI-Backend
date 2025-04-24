from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bson.objectid import ObjectId
from backend.src.config import db 

router = APIRouter()

class ProjectRequest(BaseModel):
    project_name: str

@router.post("/get_rules")
async def get_rules(request: ProjectRequest):
    project = await db["projects"].find_one({"project_name": request.project_name})
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    rules = project.get("rules", [])
    return {"rules": rules}
