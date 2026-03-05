"""FastAPI application with intentional security vulnerabilities for DevSecOps training."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.models import HealthResponse
from app.routes import lab, notes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    settings = get_settings()
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Lab mode: {'ENABLED' if settings.lab_mode else 'DISABLED'}")

    # WARNING: Do not log secrets in production!
    # This is here to demonstrate the hardcoded secret vulnerability
    logger.info(f"Using secret key: {settings.secret_key[:10]}...")

    yield

    logger.info("Shutting down application")


app = FastAPI(
    title="Notes API",
    description="FastAPI Notes API with intentional security vulnerabilities for DevSecOps training",
    version="0.1.0",
    lifespan=lifespan
)


# VULNERABILITY 2: Overly permissive CORS configuration
# This allows any origin to access the API with credentials
# SAST tools and security scanners will flag this as a security risk
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # VULNERABLE: Allows all origins
    allow_credentials=True,  # DANGEROUS when combined with allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# FIX: Secure CORS configuration
# Comment out the middleware above and uncomment below:
#
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://localhost:3000",
#         "http://localhost:8000",
#         "https://yourdomain.com",
#     ],  # Specific allowed origins
#     allow_credentials=True,  # Safe when origins are restricted
#     allow_methods=["GET", "POST", "DELETE"],  # Specific methods
#     allow_headers=["Content-Type", "Authorization"],  # Specific headers
# )


@app.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok")


# Include routers
app.include_router(notes.router)
app.include_router(lab.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
