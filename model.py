from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Submission(BaseModel):
    name: str
    roll_number: str
    email: EmailStr
    mobile_number: str
    wing: str
    category: str
    audition_clip: Optional[str] = None  # File path
    glimpse_of_work: Optional[str] = None  # File path

class User(BaseModel):
    username: str
    password: str
    role: str  # 'admin' or 'recruiter'
