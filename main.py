from __future__ import print_function

from fastapi import FastAPI, Request, Form, UploadFile, File, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URI, DATABASE_NAME
from models import Submission
from auth import get_current_user
import os
import shutil
from typing import List
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from auth import spreadsheet_service
from auth import drive_service

def read_gsheet():
    range_name = 'Form Responses 1'
    sheetId = '18UmAT1rte4aIDVuei7G5EVkjcVWVVGTO2Faq6iJUygU'
    result = spreadsheet_service.spreadsheets().values().get(
    spreadsheetId=sheetId, range=range_name).execute()
    rows = result.get('values', [])
    print('{0} rows retrieved.'.format(len(rows)))
    jsonData = [dict(zip(rows[0], row)) for row in rows[1:]]
    print('{0} rows retrieved.'.format(jsonData))
    return jsonData

app = FastAPI()

security = HTTPBasic()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# # # Setup MongoDB
# # client = AsyncIOMotorClient(MONGODB_URI)
# # db = client[DATABASE_NAME]
# submissions_collection = db["submissions"]

# Routes

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # Fetch carousel images or data as needed
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/events", response_class=HTMLResponse)
async def events(request: Request):
    # Fetch events data from DB or define statically
    return templates.TemplateResponse("events.html", {"request": request})

@app.get("/shows", response_class=HTMLResponse)
async def shows(request: Request):
    # Fetch shows data from DB or define statically
    return templates.TemplateResponse("shows.html", {"request": request})

@app.get("/the_band", response_class=HTMLResponse)
async def the_band(request: Request):
    # Fetch band member data
    return templates.TemplateResponse("the_band.html", {"request": request, "band":read_gsheet()})

@app.get("/recruitment", response_class=HTMLResponse)
async def join_us(request: Request):
    return templates.TemplateResponse("join_us.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)