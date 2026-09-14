import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import init_db, get_db
from app.repositories import UnitOfWork, get_uow


@pytest.fixture(autouse=True)
def setup_test_database(tmp_path):
    """Automatically configure a fresh isolated SQLite database for all test executions."""
    db_file = tmp_path / "test_session.db"
    test_engine = create_engine(f"sqlite:///{db_file}", connect_args={"check_same_thread": False})
    init_db(target_engine=test_engine)
    test_session_factory = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

    def override_get_uow():
        with UnitOfWork(session_factory=test_session_factory) as uow:
            yield uow

    def override_get_db():
        db = test_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_uow] = override_get_uow
    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()
    test_engine.dispose()


@pytest.fixture
def client():
    """Provides a TestClient for FastAPI endpoints."""
    return TestClient(app)
