from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from geoinsight_api.api.v1.schemas.project import (
    ProjectCreate,
    ProjectRead,
    ProjectUpdate,
)
from geoinsight_api.db.session import get_db
from geoinsight_api.services.project_service import ProjectNotFoundError, ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_service(session: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(session=session)


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate, service: ProjectService = Depends(get_project_service)
) -> ProjectRead:
    return service.create_project(name=payload.name, description=payload.description)


@router.get("", response_model=list[ProjectRead])
def list_project(
    service: ProjectService = Depends(get_project_service),
) -> list[ProjectRead]:
    return service.list_project()


@router.get("/{project_id}", response_model=ProjectRead)
def get_project(
    project_id: UUID, service: ProjectService = Depends(get_project_service)
) -> ProjectRead:
    try:
        return service.get_project(project_id=project_id)
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        ) from None


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    service: ProjectService = Depends(get_project_service),
) -> ProjectRead:
    update_data = payload.model_dump(exclude_unset=True)

    try:
        return service.update_project(project_id, update_data)
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        ) from None


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: UUID,
    service: ProjectService = Depends(get_project_service),
) -> None:
    try:
        service.delete_project(project_id)
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        ) from None
