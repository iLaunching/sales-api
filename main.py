"""
Minimal Sales API - Just FastAPI with health check
No database, no Redis, no nothing - just working API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sales API - Minimal", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": "Sales API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/sales/message")
async def send_message(data: dict):
    """Simple echo endpoint for testing"""
    return {
        "message": f"Hello! You said: {data.get('message', 'nothing')}",
        "session_id": data.get("session_id", "test-123"),
        "status": "ok"
    }


if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
