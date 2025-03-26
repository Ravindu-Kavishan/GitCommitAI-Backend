from fastapi import APIRouter, HTTPException, Request, status
from src.config import db
from fastapi.responses import JSONResponse

# Router Initialization
router = APIRouter()

# Endpoint to fetch projects for the authenticated user
@router.get("/get_projects_and_commits")
async def get_user_projects(request: Request):
    # Extract `user_id` from the cookie
    user_id = request.cookies.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )

    try:
        # Retrieve all projects for the given `user_id`
        projects = await db.commit_history.find({"user_id": user_id}).to_list(None)

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
