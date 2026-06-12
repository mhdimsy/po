from typing import Type

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, SQLModel, select

from app.core.db import create_db_and_tables, get_session
from app.modules.master_data import models

router = APIRouter(tags=["master-data"])


def list_entities(model: Type[SQLModel], session: Session, limit: int) -> list[SQLModel]:
    return list(session.exec(select(model).limit(limit)).all())


@router.post("/schema/create")
def create_schema() -> dict:
    create_db_and_tables()
    return {"status": "ok"}


@router.get("/import-batches")
def get_import_batches(session: Session = Depends(get_session), limit: int = Query(100, le=500)):
    return list_entities(models.ImportBatch, session, limit)


@router.get("/boms")
def get_boms(session: Session = Depends(get_session), limit: int = Query(100, le=500)):
    return list_entities(models.BOM, session, limit)


@router.get("/bom-parts")
def get_bom_parts(session: Session = Depends(get_session), limit: int = Query(100, le=500)):
    return list_entities(models.BOMPart, session, limit)


@router.get("/orders")
def get_orders(session: Session = Depends(get_session), limit: int = Query(100, le=500)):
    return list_entities(models.ProductionOrder, session, limit)


@router.get("/order-parts")
def get_order_parts(session: Session = Depends(get_session), limit: int = Query(100, le=500)):
    return list_entities(models.OrderPart, session, limit)


@router.get("/routings")
def get_routings(session: Session = Depends(get_session), limit: int = Query(100, le=500)):
    return list_entities(models.Routing, session, limit)


@router.get("/routing-operations")
def get_routing_operations(session: Session = Depends(get_session), limit: int = Query(100, le=500)):
    return list_entities(models.RoutingOperation, session, limit)


@router.get("/processes")
def get_processes(session: Session = Depends(get_session), limit: int = Query(100, le=500)):
    return list_entities(models.Process, session, limit)


@router.get("/process-types")
def get_process_types(session: Session = Depends(get_session), limit: int = Query(100, le=500)):
    return list_entities(models.ProcessType, session, limit)


@router.get("/machines")
def get_machines(session: Session = Depends(get_session), limit: int = Query(100, le=500)):
    return list_entities(models.Machine, session, limit)


@router.get("/work-centers")
def get_work_centers(session: Session = Depends(get_session), limit: int = Query(100, le=500)):
    return list_entities(models.WorkCenter, session, limit)


@router.get("/machine-processes")
def get_machine_processes(session: Session = Depends(get_session), limit: int = Query(100, le=500)):
    return list_entities(models.MachineProcess, session, limit)
