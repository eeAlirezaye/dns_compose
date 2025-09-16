# health-service/main.py
from fastapi import FastAPI
import mysql.connector
import os

app = FastAPI(title="Health Service")

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME'),
    'port': int(os.getenv('DB_PORT', 3306)),
}

@app.get("/health")
def health_check():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchall()
        cursor.close()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except mysql.connector.Error as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
