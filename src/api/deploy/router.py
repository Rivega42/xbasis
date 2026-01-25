"""
Deploy router - trigger deployments via Railway.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from ..core.config import settings
from ..core.database import get_db
from ..models.user import User
from ..models.project import Project, ProjectStatus, Deployment
from ..auth.router import get_current_user


router = APIRouter()


# ════════════════════════════════════════════
# Schemas
# ════════════════════════════════════════════

class DeployRequest(BaseModel):
    environment: str = "preview"  # preview, production


class DeploymentResponse(BaseModel):
    id: int
    environment: str
    status: str
    url: Optional[str]
    created_at: datetime
    finished_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ════════════════════════════════════════════
# Railway Integration
# ════════════════════════════════════════════

async def trigger_railway_deploy(project: Project, environment: str) -> dict:
    """
    Trigger deployment on Railway.
    
    This is a simplified version. Real implementation would:
    1. Create/update Railway service
    2. Set environment variables
    3. Trigger build
    4. Return deployment info
    """
    if not settings.RAILWAY_API_KEY:
        # Mock response for development
        return {
            "id": f"deploy-{project.id}-{environment}",
            "url": f"https://{project.slug}-{environment}.up.railway.app",
            "status": "building",
        }
    
    async with httpx.AsyncClient() as client:
        headers = {
            "Authorization": f"Bearer {settings.RAILWAY_API_KEY}",
            "Content-Type": "application/json",
        }
        
        # Railway GraphQL API
        query = """
        mutation deploymentCreate($input: DeploymentCreateInput!) {
            deploymentCreate(input: $input) {
                id
                status
            }
        }
        """
        
        payload = {
            "query": query,
            "variables": {
                "input": {
                    "projectId": project.railway_project_id,
                    "serviceId": project.railway_service_id,
                    "environmentId": environment,
                }
            }
        }
        
        response = await client.post(
            "https://backboard.railway.app/graphql/v2",
            json=payload,
            headers=headers,
            timeout=30.0,
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Railway API error: {response.text}"
            )
        
        data = response.json()
        return data.get("data", {}).get("deploymentCreate", {})


async def check_deployment_status(deployment_id: str) -> str:
    """Check deployment status from Railway."""
    # Mock for development
    return "live"


# ════════════════════════════════════════════
# Background Tasks
# ════════════════════════════════════════════

async def monitor_deployment(deployment_id: int, db_url: str):
    """
    Background task to monitor deployment status.
    
    In production, this would poll Railway API and update status.
    """
    pass


# ════════════════════════════════════════════
# Endpoints
# ════════════════════════════════════════════

@router.post("/{project_id}/deploy", response_model=DeploymentResponse)
async def deploy_project(
    project_id: int,
    data: DeployRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Deploy project to specified environment.
    
    FUNC-DEP-001, FUNC-DEP-002
    """
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.owner_id == current_user.id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    result = await db.execute(
        select(Deployment)
        .where(Deployment.project_id == project_id)
        .where(Deployment.environment == data.environment)
        .where(Deployment.status.in_(["pending", "building", "deploying"]))
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Deployment already in progress"
        )
    
    railway_result = await trigger_railway_deploy(project, data.environment)
    
    deployment = Deployment(
        project_id=project.id,
        environment=data.environment,
        status="building",
        url=railway_result.get("url"),
    )
    
    db.add(deployment)
    
    project.status = ProjectStatus.BUILDING
    if data.environment == "preview":
        project.preview_url = railway_result.get("url")
    else:
        project.production_url = railway_result.get("url")
    
    await db.flush()
    await db.refresh(deployment)
    
    background_tasks.add_task(
        monitor_deployment,
        deployment.id,
        str(settings.DATABASE_URL)
    )
    
    return DeploymentResponse.model_validate(deployment)


