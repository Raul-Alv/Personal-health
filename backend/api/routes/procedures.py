from fastapi import APIRouter, Depends
from rdflib import URIRef
from backend.api.deps import require_patient_access
from backend.repositories.procedure_repo import ProcedureRepo

router = APIRouter()

@router.get("/mis_pacientes/{patient_id}/get/procedimientos")
def procedimientos(patient_id: str, access=Depends(require_patient_access)):
    return ProcedureRepo().list_by_patient(patient_id)

@router.get("/mis_pacientes/{patient_id}/get/procedimientos/{procedure_id}")
def procedimiento_detalle(patient_id: str, procedure_id: str, access=Depends(require_patient_access)):
    procedure_uri = str(URIRef(f"http://hl7.org/fhir/Procedure/{procedure_id}"))
    return ProcedureRepo().get_detail(procedure_uri)
