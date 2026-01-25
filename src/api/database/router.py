"""
Database API endpoints for user project databases.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..models.user import User
from ..models.project import Project
from ..auth.router import get_current_user
from .manager import get_database_manager, TableInfo, QueryResult, MigrationInfo


router = APIRouter()


# ════════════════════════════════════════════
# Schemas
# ════════════════════════════════════════════

class ColumnSchema(BaseModel):
    name: str
    type: str
    nullable: bool
    default: Optional[str] = None
    is_primary: bool = False


class TableSchema(BaseModel):
    name: str
    columns: List[ColumnSchema]
    row_count: int


class QueryRequest(BaseModel):
    sql: str
    readonly: bool = False


class QueryResponse(BaseModel):
    columns: List[str]
    rows: List[List]
    affected_rows: int
    error: Optional[str] = None


class MigrationRequest(BaseModel):
    sql: str
    description: str = ""


class MigrationResponse(BaseModel):
    id: int
    description: str
    sql: str
    applied_at: str


class GenerateMigrationRequest(BaseModel):
    request: str  # "Добавь поле avatar в users"


# ════════════════════════════════════════════
# Helper
# ════════════════════════════════════════════

async def verify_project_access(
    project_id: int,
    current_user: User,
    db: AsyncSession,
) -> Project:
    """Verify user has access to project."""
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
    
    return project


# ════════════════════════════════════════════
# Endpoints
# ════════════════════════════════════════════

@router.post("/{project_id}/database")
async def create_database(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Initialize database for project. Creates PostgreSQL schema: project_{id}"""
    await verify_project_access(project_id, current_user, db)
    
    db_manager = get_database_manager()
    info = await db_manager.create_database(project_id)
    
    return {
        "status": "created",
        "schema_name": info.schema_name,
    }


@router.delete("/{project_id}/database")
async def drop_database(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Drop database for project. This is irreversible!"""
    await verify_project_access(project_id, current_user, db)
    
    db_manager = get_database_manager()
    await db_manager.drop_database(project_id)
    
    return {"status": "dropped"}


@router.get("/{project_id}/database/tables", response_model=List[TableSchema])
async def get_tables(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all tables in project's database."""
    await verify_project_access(project_id, current_user, db)
    
    db_manager = get_database_manager()
    tables = await db_manager.get_tables(project_id)
    
    return [
        TableSchema(
            name=t.name,
            columns=[
                ColumnSchema(
                    name=c.name,
                    type=c.type,
                    nullable=c.nullable,
                    default=c.default,
                    is_primary=c.is_primary,
                )
                for c in t.columns
            ],
            row_count=t.row_count,
        )
        for t in tables
    ]


@router.get("/{project_id}/database/tables/{table}/data", response_model=QueryResponse)
async def get_table_data(
    project_id: int,
    table: str,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get data from a table."""
    await verify_project_access(project_id, current_user, db)
    
    db_manager = get_database_manager()
    result = await db_manager.get_table_data(project_id, table, limit, offset)
    
    if result.error:
        raise HTTPException(status_code=400, detail=result.error)
    
    return QueryResponse(
        columns=result.columns,
        rows=result.rows,
        affected_rows=result.affected_rows,
    )


@router.post("/{project_id}/database/query", response_model=QueryResponse)
async def execute_query(
    project_id: int,
    data: QueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Execute SQL query. Use readonly=true for SELECT only mode."""
    await verify_project_access(project_id, current_user, db)
    
    db_manager = get_database_manager()
    result = await db_manager.execute_sql(
        project_id,
        data.sql,
        readonly=data.readonly,
    )
    
    return QueryResponse(
        columns=result.columns,
        rows=result.rows,
        affected_rows=result.affected_rows,
        error=result.error,
    )


@router.post("/{project_id}/database/migrations", response_model=QueryResponse)
async def apply_migration(
    project_id: int,
    data: MigrationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Apply a migration."""
    await verify_project_access(project_id, current_user, db)
    
    db_manager = get_database_manager()
    result = await db_manager.apply_migration(
        project_id,
        data.sql,
        data.description,
    )
    
    if result.error:
        raise HTTPException(status_code=400, detail=result.error)
    
    return QueryResponse(
        columns=[],
        rows=[],
        affected_rows=0,
    )


@router.get("/{project_id}/database/migrations", response_model=List[MigrationResponse])
async def get_migrations(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get list of applied migrations."""
    await verify_project_access(project_id, current_user, db)
    
    db_manager = get_database_manager()
    migrations = await db_manager.get_migrations(project_id)
    
    return [
        MigrationResponse(
            id=m.id,
            description=m.description,
            sql=m.sql,
            applied_at=m.applied_at,
        )
        for m in migrations
    ]


@router.get("/{project_id}/database/schema")
async def get_schema(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current schema as SQL. Useful for AI context."""
    await verify_project_access(project_id, current_user, db)
    
    db_manager = get_database_manager()
    schema_sql = await db_manager.get_schema_sql(project_id)
    
    return {"schema": schema_sql}


@router.post("/{project_id}/database/ai/migration")
async def generate_migration(
    project_id: int,
    data: GenerateMigrationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate migration using AI."""
    project = await verify_project_access(project_id, current_user, db)
    
    db_manager = get_database_manager()
    current_schema = await db_manager.get_schema_sql(project_id)
    
    from ..ai.router import AVAILABLE_MODELS
    from ..core.config import settings
    import httpx
    
    prompt = f"""Current database schema:
```sql
{current_schema}
```

User request: {data.request}

Generate a PostgreSQL migration to fulfill this request.
Output ONLY the SQL, no explanations.
Use proper PostgreSQL syntax."""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.ANTHROPIC_API_KEY,
                "content-type": "application/json",
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30.0,
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="AI generation failed")
        
        result = response.json()
        sql = result["content"][0]["text"].strip()
        
        import re
        sql = re.sub(r'^```sql?\s*', '', sql)
        sql = re.sub(r'\s*```$', '', sql)
    
    return {
        "sql": sql,
        "description": data.request,
    }
