from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from api.deps import get_current_user_uri
from services.fhir_package_service import SchemaValidationError
from services.import_service import ImportService

router = APIRouter()


@router.post("/upload/")
async def upload_rdf_shex(
    rdf_file: UploadFile = File(...),
    shex_file: UploadFile = File(...),
    user_uri: str = Depends(get_current_user_uri),
):
    rdf_bytes = await rdf_file.read()
    shex_bytes = await shex_file.read()
    try:
        result = ImportService().import_ttl_with_shex(user_uri=user_uri, rdf_bytes=rdf_bytes, shex_bytes=shex_bytes)
    except SchemaValidationError as exc:
        raise HTTPException(status_code=400, detail=exc.to_detail()) from exc
    return {k: v for k, v in result.items() if k != "ok"} | {"status": "ok"}


@router.post("/import/preview")
async def preview_import(files: list[UploadFile] = File(...), user_uri: str = Depends(get_current_user_uri)):
    payload = []
    for file in files:
        payload.append((file.filename or "archivo.ttl", await file.read()))
    try:
        return ImportService().preview_files(payload, user_uri=user_uri)
    except SchemaValidationError as exc:
        raise HTTPException(status_code=400, detail=exc.to_detail()) from exc


@router.post("/import/confirm")
async def confirm_import(
    files: list[UploadFile] = File(...),
    set_as_favorite: bool = Form(False),
    user_uri: str = Depends(get_current_user_uri),
):
    payload = []
    for file in files:
        payload.append((file.filename or "archivo.ttl", await file.read()))
    try:
        return ImportService().confirm_files(user_uri=user_uri, files=payload, set_as_favorite=set_as_favorite)
    except SchemaValidationError as exc:
        raise HTTPException(status_code=400, detail=exc.to_detail()) from exc
