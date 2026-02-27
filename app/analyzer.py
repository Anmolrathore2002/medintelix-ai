import re
import json

with open("data/normal_ranges.json") as f:
    normal_ranges = json.load(f)

def extract_values(text):
    extracted = {}
    for test in normal_ranges.keys():
        pattern = rf"{test}\s*[:\-]?\s*([\d\.]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            extracted[test] = float(match.group(1))
    return extracted

def classify_severity(test, value):
    min_val = normal_ranges[test]["min"]
    max_val = normal_ranges[test]["max"]

    if value < min_val:
        diff = min_val - value
        if diff > 3:
            return "Severe Low"
        elif diff > 1:
            return "Moderate Low"
        else:
            return "Mild Low"

    elif value > max_val:
        diff = value - max_val
        if diff > 50:
            return "Severe High"
        elif diff > 20:
            return "Moderate High"
        else:
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