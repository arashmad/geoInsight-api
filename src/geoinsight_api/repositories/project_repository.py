from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from geoinsight_api.db.models.project import Project

class ProjectRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, *, name: str, description: str|None) -> Project:
        project = Project(name=name, description=description)
        self.session.add(project)
        self.session.flush()
        return project
    
    def list(self)-> list[Project]:
        stmt = select(Project).order_by(Project.created_at.desc())
        return list(self.session.scalars(stmt).all())
    
    def get_by_id(self, project_id: UUID) -> Project | None:
        return self.session.get(Project, project_id)
    
    def update(self, project: Project, data: dict[str, Any]) -> Project:
        for field, value in data.items():
            setattr(project, field, value)
        
        self.session.flush()
        return project
    
    def delete(self, project: Project) -> None:
        self.session.delete(project)
        self.session.flush()