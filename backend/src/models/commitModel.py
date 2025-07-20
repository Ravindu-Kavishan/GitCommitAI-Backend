from pydantic import BaseModel
# Pydantic model to define request structure
class GitDiffRequest(BaseModel):
    diff: str
    message_type: str  # 'singleline' or 'multiline'
    project_name:str

# Pydantic model to define request structure
class CommitMessageRequest(BaseModel):
    commit_message: str
    project_name:str