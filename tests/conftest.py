import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker

from app.db.models import Base
from app.db.session import get_session
from app.main import app

TEST_DATABASE_URL = "postgresql://admin:password@postgres:5432/test_db"
DEFAULT_DATABASE_URL = "postgresql://admin:password@postgres:5432/postgres"

default_engine = create_engine(DEFAULT_DATABASE_URL, isolation_level="AUTOCOMMIT")
with default_engine.connect() as conn:
    try:
        conn.execute(text("CREATE DATABASE test_db"))
    except ProgrammingError:
        pass
default_engine.dispose()

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()


@pytest.fixture
def client(db):
    def override_get_session_with_db():
        yield db

    app.dependency_overrides[get_session] = override_get_session_with_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

