"""
Auth router - registration, login, token refresh.
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
import jwt

from ..core.config import settings
from ..core.database import get_db
from ..core.email import generate_verification_token, get_verification_expiry, send_verification_email
from ..models.user import User, PlanType


router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenRefresh(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str]
    plan: str
    tokens_balance: int
    is_verified: bool
    created_at: datetime
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(user_id: int, token_type: str = "access", token_version: int = 0) -> str:
    if token_type == "access":
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES)
    else:
        expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    payload = {
        "sub": str(user_id),
        "type": token_type,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    # Add version only to refresh tokens (for rotation)
    if token_type == "refresh":
        payload["ver"] = token_version
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    user_id = int(payload.get("sub"))
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is deactivated")
    return user


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="User exists")

    # Generate verification token
    verification_token = generate_verification_token()

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        name=data.name,
        plan=PlanType.FREE,
        tokens_balance=settings.PLAN_FREE_TOKENS,
        verification_token=verification_token,
        verification_expires=get_verification_expiry(),
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # Send verification email (async, don't block registration)
    await send_verification_email(user.email, verification_token, user.name)

    tokens = TokenResponse(
        access_token=create_token(user.id, "access"),
        refresh_token=create_token(user.id, "refresh", user.refresh_token_version),
    )
    return AuthResponse(user=UserResponse.model_validate(user), tokens=tokens)


@router.post("/login", response_model=AuthResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User deactivated")
    tokens = TokenResponse(
        access_token=create_token(user.id, "access"),
        refresh_token=create_token(user.id, "refresh", user.refresh_token_version),
    )
    return AuthResponse(user=UserResponse.model_validate(user), tokens=tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: TokenRefresh, db: AsyncSession = Depends(get_db)):
    payload = decode_token(data.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = int(payload.get("sub"))
    token_version = payload.get("ver", 0)

    # Use FOR UPDATE to prevent race conditions
    result = await db.execute(
        select(User).where(User.id == user_id).with_for_update()
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")

    # Verify token version (detects reuse of old tokens)
    if token_version != user.refresh_token_version:
        # Possible token theft - old token being reused after rotation
        # Could log this as security event
        raise HTTPException(status_code=401, detail="Token expired or revoked")

    # Rotate: increment version to invalidate old refresh token
    user.refresh_token_version += 1
    user.last_refresh_at = datetime.utcnow()
    await db.commit()

    return TokenResponse(
        access_token=create_token(user.id, "access"),
        refresh_token=create_token(user.id, "refresh", user.refresh_token_version),
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Logout user by invalidating all refresh tokens."""
    # Increment version to invalidate all existing refresh tokens
    current_user.refresh_token_version += 1
    await db.commit()
    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


@router.post("/verify-email")
async def verify_email(data: VerifyEmailRequest, db: AsyncSession = Depends(get_db)):
    """Verify user email with token."""
    result = await db.execute(
        select(User).where(User.verification_token == data.token)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")

    if user.is_verified:
        return {"message": "Email already verified"}

    if user.verification_expires and user.verification_expires < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification token expired")

    # Mark as verified
    user.is_verified = True
    user.verification_token = None
    user.verification_expires = None
    await db.commit()

    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification(
    data: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Resend verification email."""
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        # Don't reveal if user exists
        return {"message": "If the email exists, a verification link has been sent"}

    if user.is_verified:
        return {"message": "Email already verified"}

    # Generate new verification token
    user.verification_token = generate_verification_token()
    user.verification_expires = get_verification_expiry()
    await db.commit()

    # Send verification email
    await send_verification_email(user.email, user.verification_token, user.name)

    return {"message": "If the email exists, a verification link has been sent"}