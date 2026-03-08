from fastapi import HTTPException

from login_funcs import crear_token, hash_password, verify_password
from repositories.user_repo import UserRepo

class AuthService:
    def __init__(self):
        self.user_repo = UserRepo()

    def register(self, email: str, name: str, password: str, nombre: str) -> dict:
        if self.user_repo.get_by_email(email):
            raise HTTPException(status_code=400, detail="Usuario ya registrado")
        
        usuario_id = email.split("@")[0]
        usuario_uri = f"http://example.org/fhir/custom#Usuario/{usuario_id}"
        hashed = hash_password(password)
        self.user_repo.create(usuario_uri, name, email, hashed)
        token = crear_token(usuario_uri)
        return {"access_token": token, "token_type": "bearer"}
    
    def login(self, email: str, password: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        user_uri, stored_hashed = user
        if not verify_password(password, stored_hashed):
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")

        return {"access_token": crear_token(user_uri), "token_type": "bearer"}