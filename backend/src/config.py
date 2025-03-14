import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

#load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")



client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]