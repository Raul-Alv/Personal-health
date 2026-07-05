import hashlib

from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef

from repositories.user_repo import UserRepo
from rdf_store import get_allergy_graph, get_patient_graph, get_procedure_graph, get_store, get_user_graph
from rdf_util import copy_subgraph, extraer_valores
from services.fhir_package_service import FhirPackageService

FHIR = Namespace("http://hl7.org/fhir/")
EX = Namespace("http://example.org/fhir/custom#")
FHIR_RESOURCE_BASE = "http://hl7.org/fhir/"
COLLISION_RENAMED_RESOURCE_TYPES = (
    ("Patient", FHIR.Patient),
    ("AllergyIntolerance", FHIR.AllergyIntolerance),
)


class ImportService:
    def __init__(self) -> None:
        self.package_service = FhirPackageService()

    def import_ttl_with_shex(self, user_uri: str, rdf_bytes: bytes, shex_bytes: bytes) -> dict:
        prepared = self.package_service.prepare_import_payload(
            [("datos.ttl", rdf_bytes), ("esquema.shex", shex_bytes)]
        )
        allowed_external_patient_uris = self._allowed_external_patient_uris(user_uri, prepared.graph)
        self.package_service.assert_valid_graph(
            graph=prepared.graph,
            schema_str=prepared.schema_str,
            message="El RDF subido no cumple el esquema ShEx indicado.",
            allowed_external_patient_uris=allowed_external_patient_uris,
        )
        store_result = self._store_graph(user_uri=user_uri, graph=prepared.graph)

        store = get_store()
        g_patient = get_patient_graph()
        g_proc = get_procedure_graph()

        return {
            "ok": True,
            "pacientes_triples": sum(1 for _ in store.triples((None, None, None), context=g_patient.identifier)),
            "procedimientos_triples": sum(1 for _ in store.triples((None, None, None), context=g_proc.identifier)),
            "warnings": store_result["warnings"],
        }

    def preview_files(self, files: list[tuple[str, bytes]], user_uri: str | None = None) -> list[dict]:
        prepared = self.package_service.prepare_import_payload(files)
        allowed_external_patient_uris = (
            self._allowed_external_patient_uris(user_uri, prepared.graph) if user_uri else None
        )
        self.package_service.assert_valid_graph(
            graph=prepared.graph,
            schema_str=prepared.schema_str,
            message="La previsualización ha detectado errores de validación RDF/ShEx.",
            allowed_external_patient_uris=allowed_external_patient_uris,
        )
        return self._build_preview(prepared.graph)

    def confirm_files(self, user_uri: str, files: list[tuple[str, bytes]], set_as_favorite: bool = False) -> dict:
        prepared = self.package_service.prepare_import_payload(files)
        allowed_external_patient_uris = self._allowed_external_patient_uris(user_uri, prepared.graph)
        self.package_service.assert_valid_graph(
            graph=prepared.graph,
            schema_str=prepared.schema_str,
            message="La importación se ha detenido porque el RDF no cumple el esquema ShEx indicado.",
            allowed_external_patient_uris=allowed_external_patient_uris,
        )
        store_result = self._store_graph(
            user_uri=user_uri,
            graph=prepared.graph,
            set_as_favorite=set_as_favorite,
        )
        imported_patient_ids = store_result["imported_patient_ids"]

        redirect_patient_ids = imported_patient_ids or self._referenced_patient_ids(prepared.graph)
        response: dict[str, object]
        if len(redirect_patient_ids) == 1:
            response = {"redirect": f"/patient/{redirect_patient_ids[0]}"}
        else:
            response = {"redirect": "/profile"}
        if store_result["warnings"]:
            response["warnings"] = store_result["warnings"]
        return response

    def _allowed_external_patient_uris(self, user_uri: str, graph: Graph) -> set[str]:
        package_patient_uris = {str(subject) for subject in graph.subjects(RDF.type, FHIR.Patient)}
        referenced_patient_uris = self.package_service.collect_patient_reference_uris(graph)
        external_patient_uris = referenced_patient_uris - package_patient_uris
        user_repo = UserRepo()
        return {
            patient_uri
            for patient_uri in external_patient_uris
            if user_repo.has_patient_access(user_uri, URIRef(patient_uri))
        }

    def _referenced_patient_ids(self, graph: Graph) -> list[str]:
        return sorted(
            patient_uri.rsplit("/", 1)[-1]
            for patient_uri in self.package_service.collect_patient_reference_uris(graph)
        )

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
    def _store_graph(user_uri: str, graph: Graph, set_as_favorite: bool = False) -> dict[str, list[str]]:
        g_user = get_user_graph()
        g_patient = get_patient_graph()
        g_proc = get_procedure_graph()
        g_allergy = get_allergy_graph()
        graph = ImportService._avoid_resource_collisions(
            user_uri=user_uri,
            graph=graph,
            target_graphs={
                "Patient": g_patient,
                "Procedure": g_proc,
                "AllergyIntolerance": g_allergy,
            },
        )

        imported_patient_ids: list[str] = []
        for subj in graph.subjects(RDF.type, FHIR.Patient):
            if (subj, RDF.type, FHIR.Patient) not in g_patient:
                copy_subgraph(subj, graph, g_patient)
            imported_patient_ids.append(str(subj).split("/")[-1])

        imported_procedure_ids: list[str] = []
        skipped_procedure_ids: list[str] = []
        for subj in graph.subjects(RDF.type, FHIR.Procedure):
            procedure_id = str(subj).split("/")[-1]
            if ImportService._resource_exists(g_proc, subj):
                skipped_procedure_ids.append(procedure_id)
            else:
                ImportService._copy_procedure_subgraph(subj, graph, g_proc)
                imported_procedure_ids.append(procedure_id)

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
        warnings = [
            f"No se ha cargado el procedimiento '{procedure_id}' porque ya existe."
            for procedure_id in skipped_procedure_ids
        ]
        return {
            "imported_patient_ids": imported_patient_ids,
            "imported_procedure_ids": imported_procedure_ids,
            "skipped_procedure_ids": skipped_procedure_ids,
            "warnings": warnings,
        }

    @staticmethod
    def _copy_procedure_subgraph(subject: URIRef, source: Graph, target: Graph) -> None:
        copy_subgraph(subject, source, target)
        existing_notes = set(ImportService._procedure_note_texts(subject, target))
        for note_literal in ImportService._procedure_note_literals(subject, source):
            if str(note_literal) in existing_notes:
                continue

            note_node = BNode()
            text_node = BNode()
            target.add((subject, FHIR["Procedure.note"], note_node))
            target.add((note_node, FHIR["Annotation.text"], text_node))
            target.add((text_node, FHIR.value, note_literal))
            existing_notes.add(str(note_literal))

    @staticmethod
    def _procedure_note_literals(subject: URIRef, graph: Graph) -> list[Literal]:
        notes: list[Literal] = []
        for note_node in graph.objects(subject, FHIR["Procedure.note"]):
            for text_node in graph.objects(note_node, FHIR["Annotation.text"]):
                if isinstance(text_node, Literal):
                    notes.append(text_node)
                    continue
                for value in graph.objects(text_node, FHIR.value):
                    if isinstance(value, Literal):
                        notes.append(value)
                    else:
                        notes.append(Literal(str(value)))
        return notes

    @staticmethod
    def _procedure_note_texts(subject: URIRef, graph: Graph) -> list[str]:
        return [str(note) for note in ImportService._procedure_note_literals(subject, graph)]

    @staticmethod
    def _avoid_resource_collisions(user_uri: str, graph: Graph, target_graphs: dict[str, Graph]) -> Graph:
        uri_map = ImportService._build_collision_renames(user_uri, graph, target_graphs)
        if not uri_map:
            return graph
        return ImportService._rewrite_graph_resources(graph, uri_map)

    @staticmethod
    def _build_collision_renames(user_uri: str, graph: Graph, target_graphs: dict[str, Graph]) -> dict[URIRef, URIRef]:
        uri_map: dict[URIRef, URIRef] = {}
        reserved_uris = {subject for subject in graph.subjects() if isinstance(subject, URIRef)}
        owner_suffix = hashlib.sha1(user_uri.encode("utf-8")).hexdigest()[:10]

        for resource_type, rdf_type in COLLISION_RENAMED_RESOURCE_TYPES:
            target_graph = target_graphs[resource_type]
            for subject in graph.subjects(RDF.type, rdf_type):
                if not isinstance(subject, URIRef) or subject in uri_map:
                    continue

                parsed = ImportService._split_fhir_resource_uri(subject)
                if parsed is None or parsed[0] != resource_type:
                    continue

                if not ImportService._resource_exists(target_graph, subject):
                    continue

                uri_map[subject] = ImportService._next_available_resource_uri(
                    resource_type=resource_type,
                    resource_id=parsed[1],
                    owner_suffix=owner_suffix,
                    target_graph=target_graph,
                    reserved_uris=reserved_uris,
                )
                reserved_uris.add(uri_map[subject])

        return uri_map

    @staticmethod
    def _next_available_resource_uri(
        resource_type: str,
        resource_id: str,
        owner_suffix: str,
        target_graph: Graph,
        reserved_uris: set[URIRef],
    ) -> URIRef:
        base_resource_id = f"{resource_id}--imported-{owner_suffix}"
        counter = 1

        while True:
            suffix = "" if counter == 1 else f"-{counter}"
            candidate = URIRef(f"{FHIR_RESOURCE_BASE}{resource_type}/{base_resource_id}{suffix}")
            if candidate not in reserved_uris and not ImportService._resource_exists(target_graph, candidate):
                return candidate
            counter += 1

    @staticmethod
    def _rewrite_graph_resources(graph: Graph, uri_map: dict[URIRef, URIRef]) -> Graph:
        rewritten = Graph()
        for prefix, namespace in graph.namespaces():
            rewritten.bind(prefix, namespace, override=True)

        literal_map = ImportService._build_reference_literal_map(uri_map)
        for subject, predicate, obj in graph:
            rewritten.add(
                (
                    ImportService._rewrite_uri(subject, uri_map),
                    ImportService._rewrite_uri(predicate, uri_map),
                    ImportService._rewrite_object(obj, uri_map, literal_map),
                )
            )
        return rewritten

    @staticmethod
    def _build_reference_literal_map(uri_map: dict[URIRef, URIRef]) -> dict[str, str]:
        literal_map: dict[str, str] = {}
        for old_uri, new_uri in uri_map.items():
            old_parts = ImportService._split_fhir_resource_uri(old_uri)
            new_parts = ImportService._split_fhir_resource_uri(new_uri)
            if old_parts is None or new_parts is None or old_parts[0] != new_parts[0]:
                continue

            resource_type, old_id = old_parts
            _, new_id = new_parts
            literal_map[str(old_uri)] = str(new_uri)
            literal_map[f"{resource_type}/{old_id}"] = f"{resource_type}/{new_id}"
        return literal_map

    @staticmethod
    def _rewrite_uri(value, uri_map: dict[URIRef, URIRef]):
        if isinstance(value, URIRef):
            return uri_map.get(value, value)
        return value

    @staticmethod
    def _rewrite_object(value, uri_map: dict[URIRef, URIRef], literal_map: dict[str, str]):
        if isinstance(value, URIRef):
            return uri_map.get(value, value)
        if isinstance(value, Literal):
            replacement = literal_map.get(str(value))
            if replacement is not None:
                return Literal(replacement, datatype=value.datatype, lang=value.language)
        return value

    @staticmethod
    def _split_fhir_resource_uri(uri: URIRef) -> tuple[str, str] | None:
        value = str(uri)
        if not value.startswith(FHIR_RESOURCE_BASE):
            return None

        remainder = value[len(FHIR_RESOURCE_BASE):]
        resource_type, separator, resource_id = remainder.partition("/")
        if not separator or not resource_type or not resource_id:
            return None
        return resource_type, resource_id

    @staticmethod
    def _resource_exists(graph: Graph, uri: URIRef) -> bool:
        return (uri, None, None) in graph
