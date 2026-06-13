import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./securecop365.db")

# Determine engine config based on the connection string
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
    # Attempt to test connection
    with engine.connect() as conn:
        logger.info(f"Database connected successfully to: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
except Exception as e:
    logger.warning(f"Database connection to {DATABASE_URL} failed with error: {e}. Falling back to SQLite.")
    DATABASE_URL = "sqlite:///./securecop365.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def create_tables():
    from db.models import Base
    # Create tables in the target database
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized successfully.")
    except Exception as ex:
        logger.error(f"Error creating database tables: {ex}")

from fastapi import Request
from sqlalchemy import text
from sqlalchemy.orm import Session, with_loader_criteria
from sqlalchemy import event
import contextvars
from typing import Optional

# ContextVars to store the current request's tenant ID and user role
active_tenant_id = contextvars.ContextVar("active_tenant_id", default=None)
active_user_role = contextvars.ContextVar("active_user_role", default=None)

@event.listens_for(Session, "do_orm_execute")
def enforce_tenant_isolation(execute_state):
    """
    Enforces Row-Level Security (RLS) simulation at the ORM layer.
    Automatically filters queries by tenant_id if active_tenant_id is set.
    """
    if execute_state.execution_options.get("bypass_tenant_gate", False):
        return

    tid = active_tenant_id.get()
    role = active_user_role.get()

    if tid is not None:
        # Super Admin is permitted to bypass automatic tenant filtering
        if role == "Super Admin":
            return

        def tenant_filter(target):
            # Apply filter only to models that have a tenant_id column
            return hasattr(target.class_, "tenant_id")

        execute_state.statement = execute_state.statement.options(
            with_loader_criteria(
                tenant_filter,
                lambda target: target.tenant_id == tid,
                include_aliases=True
            )
        )

def get_db(request: Request = None):
    db = SessionLocal()
    tenant_token = None
    role_token = None
    if request:
        user = getattr(request.state, "user", None)
        if user:
            tenant_id = user.get("tenant_id")
            role = user.get("role")
            
            # Bind context variables
            tenant_token = active_tenant_id.set(tenant_id)
            role_token = active_user_role.set(role)
            
            if engine.dialect.name == "mssql":
                try:
                    db.execute(text("EXEC sp_set_session_context 'tenant_id', :tid"), {"tid": tenant_id})
                    db.execute(text("EXEC sp_set_session_context 'role', :role"), {"role": role})
                except Exception as ex:
                    logger.error(f"Failed to set mssql session context: {ex}")
    try:
        yield db
    finally:
        db.close()
        # Clean up context variables after request completes
        if tenant_token:
            active_tenant_id.reset(tenant_token)
        if role_token:
            active_user_role.reset(role_token)

