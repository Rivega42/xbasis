"""
Billing router - subscription management with Paddle.
"""
import hashlib
import hmac
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import httpx

from ..core.config import settings
from ..core.database import get_db
from ..models.user import User, PlanType
from ..auth.router import get_current_user

router = APIRouter()


class PlanInfo(BaseModel):
    id: str
    name: str
    price: int  # in cents
    interval: str
    tokens: int
    projects: int
    features: List[str]


PLANS = [
    PlanInfo(
        id="free",
        name="Free",
        price=0,
        interval="monthly",
        tokens=10000,
        projects=1,
        features=["1 project", "10K tokens/month", "Community support"]
    ),
    PlanInfo(
        id="pro",
        name="Pro",
        price=2900,  # $29/month
        interval="monthly",
        tokens=100000,
        projects=5,
        features=["5 projects", "100K tokens/month", "Custom domains", "Priority support"]
    ),
    PlanInfo(
        id="team",
        name="Team",
        price=9900,  # $99/month
        interval="monthly",
        tokens=500000,
        projects=20,
        features=["20 projects", "500K tokens/month", "Team collaboration", "Dedicated support"]
    ),
]

# Plan mapping from Paddle price IDs
PADDLE_PLAN_MAP = {
    # Configure these in .env
    # PADDLE_PRO_PRICE_ID: PlanType.PRO
    # PADDLE_TEAM_PRICE_ID: PlanType.TEAM
}


def verify_paddle_signature(payload: bytes, signature: str) -> bool:
    """Verify Paddle webhook signature."""
    if not settings.PADDLE_WEBHOOK_SECRET:
        # Development mode - skip verification
        return True

    expected = hmac.new(
        settings.PADDLE_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected, signature)


@router.get("/plans", response_model=List[PlanInfo])
async def list_plans():
    """Get available subscription plans."""
    return PLANS


class CheckoutRequest(BaseModel):
    plan_id: str
    return_url: Optional[str] = None


class CheckoutResponse(BaseModel):
    checkout_url: str


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    data: CheckoutRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a Paddle checkout session."""
    if data.plan_id not in ["pro", "team"]:
        raise HTTPException(status_code=400, detail="Invalid plan")

    # In production, use Paddle API to create checkout
    if settings.PADDLE_API_KEY:
        try:
            async with httpx.AsyncClient() as client:
                # Paddle API endpoint
                paddle_url = "https://api.paddle.com/transactions"

                # Get price ID based on plan
                price_id_map = {
                    "pro": getattr(settings, "PADDLE_PRO_PRICE_ID", ""),
                    "team": getattr(settings, "PADDLE_TEAM_PRICE_ID", ""),
                }
                price_id = price_id_map.get(data.plan_id)

                if not price_id:
                    raise HTTPException(
                        status_code=500,
                        detail="Plan not configured"
                    )

                response = await client.post(
                    paddle_url,
                    headers={
                        "Authorization": f"Bearer {settings.PADDLE_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "items": [{"price_id": price_id, "quantity": 1}],
                        "customer": {
                            "email": current_user.email,
                        },
                        "custom_data": {
                            "user_id": str(current_user.id),
                        },
                        "checkout": {
                            "url": data.return_url or f"{settings.APP_URL}/dashboard/billing",
                        },
                    },
                )

                if response.status_code == 201:
                    result = response.json()
                    checkout_url = result.get("data", {}).get("checkout", {}).get("url")
                    if checkout_url:
                        return CheckoutResponse(checkout_url=checkout_url)

                # Fallback to client-side checkout
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create checkout session"
                )

        except httpx.RequestError as e:
            # Log error and fallback
            print(f"Paddle API error: {e}")

    # Development fallback - return mock URL
    return CheckoutResponse(
        checkout_url=f"https://sandbox-checkout.paddle.com/?plan={data.plan_id}&email={current_user.email}"
    )


class UsageResponse(BaseModel):
    plan: str
    tokens_balance: int
    tokens_used_this_month: int
    projects_count: int
    projects_limit: int
    subscription_id: Optional[str] = None


@router.get("/usage", response_model=UsageResponse)
async def get_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current usage and billing information."""
    from ..models.project import Project

    # Count projects
    result = await db.execute(
        select(Project).where(Project.owner_id == current_user.id)
    )
    projects = result.scalars().all()

    # TODO: Calculate tokens used this month from AISession
    tokens_used = 0

    # Plan limits
    plan_limits = {
        "free": 1,
        "pro": 5,
        "team": 20,
        "enterprise": 1000
    }

    return UsageResponse(
        plan=current_user.plan.value,
        tokens_balance=current_user.tokens_balance,
        tokens_used_this_month=tokens_used,
        projects_count=len(projects),
        projects_limit=plan_limits.get(current_user.plan.value, 1),
        subscription_id=current_user.paddle_subscription_id,
    )


