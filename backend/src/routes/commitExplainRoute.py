from fastapi import APIRouter, HTTPException
from backend.src.functions.commit_explanation_handler import CommitExplanationHandler
from pydantic import BaseModel
from rich.console import Console
from rich.markdown import Markdown
from fastapi.responses import JSONResponse

router = APIRouter()

class CommitRequest(BaseModel):
    diff: str = ""

@router.post("/generate_commit_review")
async def generate_commit_review(request: CommitRequest):
    bot = CommitExplanationHandler()

    try:
        explanation = bot.generate_commit_review(request.diff)
        if not explanation:
            return JSONResponse(content={"message": "Commit review not generated."}, status_code=404)


        return {"commit_review": explanation}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating commit review: {str(e)}")
