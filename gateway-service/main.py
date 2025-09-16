# gateway-service/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import requests

app = FastAPI(title="Gateway Service")

DNS_RESOLVER_URL = "http://dns-resolver-service:8000/resolve"
DB_SERVICE_URL = "http://db-service:8000/lookups"

class DomainLookupRequest(BaseModel):
    domain: str

@app.get("/")
def root():
    """Root endpoint to avoid 404 errors"""
    return {"service": "DNS Gateway Service", "status": "running", "version": "1.0.0"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Test connectivity to downstream services
        dns_health = requests.get("http://dns-resolver-service:8000/health", timeout=5)
        db_health = requests.get("http://db-service:8000/health", timeout=5)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "dns_resolver": "healthy" if dns_health.status_code == 200 else "unhealthy",
                "db_service": "healthy" if db_health.status_code == 200 else "unhealthy"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

@app.post("/lookup")
def lookup_domain(request: DomainLookupRequest):
    # Step 1: Resolve domain via DNS service
    dns_response = requests.get(DNS_RESOLVER_URL, params={"domain": request.domain})
    if dns_response.status_code != 200:
        raise HTTPException(status_code=404, detail="Domain not found")
    dns_data = dns_response.json()

    # Step 2: Store result via DB service
    record = {
        "domain": dns_data["domain"],
        "ip_address": dns_data["ip_address"],
        "timestamp": datetime.now().isoformat(),
        "source": dns_data["source"]
    }
    save_response = requests.post(DB_SERVICE_URL, json=record)
    if save_response.status_code != 200:
        raise HTTPException(status_code=500, detail="Database save failed")

    return record

@app.get("/history")
def get_history(limit: int = 10):
    response = requests.get(f"{DB_SERVICE_URL}?limit={limit}")
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Database query failed")
    return response.json()