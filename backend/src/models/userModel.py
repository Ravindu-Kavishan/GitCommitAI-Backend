from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
import re

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    username: str
    contact: str
    email: EmailStr
    password: str

    # Validator for password format
    # @validator("password")
    # def password_validator(cls, value):
    #     password_regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    #     if not re.match(password_regex, value):
    #         raise ValueError("Password must be at least 8 characters long, contain at least one letter, one number, and one special character.")
    #     return value

    
    @validator("contact")
    def contact_validator(cls, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Contact number must be exactly 10 digits.")
        return value

    class Config:
        # This will allow you to use snake_case in your requests but still keep camelCase in the model
        alias_generator = lambda string: string.lower()

