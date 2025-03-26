from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.config import db  

router = APIRouter()

# Pydantic model for the request body
class RuleDeleteRequest(BaseModel):
    project_name: str
    rule: str

@router.delete("/delete_rule")
async def delete_rule(data: RuleDeleteRequest):
    try:
        # Attempt to update the project by pulling (removing) the rule
        result = await db.projects.update_one(
            {"project_name": data.project_name},
            {"$pull": {"rules": data.rule}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Project not found.")
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="Rule not found in the project.")
        
        return JSONResponse(content={"message": "Rule deleted successfully."}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
