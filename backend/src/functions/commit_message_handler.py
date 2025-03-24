import os
import faiss
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer 


class CommitMessageHandler:

    def __init__(self, faiss_index_file="faiss_rules.index", rules_file="rules.txt"):
        # Initialize the OpenAI client and the Sentence Transformer model
        self.client = OpenAI(
            base_url=os.getenv('LLAMA_URL'),
            api_key=os.getenv('LLAMA_KEY')
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
            return commit_message_example  # "No relevant rules found. Please define company guidelines first."

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




