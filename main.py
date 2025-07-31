from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load .env values
load_dotenv()

app = FastAPI()

# 🔐 Middleware to validate API key
@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    expected_key = os.getenv("EXPECTED_API_KEY")
    received_key = request.headers.get("x-api-key")

    if received_key != expected_key:
        raise HTTPException(status_code=403, detail="Forbidden")

    return await call_next(request)

# Optional: CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Backend is up"}