@router.get("/{project_id}/deployments", response_model=List[DeploymentResponse])
async def list_deployments(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all deployments for a project."""
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.owner_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    result = await db.execute(
        select(Deployment)
        .where(Deployment.project_id == project_id)
        .order_by(Deployment.created_at.desc())
        .limit(20)
    )
    deployments = result.scalars().all()
    
    return [DeploymentResponse.model_validate(d) for d in deployments]


@router.get("/{project_id}/deployments/{deployment_id}", response_model=DeploymentResponse)
async def get_deployment(
    project_id: int,
    deployment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific deployment."""
    result = await db.execute(
        select(Project)
        .where(Project.id == project_id)
        .where(Project.owner_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    result = await db.execute(
        select(Deployment)
        .where(Deployment.id == deployment_id)
        .where(Deployment.project_id == project_id)
    )
    deployment = result.scalar_one_or_none()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found"
        )
    
    return DeploymentResponse.model_validate(deployment)


@router.delete("/{project_id}/deployments/{deployment_id}")
async def cancel_deployment(
    project_id: int,
    deployment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a pending deployment."""
    result = await db.execute(
        select(Deployment)
        .where(Deployment.id == deployment_id)
        .where(Deployment.project_id == project_id)
    )
    deployment = result.scalar_one_or_none()
    
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deployment not found"
        )
    
    if deployment.status not in ["pending", "building"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only cancel pending or building deployments"
        )
    
    deployment.status = "cancelled"
    deployment.finished_at = datetime.utcnow()
    
    await db.flush()
    
    return {"message": "Deployment cancelled"}


# ════════════════════════════════════════════
# Webhook Schemas
# ════════════════════════════════════════════

class GitHubPushEvent(BaseModel):
    """GitHub push event payload (simplified)."""
    ref: str
    after: str
    repository: dict
    pusher: dict


class WebhookResponse(BaseModel):
    status: str
    message: str
    deployment_id: Optional[int] = None


# ════════════════════════════════════════════
# Webhook Endpoints
# ════════════════════════════════════════════

import hmac
import hashlib
from fastapi import Request, Header


def verify_github_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature."""
    if not signature or not secret:
        return False
    
    expected = "sha256=" + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)


@router.post("/webhook/github", response_model=WebhookResponse)
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hub_signature_256: Optional[str] = Header(None),
    x_github_event: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    GitHub webhook handler for auto-deploy.
    
    FUNC-DEP-005: Auto-deploy on push to main/master
    """
    body = await request.body()
    
    webhook_secret = getattr(settings, 'GITHUB_WEBHOOK_SECRET', None)
    if webhook_secret:
        if not verify_github_signature(body, x_hub_signature_256 or "", webhook_secret):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )
    
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    
    if x_github_event != "push":
        return WebhookResponse(
            status="ignored",
            message=f"Event type '{x_github_event}' not handled"
        )
    
    ref = payload.get("ref", "")
    if ref not in ["refs/heads/main", "refs/heads/master"]:
        return WebhookResponse(
            status="ignored",
            message=f"Branch '{ref}' not configured for auto-deploy"
        )
    
    repo_url = payload.get("repository", {}).get("html_url", "")
    repo_full_name = payload.get("repository", {}).get("full_name", "")
    
    result = await db.execute(
        select(Project)
        .where(Project.repo_url == repo_url)
        .where(Project.auto_deploy == True)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        return WebhookResponse(
            status="skipped",
            message=f"No project found for repository '{repo_full_name}' or auto-deploy disabled"
        )
    
    result = await db.execute(
        select(Deployment)
        .where(Deployment.project_id == project.id)
        .where(Deployment.status.in_(["pending", "building", "deploying"]))
    )
    if result.scalar_one_or_none():
        return WebhookResponse(
            status="skipped",
            message="Deployment already in progress"
        )
    
    commit_sha = payload.get("after", "")[:7]
    commit_message = payload.get("head_commit", {}).get("message", "")[:100]
    
    railway_result = await trigger_railway_deploy(project, "production")
    
    deployment = Deployment(
        project_id=project.id,
        environment="production",
        status="building",
        url=railway_result.get("url"),
        commit_sha=commit_sha,
        commit_message=commit_message,
    )
    
    db.add(deployment)
    
    project.status = ProjectStatus.BUILDING
    project.production_url = railway_result.get("url")
    
    await db.flush()
    await db.refresh(deployment)
    
    background_tasks.add_task(
        monitor_deployment,
        deployment.id,
        str(settings.DATABASE_URL)
    )
    
    return WebhookResponse(
        status="triggered",
        message=f"Deployment triggered for commit {commit_sha}",
        deployment_id=deployment.id
    )
