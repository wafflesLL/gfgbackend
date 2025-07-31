from fastapi import FastAPI
from app.api import routes_test
from app.middleware.auth import verify_api_key
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# Add middleware
app.middleware("http")(verify_api_key)

# Include routers
app.include_router(routes_test.router)

