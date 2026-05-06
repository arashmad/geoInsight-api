from sqlalchemy import text

from geoinsight_api.db.session import SessionLocal


def test_db_session_opens() -> None:
    with SessionLocal() as session:
        result = session.execute(text("SELECT 1")).scalar_one()
    assert result == 1


def test_postgis_existence() -> None:
    with SessionLocal() as session:
        result = session.execute(text("SELECT PostGIS_Version()")).scalar_one_or_none()
    assert result == "3.7 USE_GEOS=1 USE_PROJ=1 USE_STATS=1"