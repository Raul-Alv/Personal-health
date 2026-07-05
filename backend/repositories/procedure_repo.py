from rdflib import Literal, Namespace, URIRef

from rdf_store import get_procedure_graph
from sparql import queries

FHIR = Namespace("http://hl7.org/fhir/")


class ProcedureRepo:
    @staticmethod
    def _serialize_list_row(row) -> dict:
        procedure_uri = str(row.proc)
        return {
            "procedure_uri": procedure_uri,
            "code": str(row.code) if row.code else None,
            "text": str(row.text) if row.text else None,
            "status": str(row.status) if row.status else None,
            "performedDateTime": str(row.performedDateTime) if row.performedDateTime else None,
            "performerRef": str(row.performerRef) if row.performerRef else None,
            "notes": ProcedureRepo._get_notes(procedure_uri, row),
        }

    @staticmethod
    def _get_notes(procedure_uri: str, row=None) -> str | None:
        notes: list[str] = []
        row_notes = getattr(row, "notes", None) if row is not None else None
        if row_notes:
            notes.extend(note.strip() for note in str(row_notes).split("|") if note.strip())

        graph = get_procedure_graph()
        procedure_ref = URIRef(procedure_uri)
        for note_node in graph.objects(procedure_ref, FHIR["Procedure.note"]):
            for text_node in graph.objects(note_node, FHIR["Annotation.text"]):
                if isinstance(text_node, Literal):
                    notes.append(str(text_node))
                    continue
                for value in graph.objects(text_node, FHIR.value):
                    notes.append(str(value))

        deduped = list(dict.fromkeys(notes))
        return " | ".join(deduped) if deduped else None

    def list_by_patient(self, patient_id: str) -> list[dict]:
        return self.search_by_patient(patient_id)

    def search_by_patient(
        self,
        patient_id: str,
        nombre: str | None = None,
        fecha: str | None = None,
        practicante: str | None = None,
        diente: str | None = None,
    ) -> list[dict]:
        graph = get_procedure_graph()
        rows = graph.query(
            queries.build_procedure_list_query(
                patient_id=patient_id,
                nombre=nombre,
                fecha=fecha,
                practicante=practicante,
                diente=diente,
            )
        )
        return [self._serialize_list_row(row) for row in rows]

    def get_detail(self, procedure_uri: str) -> list[dict]:
        graph = get_procedure_graph()
        rows = graph.query(queries.PROCEDURE_GET_DETAILS.format(procedure_uri=procedure_uri))
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
                    "notes": self._get_notes(procedure_uri, row),
                }
            )
        return out

    def delete(self, procedure_id: str) -> None:
        g = get_procedure_graph()
        g.remove((URIRef(f"http://hl7.org/fhir/Procedure/{procedure_id}"), None, None))
        g.commit()
