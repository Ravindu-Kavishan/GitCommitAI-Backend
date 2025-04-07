from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
from src.routes import generateCommitRoute, generateSuggestions, commitExplainRoute
from src.routes import ravi_Login, getProjectAndCommits
from src.routes import getProjectandRules
from src.routes.addminRouters import addProjectAndRules,deleteProject,deleteRule,addRule,getProjectsandUsers,getProjectsAndRules,addUser,deleteUser
from src.interim import generateCommitMessage, generateCommitSugestions

from backend.src.routes import userRoute
from backend.src.routes import authRoute

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  
        "vscode-webview://1dj8rm3ciunnkl89kon2pclrqtfm8h2qsreshgji2hk5qacf87ie",
        "vscode-webview://058nbu3v76j2nef8hhk9og6p4rjit5891q9ni88uh0hv6n14akts"
    ],
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

app.include_router(userRoute.router)
app.include_router(authRoute.router)
