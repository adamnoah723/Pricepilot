#!/usr/bin/env python3
"""
Direct server startup script with bounded DB wait/retry logic.

This script attempts to connect to the database host/port parsed from
`DATABASE_URL` before importing the FastAPI app. That prevents import-time
database operations (like `Base.metadata.create_all`) from failing due to a
brief Postgres startup delay. The wait is bounded by environment-configurable
values to avoid infinite loops in faulty environments.
"""
import os
import sys
import time
import socket
from urllib.parse import urlparse

import uvicorn


def parse_db_host_port(database_url: str):
    if not database_url:
        return None, None
    parsed = urlparse(database_url)
    # Only attempt for TCP-based DBs (postgres, postgresql)
    if parsed.scheme and parsed.scheme.startswith("postgres"):
        host = parsed.hostname or "db"
        port = parsed.port or 5432
        return host, port
    return None, None


def wait_for_db(database_url: str, max_retries: int = 30, delay: float = 2.0):
    host, port = parse_db_host_port(database_url)
    if not host or not port:
        # Nothing to wait for (sqlite or other file-based DB)
        return True

    attempt = 0
    last_err = None
    while attempt < max_retries:
        attempt += 1
        try:
            with socket.create_connection((host, port), timeout=5):
                print(f"DB reachable at {host}:{port} (after {attempt} attempt(s))")
                return True
        except Exception as exc:
            last_err = exc
            print(f"DB not ready at {host}:{port} (attempt {attempt}/{max_retries}), retrying in {delay}s...")
            time.sleep(delay)

    print(f"Timed out waiting for DB at {host}:{port} after {max_retries} attempts: {last_err}")
    return False


if __name__ == "__main__":
    # Configuration via env vars
    database_url = os.getenv("DATABASE_URL", "")
    max_retries = int(os.getenv("DB_MAX_RETRIES", "30"))
    retry_delay = float(os.getenv("DB_RETRY_DELAY", "2"))

    print("Starting PricePilot backend server: waiting for DB if necessary...")
    ok = wait_for_db(database_url, max_retries=max_retries, delay=retry_delay)
    if not ok:
        print("Error: database unavailable after retries, aborting startup.")
        sys.exit(1)

    # Import the app only after the DB is reachable to avoid import-time errors
    from app.main import app

    uvicorn.run(
        "app.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", os.getenv("PORT", "8000"))),
        reload=True,
        log_level="info",
    )