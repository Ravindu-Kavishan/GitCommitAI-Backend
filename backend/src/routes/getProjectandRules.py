from fastapi import APIRouter, HTTPException, Request, status
from src.config import db
from fastapi.responses import JSONResponse

# Router Initialization
router = APIRouter()

# Endpoint to fetch projects for the authenticated user
@router.get("/get_projects_and_rules")
async def get_user_projects(request: Request):
    # Extract `user_id` from the cookie
    user_id = request.cookies.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not authenticated"
        )

    try:
        # Database connection check
        if db is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database connection error"
            )

        # Retrieve all projects for the given `user_id`
        projects = await db.rules.find({"user_id": user_id}).to_list(None)

        if not projects:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No projects found for this user"
            )

        # Extract project names, commits, and git_diffs
        result = []
        for project in projects:
            if "project_name" not in project:
                continue  # Skip malformed data

            result.append({
                "project_name": project["project_name"],
                "rules": [rule for rule in project["rules"]],
            })

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No valid project data available"
            )

        return JSONResponse(content={"projects": result}, status_code=200)

    except HTTPException as http_err:
        raise http_err  # Re-raise known exceptions

    except ConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
