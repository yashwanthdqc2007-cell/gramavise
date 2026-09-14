from typing import Generator, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

# Database Engine Configuration
connect_args: Dict[str, Any] = {}
engine_kwargs: Dict[str, Any] = {
    "echo": settings.DEBUG and settings.ENVIRONMENT == "development",
    "future": True,
}

if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
else:
    # Production connection pool hardening for PostgreSQL
    engine_kwargs.update({
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_timeout": settings.DB_POOL_TIMEOUT,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "pool_pre_ping": True,
    })

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **engine_kwargs
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True
)

Base = declarative_base()


def init_db(target_engine=None) -> None:
    """Explicit database schema initialization helper.
    
    Used strictly in test suites and local standalone dev environments.
    In production environments, Alembic migrations ('alembic upgrade head')
    are the exclusive authority for schema provisioning and evolution.
    """
    import app.models  # Ensure all model tables are registered in Base.metadata
    Base.metadata.create_all(bind=target_engine or engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency injection provider yielding a SQLAlchemy database session.
    
    Guarantees session cleanup upon request completion.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_health() -> bool:
    """Perform a lightweight database connectivity check for readiness probes.
    
    Returns True if the database engine can execute a test query, False otherwise.
    Never leaks connection strings or raises unhandled exceptions.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False

