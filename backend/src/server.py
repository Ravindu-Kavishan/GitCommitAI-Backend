from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
from src.routes import generateCommitRoute, generateSuggestions, commitExplainRoute
from src.routes import ravi_Login, getProjectAndCommits
from src.routes import getProjectandRules
from src.routes.addminRouters import addProjectAndRules,deleteProject,deleteRule,addRule,getProjectsandUsers,getProjectsAndRules,addUser,deleteUser
from src.interim import generateCommitMessage, generateCommitSugestions

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React frontend URL
    allow_credentials=True,                   # To handle cookies
    allow_methods=["*"],                      # Allow all HTTP methods
    allow_headers=["*"],                      # Allow all headers
)

# Include your routes
# app.include_router(generateCommitRoute.router)
# app.include_router(generateSuggestions.router)
app.include_router(commitExplainRoute.router)

app.include_router(generateCommitMessage.router)
app.include_router(generateCommitSugestions.router)
# app.include_router(addProjectToDB.router)
app.include_router(ravi_Login.router)
app.include_router(getProjectAndCommits.router)
app.include_router(getProjectandRules.router)
app.include_router(addProjectAndRules.router)
app.include_router(deleteProject.router)
app.include_router(deleteRule.router)
app.include_router(addRule.router)
app.include_router(getProjectsandUsers.router)
app.include_router(getProjectsAndRules.router)
app.include_router(addUser.router)
app.include_router(deleteUser.router)
