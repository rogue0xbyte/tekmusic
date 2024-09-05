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
    sheetId = '12N29esBverbJdqUaG6JnebB6JnvzQyIPWBAXkrOr9-M'
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

@app.get("/join_us", response_class=HTMLResponse)
async def join_us(request: Request):
    return templates.TemplateResponse("join_us.html", {"request": request})

@app.post("/join_us_submit")
async def join_us_submit(
    request: Request,
    name: str = Form(...),
    roll_number: str = Form(...),
    email: str = Form(...),
    mobile_number: str = Form(...),
    wing: str = Form(...),
    category: str = Form(...),
    audition_clip: UploadFile = File(None),
    glimpse_of_work: UploadFile = File(None)
):
    # Handle file uploads
    audition_clip_path = None
    glimpse_of_work_path = None
    upload_dir = "static/uploads"

    os.makedirs(upload_dir, exist_ok=True)

    if audition_clip:
        audition_clip_path = os.path.join(upload_dir, audition_clip.filename)
        with open(audition_clip_path, "wb") as buffer:
            shutil.copyfileobj(audition_clip.file, buffer)

    if glimpse_of_work:
        glimpse_of_work_path = os.path.join(upload_dir, glimpse_of_work.filename)
        with open(glimpse_of_work_path, "wb") as buffer:
            shutil.copyfileobj(glimpse_of_work.file, buffer)

    submission = Submission(
        name=name,
        roll_number=roll_number,
        email=email,
        mobile_number=mobile_number,
        wing=wing,
        category=category,
        audition_clip=audition_clip_path,
        glimpse_of_work=glimpse_of_work_path
    )

    await submissions_collection.insert_one(submission.dict())

    return RedirectResponse(url="/thank_you", status_code=303)

@app.get("/thank_you", response_class=HTMLResponse)
async def thank_you(request: Request):
    return templates.TemplateResponse("thank_you.html", {"request": request})

# Admin Routes

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.post("/admin/login")
async def admin_login_post(credentials: HTTPBasicCredentials = Depends(security)):
    user = get_current_user(credentials)
    if user and user['role'] == 'admin':
        # Implement session or token-based authentication
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    raise HTTPException(status_code=400, detail="Invalid credentials")

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, user: dict = Depends(get_current_user)):
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Forbidden")
    submissions = []
    async for submission in submissions_collection.find():
        submissions.append(submission)
    return templates.TemplateResponse("admin_dashboard.html", {"request": request, "submissions": submissions})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)