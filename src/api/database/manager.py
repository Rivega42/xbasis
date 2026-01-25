"""
Database Manager - PostgreSQL schemas for user projects.

Architecture:
- Shared PostgreSQL server (152-ФЗ compliant, hosted in Russia)
- Each project gets its own SCHEMA (not separate DB)
- Cheaper and easier to manage
- Isolation via schema + permissions
"""

from dataclasses import dataclass
from typing import List, Optional, Any
import re
import logging

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)


@dataclass
class ColumnInfo:
    name: str
    type: str
    nullable: bool
    default: Optional[str] = None
    is_primary: bool = False


@dataclass
class TableInfo:
    name: str
    columns: List[ColumnInfo]
    row_count: int


@dataclass
class QueryResult:
    columns: List[str]
    rows: List[List[Any]]
    affected_rows: int
    error: Optional[str] = None


@dataclass
class MigrationInfo:
    id: int
    description: str
    sql: str
    applied_at: str


@dataclass
class DatabaseInfo:
    project_id: int
    schema_name: str
    tables: List[str]


class DatabaseManager:
    """
    Manages PostgreSQL schemas for user projects.
    
    Each project gets schema: "project_{id}"
    """
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_async_engine(database_url)
    
    def _schema_name(self, project_id: int) -> str:
        """Generate schema name for project."""
        return f"project_{project_id}"
    
    def _validate_identifier(self, name: str) -> bool:
        """Validate SQL identifier (prevent injection)."""
        return bool(re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name))
    
    async def create_database(self, project_id: int) -> DatabaseInfo:
        """Create schema for project."""
        schema = self._schema_name(project_id)
        
        async with self.engine.begin() as conn:
            await conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))
            
            await conn.execute(text(f'''
                CREATE TABLE IF NOT EXISTS "{schema}"._migrations (
                    id SERIAL PRIMARY KEY,
                    description TEXT NOT NULL,
                    sql TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT NOW()
                )
            '''))
        
        logger.info(f"Created database schema for project {project_id}")
        
        return DatabaseInfo(
            project_id=project_id,
            schema_name=schema,
            tables=[],
        )
    
    async def drop_database(self, project_id: int):
        """Drop schema and all its contents."""
        schema = self._schema_name(project_id)
        
        async with self.engine.begin() as conn:
            await conn.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        
        logger.info(f"Dropped database schema for project {project_id}")
    
    async def get_tables(self, project_id: int) -> List[TableInfo]:
        """List all tables in project's schema."""
        schema = self._schema_name(project_id)
        
        async with self.engine.connect() as conn:
            result = await conn.execute(text('''
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = :schema
                AND table_name NOT LIKE '_%'
            '''), {"schema": schema})
            
            tables = []
            for row in result:
                table_name = row[0]
                
                cols_result = await conn.execute(text('''
                    SELECT 
                        c.column_name, 
                        c.data_type, 
                        c.is_nullable,
                        c.column_default,
                        CASE WHEN pk.column_name IS NOT NULL THEN true ELSE false END as is_primary
                    FROM information_schema.columns c
                    LEFT JOIN (
                        SELECT ku.column_name
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage ku 
                            ON tc.constraint_name = ku.constraint_name
                        WHERE tc.table_schema = :schema 
                        AND tc.table_name = :table
                        AND tc.constraint_type = 'PRIMARY KEY'
                    ) pk ON c.column_name = pk.column_name
                    WHERE c.table_schema = :schema AND c.table_name = :table
                    ORDER BY c.ordinal_position
                '''), {"schema": schema, "table": table_name})
                
                columns = [
                    ColumnInfo(
                        name=c[0],
                        type=c[1],
                        nullable=c[2] == "YES",
                        default=c[3],
                        is_primary=c[4],
                    )
                    for c in cols_result
                ]
                
                try:
                    count_result = await conn.execute(
                        text(f'SELECT COUNT(*) FROM "{schema}"."{table_name}"')
                    )
                    row_count = count_result.scalar() or 0
                except:
                    row_count = 0
                
                tables.append(TableInfo(
                    name=table_name,
                    columns=columns,
                    row_count=row_count,
                ))
            
            return tables
    
    async def get_table_data(
        self,
        project_id: int,
        table: str,
        limit: int = 100,
        offset: int = 0,
    ) -> QueryResult:
        """Get data from a table."""
        schema = self._schema_name(project_id)
        
        if not self._validate_identifier(table):
            return QueryResult([], [], 0, "Invalid table name")
        
        try:
            async with self.engine.connect() as conn:
                result = await conn.execute(
                    text(f'SELECT * FROM "{schema}"."{table}" LIMIT :limit OFFSET :offset'),
                    {"limit": limit, "offset": offset}
                )
                
                columns = list(result.keys())
                rows = [[self._serialize_value(cell) for cell in row] for row in result]
                
                return QueryResult(
                    columns=columns,
                    rows=rows,
                    affected_rows=len(rows),
                )
        except Exception as e:
            return QueryResult([], [], 0, str(e))
    
    async def execute_sql(
        self,
        project_id: int,
        sql: str,
        readonly: bool = False,
    ) -> QueryResult:
        """Execute SQL in project's schema."""
        schema = self._schema_name(project_id)
        sql = sql.strip()
        
        sql_upper = sql.upper()
        
        forbidden = ['DROP DATABASE', 'DROP SCHEMA project_', 'TRUNCATE project_']
        for keyword in forbidden:
            if keyword in sql_upper:
                return QueryResult([], [], 0, f"Forbidden operation: {keyword}")
        
        if readonly and not sql_upper.startswith('SELECT'):
            return QueryResult([], [], 0, "Only SELECT allowed in readonly mode")
        
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text(f'SET search_path TO "{schema}"'))
                await conn.execute(text("SET statement_timeout = '30s'"))
                
                result = await conn.execute(text(sql))
                
                if result.returns_rows:
                    columns = list(result.keys())
                    rows = [[self._serialize_value(cell) for cell in row] for row in result]
                    return QueryResult(columns, rows, len(rows))
                else:
                    await conn.commit()
                    return QueryResult([], [], result.rowcount)
                    
        except Exception as e:
            return QueryResult([], [], 0, str(e))
    
    async def apply_migration(
        self,
        project_id: int,
        sql: str,
        description: str = "",
    ) -> QueryResult:
        """Apply migration."""
        schema = self._schema_name(project_id)
        
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text(f'SET search_path TO "{schema}"'))
                await conn.execute(text(sql))
                
                await conn.execute(
                    text('''
                        INSERT INTO _migrations (description, sql) 
                        VALUES (:desc, :sql)
                    '''),
                    {"desc": description, "sql": sql}
                )
                
                logger.info(f"Applied migration for project {project_id}: {description}")
                return QueryResult([], [], 0)
                
        except Exception as e:
            logger.error(f"Migration failed for project {project_id}: {e}")
            return QueryResult([], [], 0, str(e))
    
    async def get_migrations(self, project_id: int) -> List[MigrationInfo]:
        """Get list of applied migrations."""
        schema = self._schema_name(project_id)
        
        try:
            async with self.engine.connect() as conn:
                result = await conn.execute(text(f'''
                    SELECT id, description, sql, applied_at
                    FROM "{schema}"._migrations
                    ORDER BY id DESC
                '''))
                
                return [
                    MigrationInfo(
                        id=row[0],
                        description=row[1],
                        sql=row[2],
                        applied_at=str(row[3]),
                    )
                    for row in result
                ]
        except:
            return []
    
    async def get_schema_sql(self, project_id: int) -> str:
        """Get current schema as SQL (for AI context)."""
        tables = await self.get_tables(project_id)
        
        sql_parts = []
        for table in tables:
            columns_sql = []
            for col in table.columns:
                col_def = f"  {col.name} {col.type}"
                if col.is_primary:
                    col_def += " PRIMARY KEY"
                if not col.nullable:
                    col_def += " NOT NULL"
                if col.default:
                    col_def += f" DEFAULT {col.default}"
                columns_sql.append(col_def)
            
            sql_parts.append(
                f"CREATE TABLE {table.name} (\n"
                + ",\n".join(columns_sql)
                + "\n);"
            )
        
        return "\n\n".join(sql_parts)
    
    def _serialize_value(self, value: Any) -> Any:
        """Convert database values to JSON-serializable format."""
        if value is None:
            return None
        if isinstance(value, (int, float, str, bool)):
            return value
        return str(value)


database_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get database manager instance."""
    global database_manager
    if database_manager is None:
        from ..core.config import settings
        database_manager = DatabaseManager(settings.DATABASE_URL)
    return database_manager
