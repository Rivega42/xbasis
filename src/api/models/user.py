"""
User model.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base


class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    
    # Profile
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Plan & Billing
    plan: Mapped[PlanType] = mapped_column(SQLEnum(PlanType), default=PlanType.FREE)
    tokens_balance: Mapped[int] = mapped_column(Integer, default=10000)
    paddle_customer_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    paddle_subscription_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User {self.email}>"