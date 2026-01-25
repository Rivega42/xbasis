"""
Project model.
"""
from datetime import datetime
from enum import Enum
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Integer, DateTime, Enum as SQLEnum, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..core.database import Base

if TYPE_CHECKING:
    from .user import User


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    BUILDING = "building"
    DEPLOYED = "deployed"
    FAILED = "failed"
    ARCHIVED = "archived"


class ProjectType(str, Enum):
    WEB = "web"
    API = "api"
    BOT = "bot"
    STATIC = "static"


class Project(Base):
    __tablename__ = "projects"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[ProjectType] = mapped_column(SQLEnum(ProjectType), default=ProjectType.WEB)
    
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    
    status: Mapped[ProjectStatus] = mapped_column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT)
    
    repo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    branch: Mapped[str] = mapped_column(String(100), default="main")
    
    preview_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    production_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    custom_domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    railway_project_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    railway_service_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    env_vars: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    context_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    auto_deploy: Mapped[bool] = mapped_column(default=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_deployed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    deployments: Mapped[list["Deployment"]] = relationship("Deployment", back_populates="project", cascade="all, delete-orphan")
    ai_sessions: Mapped[list["AISession"]] = relationship("AISession", back_populates="project", cascade="all, delete-orphan")


class Deployment(Base):
    __tablename__ = "deployments"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship("Project", back_populates="deployments")
    environment: Mapped[str] = mapped_column(String(50), default="preview")
    status: Mapped[str] = mapped_column(String(50), default="pending")
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    commit_sha: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    commit_message: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    build_logs: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class AISession(Base):
    __tablename__ = "ai_sessions"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    project: Mapped["Project"] = relationship("Project", back_populates="ai_sessions")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    model: Mapped[str] = mapped_column(String(100))
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    messages: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)