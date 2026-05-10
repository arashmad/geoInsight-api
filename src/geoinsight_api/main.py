from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from geoinsight_api.api.v1.router import api_router
from geoinsight_api.db.session import get_db

app = FastAPI(title="GeoInsight API")

app.include_router(api_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
