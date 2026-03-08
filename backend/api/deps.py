from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from rdflib import URIRef

from repositories.user_repo import UserRepo
from login_funcs import decodificar_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        user_uri = decodificar_token(token)
        return user_uri
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

def require_patient_access(patient_id: str, current_user: str = Depends(get_current_user)):
    patient_uri = URIRef(f"http://hl7.org/fhir/Patient/{patient_id}")
    if not UserRepo().has_access_to_patient(current_user, patient_uri):
        raise HTTPException(status_code=403, detail="Acceso denegado al paciente")