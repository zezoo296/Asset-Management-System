import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://postgres:password@127.0.0.1:5432/asset_management",
)

from core.database import SessionLocal, get_db
from core.security import create_access_token, hash_password
from main import app
from models.organization import Organization
from tests.helpers import pause as pause_helper


@pytest.fixture
def db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def clean_db(db: Session) -> Generator[None, None, None]:
    db.execute(
        text("TRUNCATE TABLE relations, assets, organizations RESTART IDENTITY CASCADE")
    )
    db.commit()
    yield


@pytest.fixture
def organization(db: Session) -> Organization:
    org = Organization(
        name="Test Org",
        email="test@example.com",
        password=hash_password("password"),
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return org


@pytest.fixture
def auth_headers(organization: Organization) -> dict[str, str]:
    token = create_access_token(organization.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def pause() -> Generator[None, None, None]:
    yield from pause_helper()
