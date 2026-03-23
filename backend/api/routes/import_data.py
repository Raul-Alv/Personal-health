from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from api.deps import get_current_user_uri
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
    result = ImportService().import_ttl_with_shex(user_uri=user_uri, rdf_bytes=rdf_bytes, shex_bytes=shex_bytes)
    if not result["ok"]:
        raise HTTPException(status_code=400, detail={"validation_errors": result["errors"]})
    return {k: v for k, v in result.items() if k != "ok"} | {"status": "ok"}


@router.post("/import/preview")
async def preview_import(files: list[UploadFile] = File(...), user_uri: str = Depends(get_current_user_uri)):
    payload = []
    for file in files:
        payload.append((file.filename or "archivo.ttl", await file.read()))
    return ImportService().preview_files(payload)


@router.post("/import/confirm")
async def confirm_import(files: list[UploadFile] = File(...), user_uri: str = Depends(get_current_user_uri)):
    payload = []
    for file in files:
        payload.append((file.filename or "archivo.ttl", await file.read()))
    return ImportService().confirm_files(user_uri=user_uri, files=payload)
