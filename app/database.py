import sqlite3
from datetime import datetime

DB_NAME = "clinical_data.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            patient_name TEXT,
            age TEXT,
            gender TEXT,
            extracted TEXT,
            analysis TEXT,
            risk_score INTEGER,
            summary TEXT
        )
    """)

    conn.commit()
    conn.close()

def save_report(name, age, gender, values, analysis, risk_score, summary):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reports (timestamp, patient_name, age, gender, extracted, analysis, risk_score, summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        name,
        age,
        gender,
        str(values),
        str(analysis),
        risk_score,
        summary
    ))

    conn.commit()
    conn.close()

def get_all_reports():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, timestamp, patient_name, age, gender, risk_score, summary
    FROM reports ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows