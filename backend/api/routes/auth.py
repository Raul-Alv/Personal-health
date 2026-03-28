from fastapi import APIRouter, Depends, Form, HTTPException

from api.deps import get_current_user_uri
from repositories.user_repo import UserRepo
from rdf_util import resource_uri
from services.auth_service import AuthService

router = APIRouter()


@router.post("/register/")
def registrar_usuario(email: str = Form(...), password: str = Form(...), nombre: str = Form(...)):
    return AuthService().register(email=email, password=password, nombre=nombre)


@router.post("/login/")
def login_usuario(email: str = Form(...), password: str = Form(...)):
    return AuthService().login(email=email, password=password)


@router.get("/me/")
def get_current_user(user_uri: str = Depends(get_current_user_uri)):
    profile = UserRepo().get_profile(user_uri)
    if not profile:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return profile


@router.get("/mis_pacientes/")
def obtener_mis_pacientes(user_uri: str = Depends(get_current_user_uri)):
    return UserRepo().list_my_patients(user_uri)


@router.get("/mis_pacientes/menu")
def obtener_pacientes_menu(user_uri: str = Depends(get_current_user_uri)):
    return UserRepo().list_my_patients(user_uri)


@router.post("/asociar_paciente/")
def asociar_paciente(patient_id: str = Form(...), user_uri: str = Depends(get_current_user_uri)):
    patient_uri = str(resource_uri("Patient", patient_id))
    UserRepo().link_patient(user_uri, patient_uri)
    return {"message": f"Paciente {patient_id} vinculado a {user_uri}"}
