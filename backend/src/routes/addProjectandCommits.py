from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
from typing import List
from backend.src.config import db
from fastapi.responses import JSONResponse

router = APIRouter()

# Commit schema
class Commit(BaseModel):
    commit_message: str
    git_diff: str

# Project schema
class Project(BaseModel):
    project_name: str
    email: str
    commits: List[Commit]

@router.post("/add_project_commit")
async def add_project_commit(project: Project):
    try:
        # Convert Pydantic commits to dict
        commits_to_add = [commit.dict() for commit in project.commits]

        # Filter by project_name and email
        filter_query = {
            "project_name": project.project_name,
            "email": project.email
        }

        # Update: push new commits to the existing document
        update_result = await db.commit_history.update_one(
            filter_query,
            {"$push": {"commits": {"$each": commits_to_add}}}
        )

        # If no document matched, optionally insert a new one
        if update_result.matched_count == 0:
            # Create a new document
            new_doc = {
                "project_name": project.project_name,
                "email": project.email,
                "commits": commits_to_add
            }
            insert_result = await db.commit_history.insert_one(new_doc)
            return JSONResponse(content={"id": str(insert_result.inserted_id), "message": "New document inserted."}, status_code=201)

        return JSONResponse(content={"message": "Commits added to existing project."}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
