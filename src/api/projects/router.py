"""
Projects router - CRUD operations for projects.
"""
from datetime import datetime
from typing import List, Optional
import re

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..models.user import User
from ..models.project import Project, ProjectStatus, ProjectType
from ..auth.router import get_current_user


router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    type: ProjectType = ProjectType.WEB


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    custom_domain: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    type: str
    status: str
    preview_url: Optional[str]
    production_url: Optional[str]
    custom_domain: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_deployed_at: Optional[datetime]
    class Config:
        from_attributes = True


def generate_slug(name: str) -> str:
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    return slug.strip('-')


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Project).where(Project.owner_id == current_user.id).order_by(Project.updated_at.desc())
    )
    return [ProjectResponse.model_validate(p) for p in result.scalars().all()]


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Project).where(Project.owner_id == current_user.id))
    project_count = len(result.scalars().all())
    plan_limits = {"free": 1, "pro": 5, "team": 20, "enterprise": 1000}
    limit = plan_limits.get(current_user.plan.value, 1)
    if project_count >= limit:
        raise HTTPException(status_code=403, detail=f"Project limit ({limit}) reached")
    
    base_slug = generate_slug(data.name)
    slug = base_slug
    counter = 1
    while True:
        result = await db.execute(select(Project).where(Project.slug == slug))
        if not result.scalar_one_or_none():
            break
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    project = Project(
        name=data.name, slug=slug, description=data.description,
        type=data.type, owner_id=current_user.id, status=ProjectStatus.DRAFT,
    )
    db.add(project)
    await db.flush()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Project).where(Project.id == project_id).where(Project.owner_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Project).where(Project.id == project_id).where(Project.owner_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description
    if data.custom_domain is not None:
        project.custom_domain = data.custom_domain
    await db.flush()
    await db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Project).where(Project.id == project_id).where(Project.owner_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await db.delete(project)


@router.get("/{project_id}/env")
async def get_env_vars(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Project).where(Project.id == project_id).where(Project.owner_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"env_vars": project.env_vars or {}}


@router.put("/{project_id}/env")
async def update_env_vars(
    project_id: int,
    env_vars: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Project).where(Project.id == project_id).where(Project.owner_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.env_vars = env_vars
    await db.flush()
    return {"message": "Updated"}