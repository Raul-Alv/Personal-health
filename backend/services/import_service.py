import hashlib

from rdflib import BNode, Graph, Literal, Namespace, RDF, URIRef

from repositories.user_repo import UserRepo
from rdf_store import get_allergy_graph, get_patient_graph, get_procedure_graph, get_store, get_user_graph
from rdf_util import copy_subgraph, extraer_valores
from services.fhir_package_service import FhirPackageService, SchemaValidationError

FHIR = Namespace("http://hl7.org/fhir/")
EX = Namespace("http://example.org/fhir/custom#")
FHIR_RESOURCE_BASE = "http://hl7.org/fhir/"
COLLISION_RENAMED_RESOURCE_TYPES = (
    ("Patient", FHIR.Patient),
    ("Procedure", FHIR.Procedure),
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
        target_graphs = {
            "Patient": g_patient,
            "Procedure": g_proc,
            "AllergyIntolerance": g_allergy,
        }
        ImportService._set_patient_identifier_from_resource_id(graph)
        ImportService._assert_imported_patients_are_new_for_user(
            user_uri=user_uri,
            graph=graph,
            user_graph=g_user,
            patient_graph=g_patient,
        )
        graph = ImportService._avoid_resource_collisions(
            user_uri=user_uri,
            graph=graph,
            target_graphs=target_graphs,
        )
        ImportService._assert_no_unhandled_resource_collisions(graph, target_graphs)

        staged_patient = Graph()
        staged_proc = Graph()
        staged_allergy = Graph()
        staged_user = Graph()

        imported_patient_ids: list[str] = []
        for subj in graph.subjects(RDF.type, FHIR.Patient):
            copy_subgraph(subj, graph, staged_patient)
            imported_patient_ids.append(str(subj).split("/")[-1])

        imported_procedure_ids: list[str] = []
        for subj in graph.subjects(RDF.type, FHIR.Procedure):
            procedure_id = str(subj).split("/")[-1]
            ImportService._copy_procedure_subgraph(subj, graph, staged_proc)
            imported_procedure_ids.append(procedure_id)

        imported_allergy_ids: list[str] = []
        for subj in graph.subjects(RDF.type, FHIR.AllergyIntolerance):
            copy_subgraph(subj, graph, staged_allergy)
            imported_allergy_ids.append(str(subj).split("/")[-1])

        favorite_patient_uri: URIRef | None = None
        for patient_id in imported_patient_ids:
            patient_uri = URIRef(f"http://hl7.org/fhir/Patient/{patient_id}")
            staged_user.add((URIRef(user_uri), EX.tienePaciente, patient_uri))

        if set_as_favorite and imported_patient_ids:
            favorite_patient_uri = URIRef(f"http://hl7.org/fhir/Patient/{imported_patient_ids[0]}")

        ImportService._apply_staged_import(
            staged_graphs=[
                (staged_patient, g_patient),
                (staged_proc, g_proc),
                (staged_allergy, g_allergy),
                (staged_user, g_user),
            ],
            user_graph=g_user,
            user_uri=user_uri,
            favorite_patient_uri=favorite_patient_uri,
        )

        return {
            "imported_patient_ids": imported_patient_ids,
            "imported_procedure_ids": imported_procedure_ids,
            "imported_allergy_ids": imported_allergy_ids,
            "skipped_procedure_ids": [],
            "warnings": [],
        }

    @staticmethod
    def _assert_imported_patients_are_new_for_user(
        user_uri: str,
        graph: Graph,
        user_graph: Graph,
        patient_graph: Graph,
    ) -> None:
        linked_patient_uris = {
            patient_uri
            for patient_uri in user_graph.objects(URIRef(user_uri), EX.tienePaciente)
            if isinstance(patient_uri, URIRef)
        }
        if not linked_patient_uris:
            return

        linked_identity_values = {
            patient_uri: ImportService._patient_identity_values(patient_graph, patient_uri)
            for patient_uri in linked_patient_uris
        }
        errors: list[dict] = []

        for patient_uri in graph.subjects(RDF.type, FHIR.Patient):
            display_id = ImportService._patient_display_id(patient_uri)
            duplicate_uri: URIRef | None = None

            if isinstance(patient_uri, URIRef) and patient_uri in linked_patient_uris:
                duplicate_uri = patient_uri
            else:
                incoming_identity_values = ImportService._patient_identity_values(graph, patient_uri)
                for linked_uri, linked_values in linked_identity_values.items():
                    if incoming_identity_values.intersection(linked_values):
                        duplicate_uri = linked_uri
                        break

            if duplicate_uri is None:
                continue

            errors.append(
                {
                    "focus": str(patient_uri),
                    "shape": "PatientImport",
                    "reason": (
                        f"El paciente '{display_id}' ya esta asociado a este usuario "
                        f"como '{ImportService._patient_display_id(duplicate_uri)}'."
                    ),
                }
            )

        if errors:
            raise SchemaValidationError(
                "La importacion se ha detenido porque el paciente ya existe para este usuario.",
                errors=errors,
            )

    @staticmethod
    def _patient_identity_values(graph: Graph, patient_uri) -> set[str]:
        values = ImportService._patient_identifier_values(graph, patient_uri)

        if isinstance(patient_uri, URIRef):
            parsed = ImportService._split_fhir_resource_uri(patient_uri)
            if parsed is not None and parsed[0] == "Patient":
                resource_id = parsed[1]
                values.add(resource_id)
                if "--imported-" in resource_id:
                    values.add(resource_id.split("--imported-", 1)[0])

        return values

    @staticmethod
    def _patient_identifier_values(graph: Graph, patient_uri) -> set[str]:
        values: set[str] = set()
        for identifier_node in graph.objects(patient_uri, FHIR["Patient.identifier"]):
            for value_node in graph.objects(identifier_node, FHIR["Identifier.value"]):
                if isinstance(value_node, Literal):
                    values.add(str(value_node))
                    continue

                for value in graph.objects(value_node, FHIR.value):
                    values.add(str(value))
        return values

    @staticmethod
    def _patient_display_id(patient_uri) -> str:
        if isinstance(patient_uri, URIRef):
            parsed = ImportService._split_fhir_resource_uri(patient_uri)
            if parsed is not None:
                return parsed[1]

        return str(patient_uri)

    @staticmethod
    def _assert_no_unhandled_resource_collisions(graph: Graph, target_graphs: dict[str, Graph]) -> None:
        errors: list[dict] = []
        for resource_type, rdf_type in (
            ("Patient", FHIR.Patient),
            ("Procedure", FHIR.Procedure),
            ("AllergyIntolerance", FHIR.AllergyIntolerance),
        ):
            target_graph = target_graphs[resource_type]
            for subject in graph.subjects(RDF.type, rdf_type):
                if not ImportService._resource_exists(target_graph, subject):
                    continue

                errors.append(
                    {
                        "focus": str(subject),
                        "shape": f"{resource_type}Import",
                        "reason": (
                            f"El recurso {resource_type} '{str(subject).split('/')[-1]}' ya existe "
                            "y no se puede importar sin dejar el paquete incompleto."
                        ),
                    }
                )

        if errors:
            raise SchemaValidationError(
                "La importacion se ha detenido porque algunos recursos ya existen en el sistema.",
                errors=errors,
            )

    @staticmethod
    def _apply_staged_import(
        staged_graphs: list[tuple[Graph, Graph]],
        user_graph: Graph,
        user_uri: str,
        favorite_patient_uri: URIRef | None,
    ) -> None:
        added_by_graph: list[tuple[Graph, list[tuple]]] = []
        removed_favorite_triples: list[tuple] = []

        try:
            for source_graph, target_graph in staged_graphs:
                added_by_graph.append((target_graph, ImportService._add_new_triples(source_graph, target_graph)))

            if favorite_patient_uri is not None:
                favorite_subject = URIRef(user_uri)
                removed_favorite_triples = list(user_graph.triples((favorite_subject, EX.pacienteFavorito, None)))
                for triple in removed_favorite_triples:
                    user_graph.remove(triple)

                favorite_triple = (favorite_subject, EX.pacienteFavorito, favorite_patient_uri)
                if favorite_triple not in user_graph:
                    user_graph.add(favorite_triple)
                    added_by_graph.append((user_graph, [favorite_triple]))

            ImportService._commit_graphs([target for _, target in staged_graphs])
        except Exception:
            ImportService._rollback_import_additions(user_graph, added_by_graph, removed_favorite_triples)
            ImportService._commit_graphs([target for _, target in staged_graphs])
            raise

    @staticmethod
    def _add_new_triples(source_graph: Graph, target_graph: Graph) -> list[tuple]:
        added: list[tuple] = []
        for triple in source_graph:
            if triple in target_graph:
                continue
            target_graph.add(triple)
            added.append(triple)
        return added

    @staticmethod
    def _rollback_import_additions(
        user_graph: Graph,
        added_by_graph: list[tuple[Graph, list[tuple]]],
        removed_favorite_triples: list[tuple],
    ) -> None:
        for graph, triples in reversed(added_by_graph):
            for triple in triples:
                graph.remove(triple)

        if removed_favorite_triples:
            for triple in removed_favorite_triples:
                user_graph.add(triple)

    @staticmethod
    def _commit_graphs(graphs: list[Graph]) -> None:
        committed_ids = set()
        for graph in graphs:
            identifier = id(graph)
            if identifier in committed_ids:
                continue
            graph.commit()
            committed_ids.add(identifier)

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
    def _set_patient_identifier_from_resource_id(graph: Graph) -> None:
        for subject in list(graph.subjects(RDF.type, FHIR.Patient)):
            if not isinstance(subject, URIRef):
                continue

            parsed = ImportService._split_fhir_resource_uri(subject)
            if parsed is None:
                continue

            _, patient_id = parsed
            ImportService._replace_patient_identifier_value(graph, subject, patient_id)

    @staticmethod
    def _replace_patient_identifier_value(graph: Graph, patient_uri: URIRef, patient_id: str) -> None:
        identifier_nodes = list(graph.objects(patient_uri, FHIR["Patient.identifier"]))
        primary_identifier = identifier_nodes[0] if identifier_nodes else BNode()

        if not identifier_nodes:
            graph.add((patient_uri, FHIR["Patient.identifier"], primary_identifier))

        for value_node in list(graph.objects(primary_identifier, FHIR["Identifier.value"])):
            graph.remove((primary_identifier, FHIR["Identifier.value"], value_node))
            ImportService._remove_blank_node_tree(graph, value_node)

        for extra_identifier in identifier_nodes[1:]:
            graph.remove((patient_uri, FHIR["Patient.identifier"], extra_identifier))
            ImportService._remove_blank_node_tree(graph, extra_identifier)

        value_node = BNode()
        graph.add((primary_identifier, FHIR["Identifier.value"], value_node))
        graph.add((value_node, FHIR.value, Literal(patient_id)))

    @staticmethod
    def _remove_blank_node_tree(graph: Graph, node, visited: set[BNode] | None = None) -> None:
        if not isinstance(node, BNode):
            return

        visited = visited or set()
        if node in visited:
            return
        visited.add(node)

        outgoing = list(graph.predicate_objects(node))
        graph.remove((node, None, None))
        for _, child in outgoing:
            ImportService._remove_blank_node_tree(graph, child, visited)

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
