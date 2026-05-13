from fastapi import APIRouter

from geoinsight_api.api.v1.routes import aois, projects, vector_layers

api_router = APIRouter(prefix="/v1")
api_router.include_router(projects.router)
api_router.include_router(aois.router)
api_router.include_router(vector_layers.router)
