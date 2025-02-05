from fastapi import FastAPI
from pydantic import BaseModel
from llama_cpp import Llama  

app = FastAPI()

# Load the GGUF model when the server starts
gguf_model_path = "qwen0.5-finetuned.gguf"
modelGGUF = Llama(
    model_path=gguf_model_path,
    rope_scaling={"type": "linear", "factor": 2.0},
    chat_format=None,  # Disables any chat formatting
    n_ctx=32768,
)

# Define the commit message prompt
commit_prompt = """Generate a meaningful commit message explaining the provided Git diff.

### Git Diff:
{}

### Commit Message:""" 

# Request model
class GitDiffRequest(BaseModel):
    git_diff: str

@app.post("/generateCommit")
def process_message(request: GitDiffRequest):
    # Format input for the model
    input_prompt = commit_prompt.format(request.git_diff)

    # Generate commit message
    output = modelGGUF(
        input_prompt,
        max_tokens=64,
        temperature=0.5,
        top_p=0.9,
        top_k=50,
    )

    # Extract and return the generated message
    commit_message = output["choices"][0]["text"].strip()
    return {"commit_message": commit_message}

