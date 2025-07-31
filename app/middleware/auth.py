from fastapi import Request, HTTPException
from app.core.config import settings

async def verify_api_key(request: Request, call_next):
    key = request.headers.get("x-api-key")
    if key != settings.EXPECTED_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await call_next(request)

