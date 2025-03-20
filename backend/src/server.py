from fastapi import FastAPI
from backend.src.routes import userRoute

app = FastAPI()

app.include_router(userRoute.router)

@app.get("/")
def home():
    return {"message": "Welcome"}


#Run the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)