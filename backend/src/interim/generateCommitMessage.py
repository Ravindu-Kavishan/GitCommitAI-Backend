# from fastapi import APIRouter, HTTPException, Request
# from backend.src.functions.commit_message_generator import CommitMessageGenerator
# from backend.src.functions.commit_message_handler import CommitMessageHandler
# from backend.src.models.commitModel import GitDiffRequest
# from backend.src.config import db 


# router = APIRouter()

# @router.post("/generate-commit-message/")
# async def generate_commit_message_endpoint(request: GitDiffRequest):
#     try:
#         # Get the Git diff and message type from the request
#         diff = request.diff
#         message_type = request.message_type
#         project_name = request.project_name

#         # Set instruction based on message_type
#         if message_type == "singleline":
#             instruction = "Given the following git diff,generate only a single line commit message, covering all the changes:"
#         elif message_type == "multiline":
#             instruction = "Given the following git diff,generate only a commit message as multiple simple few points, covering all the changes:"
#         else:
#             raise HTTPException(status_code=400, detail="Invalid message_type. It must be either 'singleline' or 'multiline'.")

#         project = await db["projects"].find_one({"project_name": request.project_name})
    
#         if not project:
#             raise HTTPException(status_code=404, detail="Project not found")
        
#         rules = project.get("rules", [])
#         # Initialize CommitMessageGenerator and generate the commit message
#         generator = CommitMessageGenerator()
#         commit_message = generator.generate_commit_message(diff, instruction)

#         # Initialize CommitMessageHandler and apply company rules
#         commit_handler = CommitMessageHandler()
#         final_commit_message = commit_handler.generate_commit_message(commit_message, rules,project_name)

#         # Return the final commit message as a JSON response
#         print({"commit_message": final_commit_message})
#         return {"commit_message": final_commit_message}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error generating commit message: {str(e)}")

from fastapi import APIRouter, HTTPException
from backend.src.functions.commit_message_generator import CommitMessageGenerator
from backend.src.functions.commit_message_handler import CommitMessageHandler
from backend.src.models.commitModel import GitDiffRequest
from backend.src.config import db

router = APIRouter()

@router.post("/generate-commit-message/")
async def generate_commit_message_endpoint(request: GitDiffRequest):
    try:
        diff = request.diff
        message_type = request.message_type
        project_name = request.project_name

        if message_type == "singleline":
            instruction = (
                "Given the following git diff, generate only a single-line commit message, "
                "covering all the changes:"
            )
        elif message_type == "multiline":
            instruction = (
                "Given the following git diff, generate a commit message in multiple simple points, "
                "covering all the changes:"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid message_type. Must be 'singleline' or 'multiline'."
            )

        project = await db["projects"].find_one({"project_name": project_name})
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        rules = project.get("rules", [])

        generator = CommitMessageGenerator()
        raw_commit_message = generator.generate_commit_message(diff, instruction)

        commit_handler = CommitMessageHandler()
        final_commit_message = commit_handler.generate_commit_message(
            raw_commit_message, rules, project_name
        )

        # 🔒 Ensure it's always a string
        if isinstance(final_commit_message, dict):
            final_commit_message = final_commit_message.get("commit_message", "")

        print("Final commit message to return:", final_commit_message)
        return {"commit_message": final_commit_message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating commit message: {str(e)}")
