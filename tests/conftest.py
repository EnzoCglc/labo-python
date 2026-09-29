import os

from dotenv import load_dotenv

# SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES come from .env.
# DATABASE_URL is forced to an in-memory database so the real labo.db is never touched
# (set before load_dotenv, which does not override existing variables).
os.environ["DATABASE_URL"] = "sqlite://"
load_dotenv()

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import cli
from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models import Equipement, Role, User


@pytest.fixture
def session_factory(monkeypatch):
    # In-memory database shared across connections, recreated for each test
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    # The CLI opens its own session: point it to the test database
    monkeypatch.setattr(cli, "SessionLocal", TestingSessionLocal)

    yield TestingSessionLocal

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db(session_factory):
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(session_factory):
    def override_get_db():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def users(db):
    accounts = {
        "gestionnaire": User(username="gestionnaire", hashed_password=hash_password("gestion123"), role=Role.gestionnaire),
        "etudiant": User(username="etudiant", hashed_password=hash_password("abc123"), role=Role.etudiant),
        "etudiant2": User(username="etudiant2", hashed_password=hash_password("abc1234"), role=Role.etudiant),
    }
    db.add_all(accounts.values())
    db.commit()
    for user in accounts.values():
        db.refresh(user)
    return accounts


def _auth_headers(client: TestClient, username: str, password: str) -> dict:
    response = client.post("/token", data={"username": username, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def manager_headers(client, users):
    return _auth_headers(client, "gestionnaire", "gestion123")


@pytest.fixture
def student_headers(client, users):
    return _auth_headers(client, "etudiant", "abc123")


@pytest.fixture
def student2_headers(client, users):
    return _auth_headers(client, "etudiant2", "abc1234")


@pytest.fixture
def equipment(db):
    item = Equipement(reference="PC-001", nom="Ordinateur fixe Lenovo", categorie="ordinateur")
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
