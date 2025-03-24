from fastapi import FastAPI
from src.routes import generateCommitRoute
from src.routes import generateSuggestions
from src.routes import commitExplainRoute


app = FastAPI()

app.include_router(generateCommitRoute.router)
app.include_router(generateSuggestions.router)
app.include_router(commitExplainRoute.router)







