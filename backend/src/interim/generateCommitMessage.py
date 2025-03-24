from fastapi import APIRouter, HTTPException, Request
import requests
import json

router = APIRouter()

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
API_KEY = "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"

@router.post("/generate-commit-message/")
async def generate_commit_message(request: Request):
    body = await request.json()
    diff = body.get("diff")
    message_type = body.get("message_type")

    if not diff or not message_type:
        raise HTTPException(status_code=400, detail="Both 'diff' and 'message_type' are required.")

    prompt_map = {
        "singleline": "Given the following git diff, generate only a single line commit message, covering all the changes:",
        "multiline": "Given the following git diff, generate only a commit message as multiple simple few points, covering all the changes:"
    }

    if message_type not in prompt_map:
        raise HTTPException(status_code=400, detail="Invalid 'message_type'. Use 'singleline' or 'multiline'.")

    prompt = f"{prompt_map[message_type]}\n{diff}"

    response = requests.post(
        url=OPENROUTER_API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "<YOUR_SITE_URL>",
            "X-Title": "<YOUR_SITE_NAME>",
        },
        data=json.dumps({
            "model": "qwen/qwen-2.5-coder-32b-instruct:free",
            "messages": [{"role": "user", "content": prompt}]
        })
    )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to generate commit message.")

    content = response.json().get('choices', [{}])[0].get('message', {}).get('content', "No content generated.")
    return {"commit_message": content}
