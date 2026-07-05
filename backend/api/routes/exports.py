from fastapi import APIRouter, Depends, Form, HTTPException, Response

from api.deps import require_form_patient_access, require_patient_access
from services.fhir_package_service import SchemaValidationError
from services.export_service import ExportService

router = APIRouter()


def _parse_id_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@router.get("/export_all/{patient_id}")
def export_patient_data(patient_id: str, access=Depends(require_patient_access)):
    try:
        content = ExportService().export_all_zip(patient_id)
    except SchemaValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.to_detail()) from exc

    return Response(
        content=content,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=export_{patient_id}.zip"},
    )


@router.post("/export_seleccionados")
def exportar_seleccionados(
    patient_id: str = Form(...),
    tipo: str = Form(""),
    ids: str = Form(""),
    procedure_ids: str = Form(""),
    allergy_ids: str = Form(""),
    incluir_paciente: str = Form("true"),
    access=Depends(require_form_patient_access),
):
    incluir_datos_paciente = incluir_paciente.lower() == "true"
    procedure_id_list = _parse_id_list(procedure_ids)
    allergy_id_list = _parse_id_list(allergy_ids)
    id_list = _parse_id_list(ids)

    try:
        if procedure_id_list or allergy_id_list:
            content, filename = ExportService().export_mixed_zip(
                patient_id=patient_id,
                procedure_ids=procedure_id_list,
                allergy_ids=allergy_id_list,
                incluir_paciente=incluir_datos_paciente,
            )
        else:
            content, filename = ExportService().export_selected_zip(
                patient_id=patient_id,
                tipo=tipo,
                ids=id_list,
                incluir_paciente=incluir_datos_paciente,
            )
    except SchemaValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.to_detail()) from exc
    except ValueError as exc:
        if str(exc) == "No se encontraron elementos para exportar.":
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not content:
        raise HTTPException(status_code=404, detail="No se encontraron elementos para exportar")

    return Response(
        content=content,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
