# config-service/main.py
from fastapi import FastAPI
import os

app = FastAPI(title="Config Service")

@app.get("/debug/config")
def debug_config():
    return {
        "DB_HOST": os.getenv('DB_HOST'),
        "DB_USER": os.getenv('DB_USER'),
        "DB_NAME": os.getenv('DB_NAME'),
        "DB_PORT": os.getenv('DB_PORT'),
    }
