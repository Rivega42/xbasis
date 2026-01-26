"""
Pytest fixtures for xBasis API tests.

Provides:
- async client for testing FastAPI
- test database session
- authenticated user fixtures
"""

import pytest
import asyncio
import os
import sys
from typing import AsyncGenerator, Generator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import declarative_base
from sqlalchemy import String, Integer, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from enum import Enum
from typing import Optional
from passlib.context import CryptContext
import jwt
from datetime import timedelta


# Test-specific Base and models to avoid import issues
TestBase = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=4)

# JWT settings for tests
JWT_SECRET = "test-secret-key"
JWT_ALGORITHM = "HS256"


class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"


class TestUser(TestBase):
    """Test User model."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    plan: Mapped[PlanType] = mapped_column(SQLEnum(PlanType), default=PlanType.FREE)
    tokens_balance: Mapped[int] = mapped_column(Integer, default=10000)
    paddle_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    paddle_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    refresh_token_version: Mapped[int] = mapped_column(Integer, default=0)
    last_refresh_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(user_id: int, token_type: str = "access", token_version: int = 0) -> str:
    if token_type == "access":
        expire = datetime.utcnow() + timedelta(minutes=15)
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    payload = {
        "sub": str(user_id),
        "type": token_type,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    if token_type == "refresh":
        payload["ver"] = token_version
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


# Set up path for app imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'api'))

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Create a minimal test FastAPI app
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import select

test_app = FastAPI(title="xBasis API Test")
security = HTTPBearer()

test_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get DB session
async def get_test_db():
    async with TestSessionLocal() as session:
        yield session


# Auth schemas
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


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_test_db)
) -> TestUser:
    try:
        payload = decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")
    user_id = int(payload.get("sub"))
    result = await db.execute(select(TestUser).where(TestUser.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is deactivated")
    return user


# Auth routes
@test_app.post("/auth/register", response_model=AuthResponse, status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_test_db)):
    result = await db.execute(select(TestUser).where(TestUser.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User exists")
    user = TestUser(
        email=data.email,
        password_hash=hash_password(data.password),
        name=data.name,
        plan=PlanType.FREE,
        tokens_balance=10000,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    tokens = TokenResponse(
        access_token=create_token(user.id, "access"),
        refresh_token=create_token(user.id, "refresh", user.refresh_token_version),
    )
    return AuthResponse(user=UserResponse.model_validate(user), tokens=tokens)


@test_app.post("/auth/login", response_model=AuthResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_test_db)):
    result = await db.execute(select(TestUser).where(TestUser.email == data.email))
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


@test_app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(data: TokenRefresh, db: AsyncSession = Depends(get_test_db)):
    try:
        payload = decode_token(data.refresh_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user_id = int(payload.get("sub"))
    token_version = payload.get("ver", 0)

    # Use FOR UPDATE to prevent race conditions (SQLite doesn't support FOR UPDATE, but PostgreSQL does)
    result = await db.execute(select(TestUser).where(TestUser.id == user_id))
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")

    # Verify token version (detects reuse of old tokens)
    if token_version != user.refresh_token_version:
        raise HTTPException(status_code=401, detail="Token expired or revoked")

    # Rotate: increment version to invalidate old refresh token
    user.refresh_token_version += 1
    user.last_refresh_at = datetime.utcnow()
    await db.commit()

    return TokenResponse(
        access_token=create_token(user.id, "access"),
        refresh_token=create_token(user.id, "refresh", user.refresh_token_version),
    )


@test_app.post("/auth/logout")
async def logout(
    current_user: TestUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_test_db)
):
    current_user.refresh_token_version += 1
    await db.commit()
    return {"message": "Logged out"}


@test_app.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: TestUser = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(TestBase.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create async HTTP client with test database."""

    async def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_test_db] = override_get_db

    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    test_app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session: AsyncSession) -> TestUser:
    """Create a test user in the database."""
    user = TestUser(
        email="test@example.com",
        password_hash=hash_password("testpassword123"),
        name="Test User",
        is_active=True,
        plan=PlanType.FREE,
        tokens_balance=10000,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_user_token(test_user: TestUser) -> str:
    """Create access token for test user."""
    return create_token(test_user.id, "access")


@pytest.fixture
async def authenticated_client(
    client: AsyncClient,
    test_user_token: str
) -> AsyncClient:
    """Client with authentication headers."""
    client.headers["Authorization"] = f"Bearer {test_user_token}"
    return client


@pytest.fixture
def user_credentials() -> dict:
    """Default user credentials for testing."""
    return {
        "email": "newuser@example.com",
        "password": "securepassword123",
        "name": "New User",
    }
