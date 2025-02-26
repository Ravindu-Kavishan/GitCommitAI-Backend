import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession

# Load environment variables
load_dotenv('.env')
LLAMA_URL = os.environ.get('LLAMA_URL')
LLAMA_KEY = os.environ.get('LLAMA_KEY')
SERVICE_ACCOUNT_KEY_FILE = os.environ.get('SERVICE_ACCOUNT_KEY_FILE')
ENDPOINT_URL = os.environ.get('ENDPOINT_URL')

# FastAPI app initialization
app = FastAPI()

class CommitMessageHandler:
    def __init__(self, faiss_index_file="faiss_rules.index", rules_file="rules.txt"):
        # Initialize the OpenAI client and the Sentence Transformer model
        self.client = OpenAI(
            base_url=LLAMA_URL,
            api_key=LLAMA_KEY
        )
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.FAISS_INDEX_FILE = faiss_index_file
        self.RULES_FILE = rules_file

    def get_embedding(self, text):
        # Generate the embedding
        embedding = self.model.encode(text)
        return np.array(embedding).astype('float32')

    def initialize_faiss(self):
        if os.path.exists(self.FAISS_INDEX_FILE):
            return faiss.read_index(self.FAISS_INDEX_FILE)
        else:
            return faiss.IndexFlatL2(384)

    def store_company_rules(self):
        if not os.path.exists(self.RULES_FILE):
            print("rules.txt does not exist.")
            return

        # Load all rules
        with open(self.RULES_FILE, "r") as f:
            rules = [line.strip() for line in f.readlines() if line.strip()]

        if not rules:
            print("rules.txt is empty!")
            return

        embeddings = self.get_embedding(rules)

        index = self.initialize_faiss()
        index.add(embeddings)

        # Save FAISS index
        faiss.write_index(index, self.FAISS_INDEX_FILE)
        print(f"FAISS index created with {len(rules)} rules.")

    def retrieve_all_rules(self):
        index = self.initialize_faiss()

        if not os.path.exists(self.RULES_FILE) or index.ntotal == 0:
            return []

        with open(self.RULES_FILE, "r") as f:
            rules = [line.strip() for line in f.readlines()]

        return rules

    def generate_commit_message(self, commit_message_example):
        self.store_company_rules()
        company_rules = self.retrieve_all_rules()

        if not company_rules:
            return commit_message_example  

        prompt = (
            "You are an AI assistant that reviews commit messages to ensure they follow company guidelines.\n"
            "Below are the company rules that must be strictly followed:\n\n"
            f"{chr(10).join(company_rules)}\n\n"
            "Rewrite the following commit message to fully comply with these rules. Stay within the context of the commit message and do not assume any content that is not in the commit message."
            "Respond with only the corrected commit message, nothing else:\n\n"
            f"{commit_message_example}"
        )

        completion = self.client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content.strip()


class CommitMessageGenerator:
    def generate_commit_message(self, git_diff, instructions):
        # Load the service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_KEY_FILE,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )

        # Create an authorized session
        authed_session = AuthorizedSession(credentials)

        # Prepare the request payload
        payload = {
            "instances": [
                {
                    "inputs": f"<|im_start|>system\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.<|im_end|>\n<|im_start|>user\n{instructions}\n\n{git_diff}<|im_end|>\n<|im_start|>assistant"
                }
            ],
            "parameters": {
                "max_new_tokens": 128,
                "temperature": 0.5
            }
        }

        # Send the request
        response = authed_session.post(ENDPOINT_URL, json=payload)

        # Handle the response
        if response.status_code == 200:
            # Extract the assistant's message
            assistant_message = response.json()["predictions"][0]

            # Remove code block markers if present
            if "```" in assistant_message:
                lines = assistant_message.split("\n")
                commit_message = "\n".join(lines[1:-1]).replace("```", "").strip()
            else:
                commit_message = assistant_message.strip()

            # Remove lines starting with '###'
            lines = commit_message.splitlines()
            filtered_lines = [line for line in lines if not line.strip().startswith("###")]
            cleaned_commit_message = "\n".join(filtered_lines).strip()

            return cleaned_commit_message
        else:
            raise Exception(f"Failed to get response: {response.status_code}, {response.text}")

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
            instruction = "Given the following git diff, generate only a single-line commit message, covering all the changes:"
        elif message_type == "multiline":
            instruction = "Given the following git diff, generate a commit message as multiple simple points, covering all the changes:"
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