@router.post("/webhook")
async def paddle_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    paddle_signature: Optional[str] = Header(None, alias="Paddle-Signature"),
):
    """Handle Paddle webhook events."""
    body = await request.body()

    # Verify signature in production
    if settings.PADDLE_WEBHOOK_SECRET and paddle_signature:
        if not verify_paddle_signature(body, paddle_signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

    data = await request.json()
    event_type = data.get("event_type")
    event_data = data.get("data", {})

    # Extract user ID from custom_data
    custom_data = event_data.get("custom_data", {})
    user_id = custom_data.get("user_id")

    if not user_id:
        return {"status": "ignored", "reason": "no_user_id"}

    # Find user
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        return {"status": "error", "reason": "user_not_found"}

    # Handle different event types
    if event_type == "subscription.created":
        # New subscription
        subscription_id = event_data.get("id")
        items = event_data.get("items", [])

        # Determine plan from price ID
        plan = PlanType.PRO  # Default to Pro
        for item in items:
            price_id = item.get("price", {}).get("id")
            if price_id == getattr(settings, "PADDLE_TEAM_PRICE_ID", None):
                plan = PlanType.TEAM
                break

        user.plan = plan
        user.paddle_subscription_id = subscription_id
        user.tokens_balance = (
            settings.PLAN_TEAM_TOKENS if plan == PlanType.TEAM
            else settings.PLAN_PRO_TOKENS
        )

    elif event_type == "subscription.updated":
        # Subscription changed (upgrade/downgrade)
        items = event_data.get("items", [])

        for item in items:
            price_id = item.get("price", {}).get("id")
            if price_id == getattr(settings, "PADDLE_TEAM_PRICE_ID", None):
                user.plan = PlanType.TEAM
                user.tokens_balance = settings.PLAN_TEAM_TOKENS
            elif price_id == getattr(settings, "PADDLE_PRO_PRICE_ID", None):
                user.plan = PlanType.PRO
                user.tokens_balance = settings.PLAN_PRO_TOKENS

    elif event_type == "subscription.canceled":
        # Subscription cancelled - revert to free at period end
        # Note: User keeps plan until subscription.ended
        pass

    elif event_type == "subscription.ended":
        # Subscription ended - revert to free
        user.plan = PlanType.FREE
        user.paddle_subscription_id = None
        user.tokens_balance = settings.PLAN_FREE_TOKENS

    elif event_type == "transaction.completed":
        # One-time payment completed (e.g., token packs)
        # Handle token purchases here
        pass

    await db.commit()

    return {"status": "ok", "event": event_type}


@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel current subscription."""
    if not current_user.paddle_subscription_id:
        raise HTTPException(status_code=400, detail="No active subscription")

    if settings.PADDLE_API_KEY:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"https://api.paddle.com/subscriptions/{current_user.paddle_subscription_id}/cancel",
                    headers={
                        "Authorization": f"Bearer {settings.PADDLE_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={"effective_from": "next_billing_period"},
                )

                if response.status_code == 200:
                    return {"message": "Subscription will be cancelled at end of billing period"}

                raise HTTPException(
                    status_code=500,
                    detail="Failed to cancel subscription"
                )

        except httpx.RequestError as e:
            print(f"Paddle API error: {e}")
            raise HTTPException(status_code=500, detail="Service unavailable")

    # Development mode
    return {"message": "Subscription cancellation requested (mock)"}
