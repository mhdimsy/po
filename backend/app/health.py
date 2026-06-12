from fastapi import APIRouter

from app.core.db import check_database_connection

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/health/db")
def database_health() -> dict:
    return check_database_connection()
