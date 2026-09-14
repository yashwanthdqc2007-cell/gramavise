import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.router import api_router
from app.api.routes import health
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.request_size import RequestSizeLimitMiddleware
from app.utils.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan event context manager for application startup and shutdown."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.ENVIRONMENT}]")
    logger.info(f"Using AI Provider: {settings.LLM_PROVIDER}")
    logger.info(f"Loaded CORS Origins: {settings.CORS_ORIGINS}")
    logger.info(f"Max Request Body Size: {settings.MAX_REQUEST_SIZE_BYTES} bytes")
    yield
    logger.info(f"Shutting down {settings.APP_NAME}")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Driven Hyper-Local Business Advisory and Financial Structuring Assistant for Rural Micro-Entrepreneurs (SIH26091)",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# 1. Request Size Limit Middleware (Must precede body consumption)
app.add_middleware(RequestSizeLimitMiddleware, max_size_bytes=settings.MAX_REQUEST_SIZE_BYTES)

# 2. CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Request Correlation ID Middleware
app.add_middleware(RequestIDMiddleware)

# Root Health & Readiness aliases for container orchestrator probes
app.include_router(health.router, tags=["Health"])

# Register Main API Router under /api prefix
app.include_router(api_router, prefix="/api")


# --- Global Exception Handlers for Production Hardening ---

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle standard HTTP exceptions with stable request correlation headers."""
    request_id = getattr(request.state, "request_id", "")
    headers = dict(exc.headers) if exc.headers else {}
    if request_id:
        headers["X-Request-ID"] = request_id
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic schema validation failures with clean errors and request correlation."""
    request_id = getattr(request.state, "request_id", "")
    headers = {"X-Request-ID": request_id} if request_id else {}
    errors = jsonable_encoder(exc.errors())
    logger.warning(f"[RequestID: {request_id}] 422 Validation error on {request.method} {request.url.path}: {errors}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors},
        headers=headers,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch unhandled server errors, log full traceback server-side, and return sanitized 500 response."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(f"[RequestID: {request_id}] Unhandled server exception: {exc}\n{traceback.format_exc()}")
    
    headers = {"X-Request-ID": request_id} if request_id else {}
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected server error occurred. Please contact support or try again shortly.",
            "request_id": request_id,
        },
        headers=headers,
    )
