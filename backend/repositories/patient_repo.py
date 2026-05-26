from rdflib import BNode, Graph

from rdf_store import get_patient_graph, get_store
from rdf_util import copy_subgraph
from sparql import queries


class PatientRepo:
    def list_all(self) -> list[dict]:
        g_patient = get_patient_graph()
        out: list[dict] = []
        for row in g_patient.query(queries.GET_ALL_PATIENTS):
            out.append(
                {
                    "uri": str(row.patient),
                    "nombre": str(row.givenName),
                    "apellido": str(row.familyName),
                }
            )
        return out

    def exists(self, patient_id: str) -> bool:
        g_patient = get_patient_graph()
        return g_patient.query(queries.ASK_PATIENT_EXISTS.format(patient_id=patient_id)).askAnswer

    def get_triples(self, patient_id: str) -> list[dict]:
        g_patient = get_patient_graph()
        return [
            {"predicado": str(p), "objeto": str(o)}
            for p, o in g_patient.query(queries.GET_PATIENT_TRIPLES.format(patient_id=patient_id))
        ]

    def delete(self, patient_id: str) -> None:
        g_patient = get_patient_graph()
        g_patient.update(queries.DELETE_PATIENT_TRIPLES.format(patient_id=patient_id))
        g_patient.commit()

    def get_details(self, patient_uri: str) -> list[dict]:
        store = get_store()
        rows = store.query(queries.PATIENT_GET_ALL_DATA.format(patient_uri=patient_uri))
        out = []
        for row in rows:
            out.append(
                {
                    "nombre": str(row.nombre) if row.nombre else None,
                    "apellidos": str(row.apellidos) if row.apellidos else None,
                    "genero": str(row.genero) if row.genero else None,
                    "fechaNacimiento": str(row.fechaNacimiento) if row.fechaNacimiento else None,
                    "estado_civil": str(getattr(row, "estado_civil", None)) if getattr(row, "estado_civil", None) else None,
                    "telefono": str(getattr(row, "telefono", None)) if getattr(row, "telefono", None) else None,
                    "ss": str(getattr(row, "ss", None)) if getattr(row, "ss", None) else None,
                    "calle": str(getattr(row, "calle", None)) if getattr(row, "calle", None) else None,
                    "cp": str(getattr(row, "cp", None)) if getattr(row, "cp", None) else None,
                    "ciudad": str(getattr(row, "ciudad", None)) if getattr(row, "ciudad", None) else None,
                    "provincia": str(getattr(row, "provincia", None)) if getattr(row, "provincia", None) else None,
                    "pais": str(getattr(row, "pais", None)) if getattr(row, "pais", None) else None,
                }
            )
        return out

    def patch(self, patient_uri: str, update_ttl: str) -> None:
        g_patient = get_patient_graph()
        temp = Graph()
        temp.parse(data=update_ttl, format="turtle")

        for predicate, obj in temp.predicate_objects(patient_uri):
            g_patient.update(f'DELETE WHERE {{ <{patient_uri}> <{predicate}> ?old . }}')
            if isinstance(obj, BNode):
                g_patient.add((patient_uri, predicate, obj))
                copy_subgraph(obj, temp, g_patient)
            else:
                g_patient.add((patient_uri, predicate, obj))
        g_patient.commit()
