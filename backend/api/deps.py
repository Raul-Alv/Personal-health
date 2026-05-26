from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from rdflib import URIRef

from login_funcs import decodificar_token
from repositories.user_repo import UserRepo


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login/")


def get_current_user_uri(token: str = Depends(oauth2_scheme)) -> str:
    user_uri = decodificar_token(token)
    if not user_uri:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_uri


def require_patient_access(patient_id: str, user_uri: str = Depends(get_current_user_uri)) -> tuple[str, URIRef]:
    patient_uri = URIRef(f"http://hl7.org/fhir/Patient/{patient_id}")
    if not UserRepo().has_patient_access(user_uri, patient_uri):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado o sin vinculación")
    return user_uri, patient_uri
