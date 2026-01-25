"""
Billing router - subscription management with Paddle.
"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.database import get_db
from ..models.user import User, PlanType
from ..auth.router import get_current_user

router = APIRouter()


class PlanInfo(BaseModel):
    id: str
    name: str
    price: int
    interval: str
    tokens: int
    projects: int
    features: List[str]


PLANS = [
    PlanInfo(id="free", name="Free", price=0, interval="monthly", tokens=10000, projects=1, features=["1 project", "10K tokens"]),
    PlanInfo(id="pro", name="Pro", price=2900, interval="monthly", tokens=100000, projects=5, features=["5 projects", "100K tokens", "Custom domains"]),
    PlanInfo(id="team", name="Team", price=9900, interval="monthly", tokens=500000, projects=20, features=["20 projects", "500K tokens", "Team collaboration"]),
]


@router.get("/plans", response_model=List[PlanInfo])
async def list_plans():
    return PLANS


@router.post("/checkout")
async def create_checkout(plan_id: str, current_user: User = Depends(get_current_user)):
    if plan_id not in ["pro", "team"]:
        raise HTTPException(status_code=400, detail="Invalid plan")
    return {"checkout_url": f"https://checkout.paddle.com/{plan_id}?email={current_user.email}"}


@router.get("/usage")
async def get_usage(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from ..models.project import Project, AISession
    result = await db.execute(select(Project).where(Project.owner_id == current_user.id))
    projects = result.scalars().all()
    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    result = await db.execute(select(AISession).where(AISession.user_id == current_user.id).where(AISession.created_at >= month_start))
    tokens_used = sum(s.total_tokens for s in result.scalars().all())
    plan_limits = {"free": 1, "pro": 5, "team": 20, "enterprise": 1000}
    return {
        "plan": current_user.plan.value,
        "tokens_balance": current_user.tokens_balance,
        "tokens_used_this_month": tokens_used,
        "projects_count": len(projects),
        "projects_limit": plan_limits.get(current_user.plan.value, 1),
    }


@router.post("/webhook")
async def paddle_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    data = await request.json()
    event_type = data.get("event_type")
    user_id = data.get("data", {}).get("custom_data", {}).get("user_id")
    if not user_id:
        return {"status": "ignored"}
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    if not user:
        return {"status": "user_not_found"}
    if event_type == "subscription.created":
        user.plan = PlanType.PRO
        user.tokens_balance = settings.PLAN_PRO_TOKENS
    elif event_type == "subscription.cancelled":
        user.plan = PlanType.FREE
    await db.flush()
    return {"status": "ok"}