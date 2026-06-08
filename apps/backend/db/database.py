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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
