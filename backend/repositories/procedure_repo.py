from rdflib import URIRef

from rdf_store import get_procedure_graph, get_store
from sparql import queries


class ProcedureRepo:
    def list_by_patient(self, patient_id: str) -> list[dict]:
        store = get_store()
        rows = store.query(queries.PROCEDURE_GET_LIST_DETAILS.format(patient_id=patient_id))
        out: list[dict] = []
        for row in rows:
            out.append(
                {
                    "procedure_uri": str(row.proc),
                    "code": str(row.code) if row.code else None,
                    "text": str(row.text) if row.text else None,
                    "status": str(row.status) if row.status else None,
                    "performedDateTime": str(row.performedDateTime) if row.performedDateTime else None,
                    "performerRef": str(row.performerRef) if row.performerRef else None,
                }
            )
        return out

    def get_detail(self, procedure_uri: str) -> list[dict]:
        store = get_store()
        rows = store.query(queries.PROCEDURE_GET_DETAILS.format(procedure_uri=procedure_uri))
        out = []
        for row in rows:
            out.append(
                {
                    "procedure_uri": procedure_uri,
                    "code": str(row.code) if row.code else None,
                    "text": str(row.text) if row.text else None,
                    "status": str(row.status) if row.status else None,
                    "performedDateTime": str(row.performedDateTime) if row.performedDateTime else None,
                    "performerRef": str(row.performerRef) if row.performerRef else None,
                    "dienteCode": str(getattr(row, "dienteCode", None)) if getattr(row, "dienteCode", None) else None,
                    "dienteDisplay": str(getattr(row, "dienteDisplay", None)) if getattr(row, "dienteDisplay", None) else None,
                }
            )
        return out

    def delete(self, procedure_id: str) -> None:
        g = get_procedure_graph()
        g.remove((URIRef(f"http://hl7.org/fhir/Procedure/{procedure_id}"), None, None))
        g.commit()
