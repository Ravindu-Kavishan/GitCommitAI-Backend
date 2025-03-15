from pydantic import BaseModel, Field
from typing import Optional

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")  #maps to mogo auto generated id automatically
    username: str
    email: str
    password: str