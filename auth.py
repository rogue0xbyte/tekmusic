from __future__ import print_function
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from config import ADMIN_USERNAME, ADMIN_PASSWORD, RECRUITER_USERNAME, RECRUITER_PASSWORD
import secrets
from googleapiclient.discovery import build 
from google.oauth2 import service_account
import base64, json, os

secret_json = os.getenv('GOOGLE_CREDS')

security = HTTPBasic()


SCOPES = [
'https://www.googleapis.com/auth/spreadsheets',
'https://www.googleapis.com/auth/drive'
]

base64_bytes = secret_json.encode("ascii")

sample_string_bytes = base64.b64decode(base64_bytes)
sample_string = sample_string_bytes.decode("ascii")

creds = json.loads(sample_string)

credentials = service_account.Credentials.from_service_account_info(creds, scopes=SCOPES)
spreadsheet_service = build('sheets', 'v4', credentials=credentials)
drive_service = build('drive', 'v3', credentials=credentials)

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_admin = secrets.compare_digest(credentials.username, ADMIN_USERNAME) and \
                    secrets.compare_digest(credentials.password, ADMIN_PASSWORD)
    correct_recruiter = secrets.compare_digest(credentials.username, RECRUITER_USERNAME) and \
                        secrets.compare_digest(credentials.password, RECRUITER_PASSWORD)
    if correct_admin:
        return {"username": credentials.username, "role": "admin"}
    elif correct_recruiter:
        return {"username": credentials.username, "role": "recruiter"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
