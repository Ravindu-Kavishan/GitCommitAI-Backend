from fastapi import HTTPException, APIRouter, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel  # Added for request body validation
from backend.src.config import db  

router = APIRouter()

# Define the request body model
class EmailRequest(BaseModel):
    email: str

@router.post("/get_projects_and_commits")  # Changed to POST to accept body data
async def get_user_projects(request_data: EmailRequest):
    try:
        # Extract the email from the request body
        email = request_data.email

        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )

        # Retrieve all projects for the given `email`
        projects = await db.commit_history.find({"email": email}).to_list(None)
        if not projects:
            return JSONResponse(content={"message": "Project not found."}, status_code=404)
        

        # Extract project names, commits, and git_diffs
        result = [
            {
                "project_name": project["project_name"],
                "commits": [
                    {
                        "commit_message": commit["commit_message"],
                        "git_diff": commit["git_diff"]
                    }
                    for commit in project.get("commits", [])
                ],
            }
            for project in projects
        ]

        return JSONResponse(content={"projects": result}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
