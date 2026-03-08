from rdflib import URIRef

from repositories.patient_repo import PatientRepo


class PatientService:
    def __init__(self) -> None:
        self.repo = PatientRepo()

    def patch_patient(self, patient_id: str, update_ttl: str) -> dict:
        patient_uri = URIRef(f"http://hl7.org/fhir/Patient/{patient_id}")
        self.repo.patch(patient_uri, update_ttl)
        return {"status": "ok", "message": f"Paciente {patient_id} parcheado correctamente."}
