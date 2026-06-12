from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select

from app.core.db import get_session
from app.modules.resources.models import Operator, Shift, Skill
from app.modules.resources.schemas import (
    GenerateOperatorsRequest,
    GenerateOperatorsResponse,
    OperatorRead,
    ShiftRead,
    SkillRead,
)
from app.modules.resources.service import generate_operators

router = APIRouter(tags=["synthetic-human-resources"])


@router.post("/operators/generate", response_model=GenerateOperatorsResponse)
def generate_synthetic_operators(
    request: GenerateOperatorsRequest | None = None,
    session: Session = Depends(get_session),
):
    return generate_operators(session, request or GenerateOperatorsRequest())


@router.get("/operators", response_model=list[OperatorRead])
def list_operators(session: Session = Depends(get_session), limit: int = Query(100, le=1000)):
    return list(session.exec(select(Operator).limit(limit)).all())


@router.get("/skills", response_model=list[SkillRead])
def list_skills(session: Session = Depends(get_session), limit: int = Query(100, le=1000)):
    return list(session.exec(select(Skill).limit(limit)).all())


@router.get("/shifts", response_model=list[ShiftRead])
def list_shifts(session: Session = Depends(get_session), limit: int = Query(100, le=1000)):
    return list(session.exec(select(Shift).limit(limit)).all())
