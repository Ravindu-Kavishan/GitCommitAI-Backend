# import os
# import faiss 
# import numpy as np
# from openai import OpenAI
# from sentence_transformers import SentenceTransformer 
# from dotenv import load_dotenv
# import requests 
# load_dotenv()


# class CommitMessageHandler:

#     def __init__(self, faiss_index_file="faiss_rules.index"):
#         # Initialize the OpenAI client and the Sentence Transformer model
#         self.client = OpenAI(
#             base_url=os.getenv('LLAMA_URL'),
#             api_key=os.getenv('LLAMA_KEY')
#         )
#         self.model = SentenceTransformer('all-MiniLM-L6-v2')
#         self.FAISS_INDEX_FILE = faiss_index_file

#     def get_rules(self, project_name):
#         """
#         Fetch rules dynamically for the given project name by making an API call.
#         """
#         try:
#             #request to the backend API
#             response = requests.post(
#                 "http://localhost:8000/get_rules",
#                 json={"project_name": project_name}
#             )
#             response.raise_for_status()  

            
#             return response.json().get("rules", [])
#         except requests.exceptions.RequestException as e:
#             return []
        
#     def get_embedding(self, texts):
#         """
#         Generate embeddings for a list of texts using the SentenceTransformer model.
#         :param texts: List of strings to generate embeddings for.
#         :return: NumPy array of embeddings.
#         """
#         if isinstance(texts, str):
#             texts = [texts]  # Convert single string to a list
#         return np.array(self.model.encode(texts))
    
#     def initialize_faiss(self):
#         if os.path.exists(self.FAISS_INDEX_FILE):
#             return faiss.read_index(self.FAISS_INDEX_FILE)
#         else:
#             return faiss.IndexFlatL2(384)

#     def store_company_rules(self, rules,project_name):
#         # Fetch rules dynamically using get_rules

#         if not rules:
#             print(f"No rules found for project: {project_name}")
#             return

#         embeddings = self.get_embedding(rules)

#         index = self.initialize_faiss()
#         index.add(embeddings)

#         # Save FAISS index
#         faiss.write_index(index, self.FAISS_INDEX_FILE)
#         print(f"FAISS index created with {len(rules)} rules for project: {project_name}.")

#     def retrieve_best_rules(self, commit_message, rules,project_name, top_k=5):

#         if not rules:
#             print(f"No rules found for project: {project_name}")
#             return []

#         # Load FAISS index
#         index = self.initialize_faiss()

#         if index.ntotal == 0:
#             print("FAISS index is empty!")
#             return []

#         # Embed the commit message
#         query_vector = self.get_embedding(commit_message['commit_message']).reshape(1, -1)

        
#         distances, indices = index.search(query_vector, top_k)

        
#         best_rules = [rules[i] for i in indices[0] if i < len(rules)]
#         print(best_rules)
#         return best_rules

#     def generate_commit_message(self, commit_message_example, rules,project_name):
#         self.store_company_rules(rules,project_name)
#         company_rules = self.retrieve_best_rules(commit_message_example,rules ,project_name)
#         print(company_rules)

#         if not company_rules:
#             return commit_message_example  
#         prompt = (
#             "You are an AI assistant that reviews commit messages to ensure they follow company guidelines.\n"
#             "Below are the company rules that must be strictly followed:\n\n"
#             f"{chr(10).join(company_rules)}\n\n"
#             "Rewrite the following commit message to fully comply with these rules. Stay within the context of the commit message and do not assume any content that is not in the commit message."
#             "Respond with only the corrected commit message, nothing else:\n\n"
#             f"{commit_message_example}"
#         )

#         completion = self.client.chat.completions.create(
#             model="meta-llama/llama-3.3-70b-instruct",
#             messages=[{"role": "user", "content": prompt}]
#         )
#         print(completion.choices[0].message.content)
#         return completion.choices[0].message.content.strip()


import os
import faiss
import numpy as np
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()

class CommitMessageHandler:
    def __init__(self, faiss_index_file="faiss_rules.index"):
        self.client = OpenAI(
            base_url=os.getenv("LLAMA_URL"),
            api_key=os.getenv("LLAMA_KEY")
        )
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.FAISS_INDEX_FILE = faiss_index_file

    def get_rules(self, project_name):
        try:
            response = requests.post(
                "http://localhost:8000/get_rules",
                json={"project_name": project_name}
            )
            response.raise_for_status()
            return response.json().get("rules", [])
        except requests.exceptions.RequestException:
            return []

    def get_embedding(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        return np.array(self.model.encode(texts))

    def initialize_faiss(self):
        if os.path.exists(self.FAISS_INDEX_FILE):
            return faiss.read_index(self.FAISS_INDEX_FILE)
        return faiss.IndexFlatL2(384)

    def store_company_rules(self, rules, project_name):
        if not rules:
            print(f"No rules found for project: {project_name}")
            return

        embeddings = self.get_embedding(rules)
        index = self.initialize_faiss()
        index.add(embeddings)
        faiss.write_index(index, self.FAISS_INDEX_FILE)
        print(f"FAISS index created with {len(rules)} rules for project: {project_name}")

    def retrieve_best_rules(self, commit_message, rules, project_name, top_k=5):
        if not rules:
            print(f"No rules found for project: {project_name}")
            return []

        index = self.initialize_faiss()
        if index.ntotal == 0:
            print("FAISS index is empty!")
            return []

        query_vector = self.get_embedding(commit_message).reshape(1, -1)
        distances, indices = index.search(query_vector, top_k)
        best_rules = [rules[i] for i in indices[0] if i < len(rules)]

        print("Best matched rules:", best_rules)
        return best_rules

    def generate_commit_message(self, commit_message_example, rules, project_name):
        # 🔒 Ensure the input is a string
        if isinstance(commit_message_example, dict):
            commit_message_example = commit_message_example.get("commit_message", "")

        self.store_company_rules(rules, project_name)
        company_rules = self.retrieve_best_rules(commit_message_example, rules, project_name)

        if not company_rules:
            return commit_message_example

        prompt = (
            "You are an AI assistant that reviews commit messages to ensure they follow company guidelines.\n"
            "Below are the company rules that must be strictly followed:\n\n"
            f"{chr(10).join(company_rules)}\n\n"
            "Rewrite the following commit message to fully comply with these rules. "
            "Stay within the context of the commit message and do not assume any content that is not in the commit message.\n"
            "Respond with only the corrected commit message, nothing else:\n\n"
            "remove the double cotation marks and send the answer"
            f"{commit_message_example}"
        )

        completion = self.client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct",
            messages=[{"role": "user", "content": prompt}]
        )

        final_message = completion.choices[0].message.content.strip()

        # 🔒 In case the LLM returns a JSON-style message
        if final_message.startswith('{') and 'commit_message' in final_message:
            try:
                final_message = json.loads(final_message).get("commit_message", final_message)
            except Exception:
                pass
        
        print("finel commit message:", final_message)
        # 🔁 Replace double quotes with single quotes
        final_message = final_message.replace('"', '').replace("'", '')

        print("Corrected commit message:", final_message)
        return final_message
