from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlmodel import Session

from app.core.db import get_session
from app.modules.import_factory.schemas import ImportRunReport, ImportValidationReport
from app.modules.import_factory.service import run_import, validate_csv_files

router = APIRouter(tags=["imports"])


async def read_uploaded_files(files: list[UploadFile]) -> dict[str, bytes]:
    return {file.filename or "": await file.read() for file in files}


@router.post("/validate", response_model=ImportValidationReport)
async def validate_import(files: list[UploadFile] = File(...)):
    return validate_csv_files(await read_uploaded_files(files))


@router.post("/run", response_model=ImportRunReport)
async def run_import_endpoint(
    files: list[UploadFile] = File(...),
    source_name: str | None = Form(default=None),
    session: Session = Depends(get_session),
):
    return run_import(session, await read_uploaded_files(files), source_name=source_name)
