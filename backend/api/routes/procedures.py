from fastapi import APIRouter, Depends, Query

from api.deps import require_patient_access
from repositories.procedure_repo import ProcedureRepo
from rdf_util import resource_uri

router = APIRouter()


@router.get("/mis_pacientes/{patient_id}/get/procedimientos")
def obtener_procedimientos_paciente(patient_id: str, access=Depends(require_patient_access)):
    return ProcedureRepo().list_by_patient(patient_id)


@router.get("/mis_pacientes/{patient_id}/search/procedimientos")
def buscar_procedimientos_paciente(
    patient_id: str,
    nombre: str | None = Query(default=None),
    fecha: str | None = Query(default=None),
    practicante: str | None = Query(default=None),
    diente: str | None = Query(default=None),
    access=Depends(require_patient_access),
):
    return ProcedureRepo().search_by_patient(
        patient_id,
        nombre=nombre,
        fecha=fecha,
        practicante=practicante,
        diente=diente,
    )


@router.get("/mis_pacientes/{patient_id}/get/procedimientos/{procedure_id}")
def obtener_procedimiento_paciente(patient_id: str, procedure_id: str, access=Depends(require_patient_access)):
    return ProcedureRepo().get_detail(str(resource_uri("Procedure", procedure_id)))


@router.delete("/mis_pacientes/{patient_id}/delete/procedimientos/{procedure_id}")
def delete_procedure(patient_id: str, procedure_id: str, access=Depends(require_patient_access)):
    ProcedureRepo().delete(procedure_id)
    return {"detail": "Procedimiento eliminado"}
