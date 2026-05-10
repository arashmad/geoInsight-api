from uuid import UUID

from sqlalchemy.orm import Session

from geoinsight_api.db.models.project import Project
from geoinsight_api.repositories.project_repository import ProjectRepository


class ProjectNotFoundError(Exception):
    pass


class ProjectService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = ProjectRepository(session=session)

    def create_project(self, *, name: str, description: str | None) -> Project:
        project = self.repository.create(name=name, description=description)
        self.session.commit()
        self.session.refresh(project)
        return project

    def list_project(self) -> list[Project]:
        return self.repository.list()

    def get_project(self, project_id: UUID) -> Project:
        project = self.repository.get_by_id(project_id=project_id)

        if project is None:
            raise ProjectNotFoundError

        return project

    def update_project(self, project_id: UUID, data: dict) -> Project:
        project = self.get_project(project_id=project_id)
        project = self.repository.update(project=project, data=data)

        self.session.commit()
        self.session.refresh(project)

        return project

    def delete_project(self, project_id: UUID) -> None:
        project = self.get_project(project_id=project_id)
        self.repository.delete(project=project)

        self.session.commit()
