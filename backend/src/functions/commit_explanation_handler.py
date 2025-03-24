import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown


class CommitExplanationHandler:

    def __init__(self, faiss_index_file="faiss_rules.index", rules_file="rules.txt"):
        load_dotenv('.env')
        LLAMA_URL = os.getenv('LLAMA_URL')
        LLAMA_KEY = os.getenv('LLAMA_KEY')

        if not LLAMA_URL or not LLAMA_KEY:
            raise ValueError("Environment variables LLAMA_URL or LLAMA_KEY are missing.")

        # Initialize the OpenAI client and the Sentence Transformer model
        self.client = OpenAI(
            base_url=LLAMA_URL,
            api_key=LLAMA_KEY
        )

    def generate_commit_review(self, diff):
        prompt = (
            "You are an AI assistant that explains a given git difference to a user briefly.\n"
            "Below is the git difference to be explained:\n"
            f"{diff}\n"
        )

        try:
            completion = self.client.chat.completions.create(
                model="meta-llama/Llama-3-70b-instruct",
                messages=[{"role": "user", "content": prompt}]
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logging.error(f"Error generating commit review: {str(e)}", exc_info=True)
            return "Failed to generate commit review. Please try again."
