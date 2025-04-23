from google.oauth2 import service_account
from google.auth.transport.requests import AuthorizedSession
import os


class CommitMessageGenerator:

    def generate_commit_message(self, git_diff, instructions):
        # Load the service account credentials
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv('SERVICE_ACCOUNT_KEY_FILE'),
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
        response = authed_session.post(os.getenv('ENDPOINT_URL'), json=payload)

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
