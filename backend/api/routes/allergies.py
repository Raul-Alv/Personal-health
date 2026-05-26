from fastapi import APIRouter, Depends

from api.deps import require_patient_access
from repositories.allergy_repo import AllergyRepo

router = APIRouter()


@router.get("/mis_pacientes/{patient_id}/get/alergias")
def obtener_alergias_paciente(patient_id: str, access=Depends(require_patient_access)):
    return AllergyRepo().list_by_patient(patient_id)


@router.delete("/mis_pacientes/{patient_id}/delete/alergias/{allergy_id}")
def delete_allergy(patient_id: str, allergy_id: str, access=Depends(require_patient_access)):
    AllergyRepo().delete(allergy_id)
    return {"detail": "Alergia eliminada"}
