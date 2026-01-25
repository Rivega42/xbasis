"""
Sandbox API endpoints for Live Preview.
"""
from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..models.user import User
from ..models.project import Project
from ..auth.router import get_current_user
from .manager import sandbox_manager

router = APIRouter()


class CreateSandboxRequest(BaseModel):
    files: Dict[str, str] = {}


class SandboxResponse(BaseModel):
    id: str
    project_id: int
    preview_url: str
    status: str
    port: int


class UpdateFilesRequest(BaseModel):
    files: Dict[str, str]


@router.post("/{project_id}/sandbox", response_model=SandboxResponse)
async def create_sandbox(
    project_id: int,
    data: CreateSandboxRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id).where(Project.owner_id == current_user.id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    sandbox = await sandbox_manager.create_sandbox(
        project_id=project_id,
        project_type=project.type.value,
        files=data.files,
        db_url=f"postgresql://project_{project_id}@localhost/xbasis",
    )
    return SandboxResponse(id=sandbox.id, project_id=sandbox.project_id, preview_url=sandbox.preview_url, status=sandbox.status, port=sandbox.port)


@router.get("/{project_id}/sandbox", response_model=SandboxResponse)
async def get_sandbox(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id).where(Project.owner_id == current_user.id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")
    sandbox = await sandbox_manager.get_sandbox(project_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="Sandbox not found")
    return SandboxResponse(id=sandbox.id, project_id=sandbox.project_id, preview_url=sandbox.preview_url, status=sandbox.status, port=sandbox.port)


@router.put("/{project_id}/sandbox/files")
async def update_sandbox_files(
    project_id: int,
    data: UpdateFilesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id).where(Project.owner_id == current_user.id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")
    try:
        await sandbox_manager.update_files(project_id, data.files)
        return {"status": "updated", "files_count": len(data.files)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{project_id}/sandbox")
async def stop_sandbox(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Project).where(Project.id == project_id).where(Project.owner_id == current_user.id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Project not found")
    await sandbox_manager.destroy_sandbox(project_id)
    return {"status": "stopped"}