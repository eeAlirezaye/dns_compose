# dns-resolver-service/main.py
from fastapi import FastAPI, HTTPException
import socket
import requests
from typing import Optional

app = FastAPI(title="DNS Resolver Service")

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

@app.get("/resolve")
def resolve(domain: str):
    domain = domain.lower().strip()
    ip_address = resolve_dns(domain)
    source = "system_dns"

    if not ip_address:
        ip_address = resolve_with_external_api(domain)
        source = "google_dns"

    if not ip_address:
        raise HTTPException(status_code=404, detail="Domain not found")

    return {"domain": domain, "ip_address": ip_address, "source": source}
