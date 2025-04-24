from commit_message_handler import CommitMessageHandler

handler = CommitMessageHandler()
commit_message = "Fixed a bug in the login flow."
project_name = "sample_project"

corrected_message = handler.generate_commit_message(commit_message, project_name)
print(corrected_message)
