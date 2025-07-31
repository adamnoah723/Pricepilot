#!/usr/bin/env python3
"""
Direct server startup script
"""
import uvicorn
from app.main import app

if __name__ == "__main__":
    print("Starting PricePilot backend server...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )