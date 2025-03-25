from fastapi import FastAPI
from src.routes import generateCommitRoute
from src.routes import generateSuggestions
from src.routes import commitExplainRoute
from src.interim import generateCommitMessage
from src.interim import generateCommitSugestions
from src.routes import addProjectToDB
from src.routes import ravi_Login


app = FastAPI()

# app.include_router(generateCommitRoute.router)
# app.include_router(generateSuggestions.router)
app.include_router(commitExplainRoute.router)


app.include_router(generateCommitMessage.router)
app.include_router(generateCommitSugestions.router)
app.include_router(addProjectToDB.router)
app.include_router(ravi_Login.router)







