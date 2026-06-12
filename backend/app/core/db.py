from collections.abc import Generator

from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings


def get_database_url() -> str:
    return get_settings().database_url


def get_engine():
    database_url = get_database_url()
    if not database_url:
        return None
    return create_engine(database_url, pool_pre_ping=True)


def create_db_and_tables() -> None:
    engine = get_engine()
    if engine is None:
        return
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    engine = get_engine()
    if engine is None:
        raise RuntimeError("Database connection string is not configured.")
    with Session(engine) as session:
        yield session


def check_database_connection() -> dict:
    engine = get_engine()
    if engine is None:
        return {
            "status": "not_configured",
            "ok": False,
            "message": "SQLSERVER_CONNECTION_STRING or DATABASE_URL is not configured.",
        }
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "ok", "ok": True, "message": "Database connection succeeded."}
    except Exception as exc:
        return {"status": "error", "ok": False, "message": str(exc)}
