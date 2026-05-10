from fastapi import APIRouter

from geoinsight_api.api.v1.routes import projects, aois

api_router = APIRouter(prefix="/v1")
api_router.include_router(projects.router)
api_router.include_router(aois.router)