import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError

from app.main import app
from app.db.models import Base
from app.db.session import get_session

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
    """Override the get_session dependency for tests"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test database schema once per test session"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Provide a database session for tests"""
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
    """Provide a test client with overridden database"""
    def override_get_session_with_db():
        """Use the test's db session"""
        yield db
    
    app.dependency_overrides[get_session] = override_get_session_with_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()