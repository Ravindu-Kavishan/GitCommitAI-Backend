from fastapi import FastAPI
from backend.src.routes import userRoute
from backend.src.routes import authRoute
from fastapi.middleware.cors import CORSMiddleware  # Make sure this line is included



app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins, change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.include_router(userRoute.router)
app.include_router(authRoute.router)

@app.get("/")
def home():
    return {"message": "Welcome"}


#Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)