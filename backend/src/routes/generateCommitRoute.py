from fastapi import FastAPI, HTTPException,APIRouter
from backend.src.functions.commit_message_generator import CommitMessageGenerator
from backend.src.functions.commit_message_handler import CommitMessageHandler
from backend.src.models.commitModel import GitDiffRequest


router = APIRouter()

@router.post("/generate-commit-message/")
async def generate_commit_message_endpoint(request: GitDiffRequest):
    try:
        # Get the Git diff and message type from the request
        diff = request.diff
        message_type = request.message_type

        # Set instruction based on message_type
        if message_type == "singleline":
            instruction = "Given the following git diff,generate only a single line commit message, covering all the changes:"
        elif message_type == "multiline":
            instruction = "Given the following git diff,generate only a commit message as multiple simple few points, covering all the changes:"
        else:
            raise HTTPException(status_code=400, detail="Invalid message_type. It must be either 'singleline' or 'multiline'.")

        # Initialize CommitMessageGenerator and generate the commit message
        generator = CommitMessageGenerator()
        commit_message = generator.generate_commit_message_with_vertexai(diff, instruction)
        print(commit_message)

        # Initialize CommitMessageHandler and apply company rules
        commit_handler = CommitMessageHandler()
        final_commit_message = commit_handler.generate_commit_message(commit_message)
        print(final_commit_message)

        # Return the final commit message as a JSON response
        return {"commit_message": final_commit_message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating commit message: {str(e)}")



