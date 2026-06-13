from collections.abc import Generator

from sqlalchemy import text
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings


def import_all_models() -> None:
    from app.modules.events import models as events_models  # noqa: F401
    from app.modules.master_data import models as master_data_models  # noqa: F401
    from app.modules.materials import models as materials_models  # noqa: F401
    from app.modules.optimizer import models as optimizer_models  # noqa: F401
    from app.modules.qc_ncr import models as qc_ncr_models  # noqa: F401
    from app.modules.resources import models as resources_models  # noqa: F401
    from app.modules.risk import models as risk_models  # noqa: F401
    from app.modules.scenarios import models as scenarios_models  # noqa: F401
    from app.modules.simulation import models as simulation_models  # noqa: F401


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
    import_all_models()
    SQLModel.metadata.create_all(engine)


def reset_db_and_tables() -> None:
    engine = get_engine()
    if engine is None:
        raise RuntimeError("Database connection string is not configured.")
    import_all_models()
    SQLModel.metadata.drop_all(engine)
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
