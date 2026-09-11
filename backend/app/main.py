from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.router import api_router
from app.database import Base, engine
from app.utils.logging import logger

# Initialize database schema tables (in development mode)
# In production, tables will be provisioned via Alembic migrations
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Driven Hyper-Local Business Advisory and Financial Structuring Assistant for Rural Micro-Entrepreneurs (SIH26091)",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router under /api prefix
app.include_router(api_router, prefix="/api")


@app.on_event("startup")
async def on_startup():
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.ENVIRONMENT}]")
    logger.info(f"Using AI Provider: {settings.LLM_PROVIDER}")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info(f"Shutting down {settings.APP_NAME}")
