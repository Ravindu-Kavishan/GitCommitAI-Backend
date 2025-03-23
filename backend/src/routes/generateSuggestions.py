from fastapi import FastAPI, HTTPException,APIRouter
from pydantic import BaseModel
from src.functions.manual_commit_handler import ManualCommitHandler
from src.models.commitModel import CommitMessageRequest

router = APIRouter()

@router.post("/generate-commit-suggestions/")
async def generate_commit_message_suggestions(request: CommitMessageRequest):
    try:
        commit_message_example = request.commit_message

        # Initialize the commit handler
        handler = ManualCommitHandler()

        # Generate commit message suggestions as a paragraph
        suggestions = handler.generate_commit_message(commit_message_example)

        # Split the suggestions into lines, remove empty lines,
        # and optionally remove a header like "Suggestions:" if present.
        suggestion_lines = [
            line.strip() 
            for line in suggestions.split('\n') 
            if line.strip() and not line.strip().startswith("Suggestions:")
        ]

        # Return the array of suggestion lines in the response
        return {"suggestions": suggestion_lines}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating commit suggestions: {str(e)}")
