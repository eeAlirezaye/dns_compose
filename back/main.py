# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import socket
import mysql.connector
from datetime import datetime
import requests
import os
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development (restrict in production)
    allow_methods=["*"],
    allow_headers=["*"],
)
# main.py (updated DB_CONFIG)
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),  # Changed from 'root'
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}
# Models
class DomainLookupRequest(BaseModel):
    domain: str

class LookupResult(BaseModel):
    domain: str
    ip_address: str
    timestamp: datetime
    source: str

# Database setup
def init_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Create table if not exists
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

# DNS resolution functions
def resolve_dns(domain: str) -> Optional[str]:
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return None

def resolve_with_external_api(domain: str) -> Optional[str]:
    try:
        response = requests.get(f"https://dns.google/resolve?name={domain}&type=A")
        data = response.json()
        if 'Answer' in data:
            return data['Answer'][0]['data']
        return None
    except Exception:
        return None

# API Endpoints
@app.post("/lookup", response_model=LookupResult)
async def lookup_domain(request: DomainLookupRequest):
    domain = request.domain.lower().strip()
    
    # Try system DNS first
    ip_address = resolve_dns(domain)
    source = "system_dns"
    
    # Fallback to external API
    if not ip_address:
        ip_address = resolve_with_external_api(domain)
        source = "google_dns"
        if not ip_address:
            raise HTTPException(status_code=404, detail="Domain not found")
    
    # Store in database
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO lookups (domain, ip_address, timestamp, source) VALUES (%s, %s, %s, %s)",
        (domain, ip_address, datetime.now(), source)
    )
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return {
        "domain": domain,
        "ip_address": ip_address,
        "timestamp": datetime.now(),
        "source": source
    }

@app.get("/history")
async def get_history(limit: int = 10):
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

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()