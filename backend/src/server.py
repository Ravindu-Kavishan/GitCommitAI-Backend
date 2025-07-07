from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
from backend.src.routes import generateCommitRoute, generateSuggestions, commitExplainRoute,getProjectAndCommits,getProjectandRules,forgetPasword,getProjects,nextWord,addProjectandCommits
from backend.src.routes.addminRouters import addProject,deleteProject,deleteRule,addRule,getProjectsandUsers,getProjectsAndRules,addUser,deleteUser
from backend.src.interim import generateCommitMessage, generateCommitSugestions
from backend.src.routes import userRoute
from backend.src.routes import authRoute
from backend.src.routes import getRules
from backend.src.routes import notifyAgent
import asyncio



app = FastAPI()

monitor_task = None

@app.on_event("startup")
async def startup_event():
    """Start all necessary background tasks"""
    global monitor_task
    monitor_task = await notifyAgent.start_monitor()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup when the application shuts down"""
    global monitor_task
    if monitor_task:
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include your routes
# app.include_router(generateCommitRoute.router)
# app.include_router(generateSuggestions.router)
app.include_router(commitExplainRoute.router)

app.include_router(generateCommitMessage.router)
app.include_router(generateCommitSugestions.router)

# app.include_router(addProjectToDB.router)
app.include_router(getProjectAndCommits.router)
app.include_router(getProjectandRules.router)
app.include_router(addProject.router)
app.include_router(deleteProject.router)
app.include_router(deleteRule.router)
app.include_router(addRule.router)
app.include_router(getProjectsandUsers.router)
app.include_router(getProjectsAndRules.router)
app.include_router(addProjectandCommits.router)
app.include_router(addUser.router)
app.include_router(deleteUser.router)
app.include_router(getProjects.router)
app.include_router(getRules.router)
app.include_router(userRoute.router)
app.include_router(authRoute.router)

app.include_router(forgetPasword.router)

app.include_router(nextWord.router)


@app.get("/")
async def hello_world():
    return {"message": "Hello, World!"}

