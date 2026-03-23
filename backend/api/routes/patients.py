from fastapi import APIRouter, Body, Depends, HTTPException, Query

from api.deps import get_current_user_uri, require_patient_access
from repositories.patient_repo import PatientRepo
from repositories.user_repo import UserRepo
from services.patient_service import PatientService

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Bienvenido a tu aplicacion personal de salud!"}


@router.get("/pacientes/")
def listar_pacientes():
    return PatientRepo().list_all()


@router.get("/paciente")
def get_paciente(patient_id: str = Query(..., alias="patient_id")):
    repo = PatientRepo()
    if not repo.exists(patient_id):
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return {"id": patient_id, "tripletas": repo.get_triples(patient_id)}


@router.delete("/pacientes/delete")
def eliminar_paciente(patient_id: str = Query(..., alias="patient_id")):
    repo = PatientRepo()
    if not repo.exists(patient_id):
        raise HTTPException(status_code=404, detail=f"No se encontró ningún paciente con ID {patient_id}")
    repo.delete(patient_id)
    return {"status": "ok", "message": f"Paciente {patient_id} eliminado."}


@router.get("/mis_pacientes/{patient_id}/get/datos")
def obtener_datos_paciente(patient_id: str, access=Depends(require_patient_access)):
    _, patient_uri = access
    return PatientRepo().get_details(str(patient_uri))


@router.patch("/mis_pacientes/{patient_id}/actualizar")
def update_patient(patient_id: str, update: str = Body(...), access=Depends(require_patient_access)):
    return PatientService().patch_patient(patient_id=patient_id, update_ttl=update)
