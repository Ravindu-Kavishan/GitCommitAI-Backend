from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from commit_message_generator import CommitMessageGenerator
from commit_message_handler import CommitMessageHandler
from manual_commit_handler import ManualCommitHandler

# FastAPI app initialization
app = FastAPI()

# Pydantic model to define request structure
class GitDiffRequest(BaseModel):
    diff: str
    message_type: str  # 'singleline' or 'multiline'


@app.post("/generate-commit-message/")
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
        commit_message = generator.generate_commit_message(diff, instruction)
        print(commit_message)

        # Initialize CommitMessageHandler and apply company rules
        commit_handler = CommitMessageHandler()
        final_commit_message = commit_handler.generate_commit_message(commit_message)
        print(final_commit_message)

        # Return the final commit message as a JSON response
        return {"commit_message": final_commit_message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating commit message: {str(e)}")




# Pydantic model to define request structure
class CommitMessageRequest(BaseModel):
    commit_message: str




@app.post("/generate-commit-suggestions/")
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
