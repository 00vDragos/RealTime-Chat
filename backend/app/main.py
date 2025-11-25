# app/main.py
from fastapi import FastAPI

app = FastAPI(title="Real-Time Chat API")

@app.get("/healthz")
async def health_check():
    """
    Endpoint de verificare a stării aplicației.
    Îl poți accesa la http://localhost:8000/healthz
    după ce rulezi containerul.
    """
    return {"status": "ok", "message": "Backend is healthy "}
