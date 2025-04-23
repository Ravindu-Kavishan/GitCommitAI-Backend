import os
import faiss
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient


class CommitMessageHandler1:

    def __init__(self, faiss_index_file="faiss_rules.index", mongo_uri="mongodb://localhost:27017", db_name="commit_DB", collection_name="projects"):
        # Initialize the OpenAI client and the Sentence Transformer model
        self.client = OpenAI(
            base_url=os.getenv('LLAMA_URL'),
            api_key=os.getenv('LLAMA_KEY')
        )
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.FAISS_INDEX_FILE = faiss_index_file

        # MongoDB setup
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client[db_name]
        self.collection = self.db[collection_name]

    def get_embedding(self, text):
        # Generate the embedding
        embedding = self.model.encode(text)
        return np.array(embedding).astype('float32')

    def initialize_faiss(self):
        if os.path.exists(self.FAISS_INDEX_FILE):
            return faiss.read_index(self.FAISS_INDEX_FILE)
        else:
            return faiss.IndexFlatL2(384)

    def store_project_rules(self, project_name):
        # Fetch rules dynamically for the selected project from MongoDB
        project = self.collection.find_one({"project_name": project_name}, {"_id": 0, "rules": 1})
        if not project or "rules" not in project:
            print(f"No rules found for project: {project_name}")
            return

        rules = project["rules"]

        embeddings = self.get_embedding(rules)

        index = self.initialize_faiss()
        index.add(embeddings)

        # Save FAISS index
        faiss.write_index(index, self.FAISS_INDEX_FILE)
        print(f"FAISS index created with {len(rules)} rules for project: {project_name}")

    def retrieve_project_rules(self, project_name):
        # Fetch rules dynamically for the selected project from MongoDB
        project = self.collection.find_one({"project_name": project_name}, {"_id": 0, "rules": 1})
        if not project or "rules" not in project:
            print(f"No rules found for project: {project_name}")
            return []

        return project["rules"]

    def generate_commit_message(self, commit_message_example, project_name):
        self.store_project_rules(project_name)
        project_rules = self.retrieve_project_rules(project_name)

        if not project_rules:
            return commit_message_example  # "No relevant rules found. Please define project guidelines first."

        prompt = (
            "You are an AI assistant that reviews commit messages to ensure they follow project-specific guidelines.\n"
            "Below are the project rules that must be strictly followed:\n\n"
            f"{chr(10).join(project_rules)}\n\n"
            "Rewrite the following commit message to fully comply with these rules. Stay within the context of the commit message and do not assume any content that is not in the commit message."
            "Respond with only the corrected commit message, nothing else:\n\n"
            f"{commit_message_example}"
        )

        completion = self.client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content.strip()