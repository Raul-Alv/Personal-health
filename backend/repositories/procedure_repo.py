from rdflib import URIRef

from rdf_store import get_store, get_procedure_graph
from backend.sparql import queries

FHIR_PATIENT_PREFIX = "Patient/"

class ProcedureRepo:
    def list_by_patient(self, patient_id: str) -> list[dict]:
        store = get_store()
        rows = store.query(queries.PROCEDURE_GET_LIST_DETAILS.format(patient_id=patient_id))
        out: list[dict] = []

        for r in rows:
            out.append({
                "procedure_uri": str(r.proc),
                "code": str(r.code) if r.code else None,
                "text": str(r.text) if r.text else None,
                "status": str(r.status) if r.status else None,
                "performedDateTime": str(r.performedDateTime) if r.performedDateTime else None,
                "performerRef": str(r.performerRef) if r.performerRef else None,
            })
        return out

    def get_detail(self, procedure_uri: str) -> dict:
        store = get_store()
        rows = store.query(queries.PROCEDURE_GET_DETAILS.format(procedure_uri=procedure_uri))
        if not rows:
            return {}
        r = rows[0]
        return {
            "procedure_uri": procedure_uri,
            "code": str(r.code) if r.code else None,
            "text": str(r.text) if r.text else None,
            "status": str(r.status) if r.status else None,
            "performedDateTime": str(r.performedDateTime) if r.performedDateTime else None,
            "performerRef": str(r.performerRef) if r.performerRef else None,
            "dienteCode": str(r.dienteCode) if getattr(r, "dienteCode", None) else None,
            "dienteDisplay": str(r.dienteDisplay) if getattr(r, "dienteDisplay", None) else None,
        }
    
    def delete(self, procedure_id: str) -> None:
        g = get_procedure_graph()
        g.remove((URIRef(f"http://hl7.org/fhir/Procedure/{procedure_id}"), None, None))
        g.commit()