from fastapi import APIRouter, HTTPException, Request
from backend.src.functions.commit_message_generator import CommitMessageGenerator
from backend.src.functions.commit_message_handler import CommitMessageHandler
from backend.src.models.commitModel import GitDiffRequest
from backend.src.config import db 


router = APIRouter()

# @router.post("/generate-commit-message/")
# async def generate_commit_message(request: Request):
#     body = await request.json()
#     diff = body.get("diff")
#     message_type = body.get("message_type")

#     if not diff or not message_type:
#         raise HTTPException(status_code=400, detail="Both 'diff' and 'message_type' are required.")

#     prompt_map = {
#         "singleline": "Given the following git diff, generate only a single line commit message, covering all the changes:",
#         "multiline": "Given the following git diff, generate only a commit message as multiple simple few points, covering all the changes:"
#     }

#     if message_type not in prompt_map:
#         raise HTTPException(status_code=400, detail="Invalid 'message_type'. Use 'singleline' or 'multiline'.")

#     prompt = f"{prompt_map[message_type]}\n{diff}"

#     response = requests.post(
#         url=OPENROUTER_API_URL,
#         headers={
#             "Authorization": f"Bearer {API_KEY}",
#             "Content-Type": "application/json",
#             "HTTP-Referer": "<YOUR_SITE_URL>",
#             "X-Title": "<YOUR_SITE_NAME>",
#         },
#         data=json.dumps({
#             "model": "qwen/qwen-2.5-coder-32b-instruct:free",
#             "messages": [{"role": "user", "content": prompt}]
#         })
#     )

#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail="Failed to generate commit message.")

#     content = response.json().get('choices', [{}])[0].get('message', {}).get('content', "No content generated.")
#     return {"commit_message": content}


@router.post("/generate-commit-message/")
async def generate_commit_message_endpoint(request: GitDiffRequest):
    try:
        # Get the Git diff and message type from the request
        diff = request.diff
        message_type = request.message_type
        project_name = request.project_name

        # Set instruction based on message_type
        if message_type == "singleline":
            instruction = "Given the following git diff,generate only a single line commit message, covering all the changes:"
        elif message_type == "multiline":
            instruction = "Given the following git diff,generate only a commit message as multiple simple few points, covering all the changes:"
        else:
            raise HTTPException(status_code=400, detail="Invalid message_type. It must be either 'singleline' or 'multiline'.")

        project = await db["projects"].find_one({"project_name": request.project_name})
    
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        rules = project.get("rules", [])
        # Initialize CommitMessageGenerator and generate the commit message
        generator = CommitMessageGenerator()
        commit_message = generator.generate_commit_message(diff, instruction)
        print(commit_message)

        # Initialize CommitMessageHandler and apply company rules
        commit_handler = CommitMessageHandler()
        final_commit_message = commit_handler.generate_commit_message(commit_message, rules,project_name)
        print(final_commit_message)

        # Return the final commit message as a JSON response
        return {"commit_message": final_commit_message}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating commit message: {str(e)}")