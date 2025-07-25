"""
FastAPI Main Application Module

This module initializes and configures the FastAPI application with:
- Google Cloud Logging setup
- Router registration for business logic endpoints
- Exception handlers for error management
- CORS and Trusted Host middleware configuration
- API versioning support

The application exposes a REST API for SAP OData operations.
"""

import logging as log
from typing import Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import logging as gcp_logging
from sqlalchemy.exc import OperationalError
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.bussiness_logic.endpoints import business_logic_router
from app.exception import exception_handler, DoesNotExist, does_not_exist_handler
from app.env_variables import LOGGING_NAME

# API Version configuration
API_VERSION = "1.0.0"
API_PREFIX = "/api/v1"

# Initialize Google Cloud Logging
try:
    logging_client = gcp_logging.Client()
    logging_client.setup_logging(name=LOGGING_NAME)
except Exception as e:
    log.warning(f"Failed to initialize Google Cloud Logging: {e}")

# Create FastAPI application instance
app = FastAPI(
    title="OData Middleware",
    description="REST API for executing SAP OData operations",
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)
app.root_path = "/"

# Version info endpoint
@app.get("/version", tags=["System"])
def get_version() -> Dict[str, str]:
    """Returns the current API version information"""
    return {
        "version": API_VERSION,
        "status": "active"
    }

# Register routers with versioned prefix
app.include_router(
    business_logic_router,
    prefix=API_PREFIX,
    tags=["Business Logic"]
)

# Configure exception handlers
app.add_exception_handler(Exception, exception_handler)
app.add_exception_handler(OperationalError, exception_handler)
app.add_exception_handler(DoesNotExist, does_not_exist_handler)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
