from fastapi import APIRouter, Depends
from backend.api.deps import get_current_user, require_patient_access
from backend.repositories.user_repo import UserRepo
from backend.repositories.patient_repo import PatientRepo

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Bienvenido a tu aplicacion personal de salud!"}

@router.get("/mis_pacientes/")
def mis_pacientes(user_uri: str = Depends(get_current_user)):
    return UserRepo().list_my_patients(user_uri)

@router.get("/mis_pacientes/menu")
def obtener_pacientes_menu(user_uri: str = Depends(get_current_user)):
    return UserRepo().list_my_patients(user_uri)

@router.get("/mis_pacientes/{patient_id}/get/datos")
def datos_paciente(patient_id: str, access=Depends(require_patient_access)):
    _, patient_uri = access
    return PatientRepo().get_details(str(patient_uri))