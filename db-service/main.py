# db-service/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import mysql.connector
import os
from typing import List

app = FastAPI(title="Database Service")

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'consume_results': True
}

class LookupRecord(BaseModel):
    domain: str
    ip_address: str
    timestamp: datetime
    source: str

def init_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lookups (
        id INT AUTO_INCREMENT PRIMARY KEY,
        domain VARCHAR(255) NOT NULL,
        ip_address VARCHAR(45) NOT NULL,
        timestamp DATETIME NOT NULL,
        source VARCHAR(50) NOT NULL
    )
    """)
    conn.commit()
    cursor.close()
    conn.close()

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/lookups")
def save_lookup(record: LookupRecord):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO lookups (domain, ip_address, timestamp, source) VALUES (%s, %s, %s, %s)",
        (record.domain, record.ip_address, record.timestamp, record.source)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "saved"}

@app.get("/lookups")
def get_history(limit: int = 10):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT domain, ip_address, timestamp, source FROM lookups ORDER BY timestamp DESC LIMIT %s",
        (limit,)
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results
