from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.admin import router as admin_router
from api.routes.allergies import router as allergies_router
from api.routes.auth import router as auth_router
from api.routes.exports import router as exports_router
from api.routes.import_data import router as import_router
from api.routes.patients import router as patients_router
from api.routes.procedures import router as procedures_router


def create_app() -> FastAPI:
    """Crea la aplicación y solo compone routers + middleware.

    Toda la lógica de negocio vive fuera de main.py. Ese es el cambio clave.
    """
    app = FastAPI(title="App Salud Backend")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://[::1]:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router, prefix="/api", tags=["auth"])
    app.include_router(patients_router, prefix="/api", tags=["patients"])
    app.include_router(procedures_router, prefix="/api", tags=["procedures"])
    app.include_router(allergies_router, prefix="/api", tags=["allergies"])
    app.include_router(import_router, prefix="/api", tags=["import"])
    app.include_router(exports_router, prefix="/api", tags=["export"])
    app.include_router(admin_router, prefix="/api", tags=["admin"])
    return app


app = create_app()
