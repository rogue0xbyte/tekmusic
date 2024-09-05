import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017")
DATABASE_NAME = "music_club"
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "adminpassword")
RECRUITER_USERNAME = os.getenv("RECRUITER_USERNAME", "recruiter")
RECRUITER_PASSWORD = os.getenv("RECRUITER_PASSWORD", "recruiterpassword")
