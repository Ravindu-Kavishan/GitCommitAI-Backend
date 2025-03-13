import os
from dotenv import load_dotenv
from openai import OpenAI


class ManualCommitHandler:
    load_dotenv('.env')
    LLAMA_URL = os.getenv('LLAMA_URL')
    LLAMA_KEY = os.getenv('LLAMA_KEY')

    def __init__(self,faiss_index_file="faiss_rules.index", rules_file="rules.txt"):
        # Initialize the OpenAI client and the Sentence Transformer model
        self.client = OpenAI(
            base_url=self.LLAMA_URL,
            api_key=self.LLAMA_KEY
        )
        self.RULES_FILE = rules_file

    def retrieve_all_rules(self):

        with open(self.RULES_FILE, "r") as f:
            rules = [line.strip() for line in f.readlines()]

        return rules

    def generate_commit_message(self, commit_message_example):
        company_rules = self.retrieve_all_rules()

        if not company_rules:
            return commit_message_example  # "No relevant rules found. Please define company guidelines first."

        prompt = (
            "You are an AI assistant that reviews commit messages to ensure they follow company guidelines.\n"
            "Below are the company rules that must be strictly followed:\n\n"
            f"{chr(10).join(company_rules)}\n\n"
            "Give short suggestions on how to apply the given rules and improve the given commit message.\n"
            "Do not mention anything about the rules that's already been followed by the commit message.\n"
            "Keep it concise.\n"
            "Give an example commit message at the end.\n\n"
            "Commit message:\n"
            f"{commit_message_example}"
        )


        completion = self.client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=[{"role": "user", "content": prompt}]
        )

        return completion.choices[0].message.content.strip()
