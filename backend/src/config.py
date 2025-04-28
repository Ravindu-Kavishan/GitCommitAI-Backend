
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
# MONGO_URI="mongodb://localhost:27017"
#DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_NAME = "commit_DB"
# DATABASE_NAME = os.getenv("DATABASE_NAME", "commit_DB")


# Debugging
print(f"DATABASE_NAME: {MONGO_URI} (Type: {type(DATABASE_NAME)})")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]  # Failing line

