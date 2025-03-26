from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from src.config import db  # Assuming db is your database instance
from fastapi.responses import JSONResponse

# FastAPI router initialization
router = APIRouter()

# Define the Commit Pydantic model
class Commit(BaseModel):
    commit_id: str
    commit_message: str
    git_diff: str

# Define the Project Pydantic model
class Project(BaseModel):
    project_name: str
    user_id:str
    commits: list[Commit]  # A list of commits

# Endpoint to add a project with commits to the database
@router.post("/add_project_Commit")
async def add_project(project: Project):
    try:
        # Convert the Pydantic model to a dictionary for insertion
        project_dict = project.dict()
        
        # Insert the project document into the projects collection
        result = await db.projects.insert_one(project_dict)
        
        # Return the inserted ID
        return JSONResponse(content={"id": str(result.inserted_id)}, status_code=201)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
