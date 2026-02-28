import re
import json

with open("data/normal_ranges.json") as f:
    normal_ranges = json.load(f)

def extract_patient_info(text):
    name = age = gender = None

    name_match = re.search(r"(Name|Patient Name)\s*[:\-]?\s*([A-Za-z ]+)", text, re.I)
    age_match = re.search(r"(Age)\s*[:\-]?\s*(\d+)", text, re.I)
    gender_match = re.search(r"(Gender|Sex)\s*[:\-]?\s*(Male|Female)", text, re.I)

    if name_match:
        name = name_match.group(2).strip()
    if age_match:
        age = age_match.group(2).strip()
    if gender_match:
        gender = gender_match.group(2).strip()

    return name, age, gender

def extract_values(text):
    extracted = {}
    for test in normal_ranges.keys():
        pattern = rf"{test}\s*[:\-]?\s*([\d\.]+)"
        match = re.search(pattern, text, re.I)
        if match:
            extracted[test] = float(match.group(1))
    return extracted

def classify_severity(test, value):
    min_val = normal_ranges[test]["min"]
    max_val = normal_ranges[test]["max"]

    if value < min_val:
        return "Mild Low"
    elif value > max_val:
        return "Mild High"
    return "Normal"

def calculate_risk_score(analysis):
    risk = 0
    for status in analysis.values():
        if "Severe" in status:
            risk += 30
        elif "Moderate" in status:
            risk += 15
        elif "Mild" in status:
            risk += 5
    return min(risk, 100)
