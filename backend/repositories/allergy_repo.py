from rdflib import URIRef

from rdf_store import get_allergy_graph
from sparql import queries


class AllergyRepo:
    def list_by_patient(self, patient_id: str) -> list[dict]:
        graph = get_allergy_graph()
        rows = graph.query(queries.ALLERGY_GET_LIST_DETAILS.format(patient_id=patient_id))
        out: list[dict] = []
        for row in rows:
            out.append(
                {
                    "alergia_uri": str(row.alergia),
                    "display": str(row.display) if row.display else None,
                    "code": str(row.code) if row.code else None,
                    "status": str(row.status) if row.status else None,
                    "onsetDateTime": str(row.onsetDateTime) if row.onsetDateTime else None,
                    "performerRef": str(row.performerRef) if row.performerRef else None,
                    "category": str(row.category) if row.category else None,
                }
            )
        return out

    def delete(self, allergy_id: str) -> None:
        g = get_allergy_graph()
        g.remove((URIRef(f"http://hl7.org/fhir/AllergyIntolerance/{allergy_id}"), None, None))
        g.commit()
