import os
from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv

# ✅ Load environment variables from .env file
load_dotenv()

# ✅ Get the API key from the environment
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise RuntimeError("GOOGLE_API_KEY is not set in environment variables.")

# ✅ Configure the GenAI client
genai.configure(api_key=api_key)

# ✅ Initialize the model
model = genai.GenerativeModel("gemini-2.0-flash")

# ✅ Define FastAPI router
router = APIRouter()

# ✅ Request model
class CommitRequest(BaseModel):
    commit_msg: str
    git_diff: str

# ✅ AI prediction logic
def get_suggested_word(commit_msg: str, git_diff: str) -> str:
    prompt = (
        "You are an AI assistant that helps a user complete a manual commit message by suggesting the next word.\n"
        f"Commit message so far: {commit_msg}\n\n"
        f"Git diff:\n{git_diff}\n\n"
        "Instructions:\n"
        "- Return only the next word in the commit message.\n"
        "- If the message is complete, return 'done'.\n"
        "- If the message is empty, return a starting word.\n"
        "- Keep the message concise and relevant to the diff."
    )
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        raise RuntimeError(f"Prediction failed: {str(e)}")

# ✅ POST endpoint
@router.post("/nextWord")
def suggest_next_word(request: CommitRequest):
    try:
        suggestion = get_suggested_word(request.commit_msg, request.git_diff)
        return {"next_word": suggestion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
