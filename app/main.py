from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pdfplumber
from PIL import Image
from docx import Document
import shutil
import os

from app.analyzer import (
    extract_values,
    classify_severity,
    calculate_risk_score,
    extract_patient_info
)
from app.database import init_db, save_report, get_all_reports
from app.summarizer import generate_summary

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
                    extracted_text += page.extract_text() or ""

        elif file.filename.endswith((".png", ".jpg", ".jpeg")):
            from pytesseract import image_to_string
            image = Image.open(file_path)
            extracted_text = image_to_string(image)

        elif file.filename.endswith(".txt"):
            with open(file_path, "r") as f:
                extracted_text = f.read()

        elif file.filename.endswith(".docx"):
            doc = Document(file_path)
            for para in doc.paragraphs:
                extracted_text += para.text + "\n"

    # Auto extract patient info
    auto_name, auto_age, auto_gender = extract_patient_info(extracted_text)

    if not patient_name:
        patient_name = auto_name
    if not age:
        age = auto_age
    if not gender:
        gender = auto_gender

    extracted = extract_values(extracted_text)
    analysis = {}

    for test, value in extracted.items():
        analysis[test] = classify_severity(test, value)

    risk_score = calculate_risk_score(analysis)
    summary = generate_summary(analysis, risk_score)

    save_report(patient_name, age, gender, extracted, analysis, risk_score, summary)

    return templates.TemplateResponse("result.html", {
        "request": request,
        "results": extracted,
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
