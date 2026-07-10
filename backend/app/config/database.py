from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import settings

import logging

logger = logging.getLogger("inframind_logger")

connect_args = {}
fallback_sqlite = "sqlite:///./inframind_local.db"

try:
    if settings.DATABASE_URL.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
    else:
        engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
    # Test connection
    with engine.connect() as conn:
        pass
except Exception as e:
    logger.warning(f"Primary database connection failed: {e}. Falling back to SQLite: {fallback_sqlite}")
    connect_args = {"check_same_thread": False}
    engine = create_engine(fallback_sqlite, connect_args=connect_args)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
