from rdflib import Graph, Namespace, RDF, URIRef

from repositories.user_repo import UserRepo
from rdf_store import get_allergy_graph, get_patient_graph, get_procedure_graph, get_store, get_user_graph
from rdf_util import copy_subgraph, extraer_valores
from services.fhir_package_service import FhirPackageService

FHIR = Namespace("http://hl7.org/fhir/")
EX = Namespace("http://example.org/fhir/custom#")


class ImportService:
    def __init__(self) -> None:
        self.package_service = FhirPackageService()

    def import_ttl_with_shex(self, user_uri: str, rdf_bytes: bytes, shex_bytes: bytes) -> dict:
        prepared = self.package_service.prepare_import_payload(
            [("datos.ttl", rdf_bytes), ("esquema.shex", shex_bytes)]
        )
        self.package_service.assert_valid_graph(
            graph=prepared.graph,
            schema_str=prepared.schema_str,
            message="El RDF subido no cumple el esquema ShEx indicado.",
        )
        self._store_graph(user_uri=user_uri, graph=prepared.graph)

        store = get_store()
        g_patient = get_patient_graph()
        g_proc = get_procedure_graph()

        return {
            "ok": True,
            "pacientes_triples": sum(1 for _ in store.triples((None, None, None), context=g_patient.identifier)),
            "procedimientos_triples": sum(1 for _ in store.triples((None, None, None), context=g_proc.identifier)),
        }

    def preview_files(self, files: list[tuple[str, bytes]]) -> list[dict]:
        prepared = self.package_service.prepare_import_payload(files)
        self.package_service.assert_valid_graph(
            graph=prepared.graph,
            schema_str=prepared.schema_str,
            message="La previsualización ha detectado errores de validación RDF/ShEx.",
        )
        return self._build_preview(prepared.graph)

    def confirm_files(self, user_uri: str, files: list[tuple[str, bytes]], set_as_favorite: bool = False) -> dict:
        prepared = self.package_service.prepare_import_payload(files)
        self.package_service.assert_valid_graph(
            graph=prepared.graph,
            schema_str=prepared.schema_str,
            message="La importación se ha detenido porque el RDF no cumple el esquema ShEx indicado.",
        )
        imported_patient_ids = self._store_graph(
            user_uri=user_uri,
            graph=prepared.graph,
            set_as_favorite=set_as_favorite,
        )

        if len(imported_patient_ids) == 1:
            return {"redirect": f"/paciente/{imported_patient_ids[0]}"}
        return {"redirect": "/profile"}

    @staticmethod
    def _build_preview(graph: Graph) -> list[dict]:
        data: list[dict] = []
        for subj in graph.subjects(RDF.type, FHIR.Patient):
            data.append({"tipo": "paciente", "datos": extraer_valores(graph, subj)})
        for subj in graph.subjects(RDF.type, FHIR.Procedure):
            data.append({"tipo": "procedimiento", "datos": extraer_valores(graph, subj)})
        for subj in graph.subjects(RDF.type, FHIR.AllergyIntolerance):
            data.append({"tipo": "alergia", "datos": extraer_valores(graph, subj)})
        return data

    @staticmethod
    def _store_graph(user_uri: str, graph: Graph, set_as_favorite: bool = False) -> list[str]:
        g_user = get_user_graph()
        g_patient = get_patient_graph()
        g_proc = get_procedure_graph()
        g_allergy = get_allergy_graph()

        imported_patient_ids: list[str] = []
        for subj in graph.subjects(RDF.type, FHIR.Patient):
            if (subj, RDF.type, FHIR.Patient) not in g_patient:
                copy_subgraph(subj, graph, g_patient)
            imported_patient_ids.append(str(subj).split("/")[-1])

        for subj in graph.subjects(RDF.type, FHIR.Procedure):
            if (subj, RDF.type, FHIR.Procedure) not in g_proc:
                copy_subgraph(subj, graph, g_proc)

        for subj in graph.subjects(RDF.type, FHIR.AllergyIntolerance):
            if (subj, RDF.type, FHIR.AllergyIntolerance) not in g_allergy:
                copy_subgraph(subj, graph, g_allergy)

        g_patient.commit()
        g_proc.commit()
        g_allergy.commit()

        for patient_id in imported_patient_ids:
            patient_uri = URIRef(f"http://hl7.org/fhir/Patient/{patient_id}")
            g_user.add((URIRef(user_uri), EX.tienePaciente, patient_uri))
        g_user.commit()

        if set_as_favorite and imported_patient_ids:
            favorite_patient_uri = f"http://hl7.org/fhir/Patient/{imported_patient_ids[0]}"
            UserRepo().set_favorite_patient(user_uri, favorite_patient_uri)
        return imported_patient_ids
