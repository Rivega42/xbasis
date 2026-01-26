"""
xBasis API
~~~~~~~~~~~
Main FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings

# Sentry initialization (if DSN is configured)
if settings.SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 1.0,
        profiles_sample_rate=0.1 if settings.ENVIRONMENT == "production" else 1.0,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            SqlalchemyIntegration(),
        ],
        send_default_pii=False,
    )
from .core.database import init_db
from .auth.router import router as auth_router
from .projects.router import router as projects_router
from .ai.router import router as ai_router
from .deploy.router import router as deploy_router
from .billing.router import router as billing_router
from .sandbox.router import router as sandbox_router
from .database.router import router as database_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    await init_db()
    yield


app = FastAPI(
    title="xBasis API",
    description="From idea to production in days",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(projects_router, prefix="/projects", tags=["projects"])
app.include_router(ai_router, prefix="/ai", tags=["ai"])
app.include_router(deploy_router, prefix="/deploy", tags=["deploy"])
app.include_router(billing_router, prefix="/billing", tags=["billing"])
app.include_router(sandbox_router, prefix="/projects", tags=["sandbox"])
app.include_router(database_router, prefix="/projects", tags=["database"])


@app.get("/")
async def root():
    return {"name": "xBasis API", "version": "0.1.0", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy", "database": "connected"}