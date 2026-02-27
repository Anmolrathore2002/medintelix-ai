from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pdfplumber
from PIL import Image
import shutil
import os

from app.analyzer import extract_values, classify_severity, calculate_risk_score
from app.summarizer import generate_summary
from app.database import init_db, save_report, get_all_reports

app = FastAPI()
templates = Jinja2Templates(directory="templates")

init_db()
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze", response_class=HTMLResponse)
async def analyze(
    request: Request,
    patient_name: str = Form(None),
    age: str = Form(None),
    gender: str = Form(None),
    report_text: str = Form(None),
    file: UploadFile = File(None)
):

    extracted_text = ""

    if report_text and report_text.strip():
        extracted_text = report_text

    elif file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        if file.filename.endswith(".pdf"):
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text

        elif file.filename.endswith((".png", ".jpg", ".jpeg")):
            from pytesseract import image_to_string
            image = Image.open(file_path)
            extracted_text = image_to_string(image)

        elif file.filename.endswith(".txt"):
            with open(file_path, "r") as f:
                extracted_text = f.read()

    extracted = extract_values(extracted_text)
    analysis = {}
    detailed = []

    for test, value in extracted.items():
        status = classify_severity(test, value)
        analysis[test] = status
        detailed.append({"name": test, "value": value, "status": status})

    risk_score = calculate_risk_score(analysis)
    summary = generate_summary(analysis, risk_score)

    save_report(patient_name, age, gender, extracted, analysis, risk_score, summary)

    return templates.TemplateResponse("result.html", {
        "request": request,
        "results": detailed,
        "risk_score": risk_score,
        "summary": summary
    })

@app.get("/history", response_class=HTMLResponse)
def history(request: Request):
    reports = get_all_reports()
    return templates.TemplateResponse("history.html", {
        "request": request,
        "reports": reports
    })