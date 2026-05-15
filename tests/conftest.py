from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from geoinsight_api.db.session import SessionLocal, get_db
from geoinsight_api.main import app


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    session = SessionLocal()

    try:
        # Cleanup before each test
        session.execute(text("DELETE FROM vector_analysis_results"))
        session.execute(text("DELETE FROM vector_features"))
        session.execute(text("DELETE FROM vector_layers"))
        session.execute(text("DELETE FROM aois"))
        session.execute(text("DELETE FROM projects"))

        session.commit()

        yield session

    finally:
        # Cleanup after each test
        session.execute(text("DELETE FROM aois"))
        session.execute(text("DELETE FROM projects"))
        session.commit()
        session.close()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
