from __future__ import annotations

import io
import re
import zipfile
from contextlib import redirect_stderr
from dataclasses import dataclass
from pathlib import Path

from pyshex import ShExEvaluator
from rdflib import BNode, Graph, Namespace, RDF, URIRef
from rdflib.util import guess_format

from rdf_util import copy_subgraph

FHIR = Namespace("http://hl7.org/fhir/")
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SCHEMA_PATH = BASE_DIR / "schemas" / "fhir_r4_clinical.shex"
SUPPORTED_RDF_SUFFIXES = {".ttl", ".rdf", ".xml"}
SUPPORTED_ARCHIVE_SUFFIXES = {".zip"}
FHIR_ID_RE = re.compile(r"^[A-Za-z0-9\-.]{1,64}$")


class SchemaValidationError(Exception):
    def __init__(self, message: str, errors: list[dict] | None = None):
        super().__init__(message)
        self.message = message
        self.errors = errors or []

    def to_detail(self) -> dict:
        detail: dict[str, object] = {"message": self.message}
        if self.errors:
            detail["validation_errors"] = self.errors
        return detail


@dataclass
class PreparedImportPayload:
    graph: Graph
    rdf_filenames: list[str]
    shex_filename: str
    schema_str: str


class FhirPackageService:
    def load_default_schema(self) -> str:
        return DEFAULT_SCHEMA_PATH.read_text(encoding="utf-8")

    def prepare_import_payload(self, files: list[tuple[str, bytes]]) -> PreparedImportPayload:
        if not files:
            raise SchemaValidationError(
                "Debes subir entre 1 y 3 archivos RDF y un esquema ShEx, o un paquete ZIP exportado por la aplicación."
            )

        normalized_files = self._expand_archives(files)
        shex_files = [(name, content) for name, content in normalized_files if Path(name).suffix.lower() == ".shex"]
        rdf_files = [(name, content) for name, content in normalized_files if Path(name).suffix.lower() in SUPPORTED_RDF_SUFFIXES]

        if not rdf_files:
            raise SchemaValidationError("No se ha encontrado ningún archivo RDF compatible en la importación.")

        if len(rdf_files) > 3:
            raise SchemaValidationError("La importación admite como máximo 3 archivos RDF por paquete.")

        if len(shex_files) != 1:
            raise SchemaValidationError("Debes incluir exactamente un único archivo ShEx para validar el RDF.")

        graph = Graph()
        for filename, content in rdf_files:
            self._parse_rdf_bytes(graph=graph, filename=filename, content=content)

        shex_filename, shex_content = shex_files[0]
        schema_str = self._decode_text(shex_content, shex_filename)

        return PreparedImportPayload(
            graph=graph,
            rdf_filenames=[name for name, _ in rdf_files],
            shex_filename=shex_filename,
            schema_str=schema_str,
        )

    def validate_graph(
        self,
        graph: Graph,
        schema_str: str,
        validate_patient_references: bool = True,
        allowed_external_patient_uris: set[str] | None = None,
    ) -> list[dict]:
        shex_parse_output = io.StringIO()
        try:
            with redirect_stderr(shex_parse_output):
                evaluator = ShExEvaluator(rdf=graph, schema=schema_str)
        except Exception as exc:
            parse_details = " ".join(shex_parse_output.getvalue().split())
            reason = f"No se ha podido interpretar el esquema ShEx: {exc}"
            if parse_details:
                reason = f"{reason}. {parse_details}"
            return [
                {
                    "focus": "schema",
                    "shape": "ShEx",
                    "reason": reason,
                }
            ]

        errors: list[dict] = []
        validated_resources = 0

        for shape_name, resource_type in (
            ("PatientShape", FHIR.Patient),
            ("ProcedureShape", FHIR.Procedure),
            ("AllergyIntoleranceShape", FHIR.AllergyIntolerance),
        ):
            for subject in graph.subjects(RDF.type, resource_type):
                validated_resources += 1
                try:
                    results = evaluator.evaluate(start=shape_name, focus=str(subject))
                except Exception as exc:  # pragma: no cover - depends on pyshex internals
                    errors.append(
                        {
                            "focus": str(subject),
                            "shape": shape_name,
                            "reason": str(exc),
                        }
                    )
                    continue

                for result in results:
                    if not result.result:
                        errors.append(
                            {
                                "focus": str(result.focus),
                                "shape": str(result.start or shape_name),
                                "reason": str(result.reason),
                            }
                        )

        if validated_resources == 0:
            errors.append(
                {
                    "focus": "graph",
                    "shape": "FHIRResources",
                    "reason": "No se han encontrado recursos FHIR Patient, Procedure o AllergyIntolerance en los RDF subidos.",
                }
            )

        if validate_patient_references:
            errors.extend(
                self._validate_patient_references(
                    graph,
                    allowed_external_patient_uris=allowed_external_patient_uris,
                )
            )
        return errors

    def assert_valid_graph(
        self,
        graph: Graph,
        schema_str: str,
        message: str,
        validate_patient_references: bool = True,
        allowed_external_patient_uris: set[str] | None = None,
    ) -> None:
        errors = self.validate_graph(
            graph=graph,
            schema_str=schema_str,
            validate_patient_references=validate_patient_references,
            allowed_external_patient_uris=allowed_external_patient_uris,
        )
        if errors:
            raise SchemaValidationError(message, errors=errors)

    def split_graph_by_resource_type(self, graph: Graph) -> dict[str, Graph]:
        resource_graphs = {
            "paciente.ttl": Graph(),
            "procedimientos.ttl": Graph(),
            "alergias.ttl": Graph(),
        }

        for filename, resource_type in (
            ("paciente.ttl", FHIR.Patient),
            ("procedimientos.ttl", FHIR.Procedure),
            ("alergias.ttl", FHIR.AllergyIntolerance),
        ):
            target_graph = resource_graphs[filename]
            target_graph.namespace_manager.bind("fhir", FHIR, override=True)

            for subject in graph.subjects(RDF.type, resource_type):
                copy_subgraph(subject, graph, target_graph)

        return {
            filename: resource_graph
            for filename, resource_graph in resource_graphs.items()
            if len(resource_graph) > 0
        }

    def build_export_zip(self, graph: Graph, base_filename: str, validate_patient_references: bool = True) -> bytes:
        schema_str = self.load_default_schema()
        self.assert_valid_graph(
            graph=graph,
            schema_str=schema_str,
            message="Los datos exportados no cumplen el perfil RDF/ShEx FHIR configurado para la aplicación.",
            validate_patient_references=validate_patient_references,
        )

        resource_graphs = self.split_graph_by_resource_type(graph)
        if not resource_graphs:
            raise SchemaValidationError("No hay datos RDF que exportar para la selección indicada.")

        mem = io.BytesIO()
        with zipfile.ZipFile(mem, mode="w") as zf:
            for filename, resource_graph in resource_graphs.items():
                zf.writestr(filename, resource_graph.serialize(format="turtle"))
            zf.writestr(f"{base_filename}.shex", schema_str)

        mem.seek(0)
        return mem.read()

    def _expand_archives(self, files: list[tuple[str, bytes]]) -> list[tuple[str, bytes]]:
        archive_files = [item for item in files if Path(item[0]).suffix.lower() in SUPPORTED_ARCHIVE_SUFFIXES]
        if not archive_files:
            return files

        if len(files) != 1 or len(archive_files) != 1:
            raise SchemaValidationError(
                "Si subes un ZIP de exportación, debe ser el único archivo de la importación."
            )

        archive_name, archive_bytes = archive_files[0]
        try:
            with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
                extracted: list[tuple[str, bytes]] = []
                for info in archive.infolist():
                    if info.is_dir():
                        continue

                    entry_name = Path(info.filename).name
                    suffix = Path(entry_name).suffix.lower()
                    if suffix not in SUPPORTED_RDF_SUFFIXES and suffix != ".shex":
                        continue

                    extracted.append((entry_name, archive.read(info)))
        except zipfile.BadZipFile as exc:
            raise SchemaValidationError(f"El archivo '{archive_name}' no es un ZIP válido.") from exc

        if not extracted:
            raise SchemaValidationError(
                f"El ZIP '{archive_name}' no contiene archivos RDF ni ShEx compatibles para la importación."
            )

        return extracted

    def _parse_rdf_bytes(self, graph: Graph, filename: str, content: bytes) -> None:
        text = self._decode_text(content, filename)
        formats: list[str] = []
        guessed = guess_format(filename)
        if guessed:
            formats.append(guessed)

        for fallback in ("turtle", "xml"):
            if fallback not in formats:
                formats.append(fallback)

        last_error: Exception | None = None
        for rdf_format in formats:
            try:
                parsed_graph = Graph()
                parsed_graph.parse(data=text, format=rdf_format)
                for triple in parsed_graph:
                    graph.add(triple)
                return
            except Exception as exc:  # pragma: no cover - rdflib parser specifics vary
                last_error = exc

        raise SchemaValidationError(
            f"No se ha podido interpretar '{filename}' como RDF Turtle ni RDF/XML: {last_error}"
        )

    @staticmethod
    def _decode_text(content: bytes, filename: str) -> str:
        for encoding in ("utf-8-sig", "utf-8", "latin-1"):
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue

        raise SchemaValidationError(f"No se ha podido decodificar el archivo '{filename}' como texto.")

    def collect_patient_reference_uris(self, graph: Graph) -> set[str]:
        patient_uris: set[str] = set()
        resources_with_patient_ref = (
            (FHIR.Procedure, FHIR["Procedure.subject"]),
            (FHIR.AllergyIntolerance, FHIR["AllergyIntolerance.patient"]),
        )

        for resource_type, predicate in resources_with_patient_ref:
            for subject in graph.subjects(RDF.type, resource_type):
                for reference_value in self._extract_reference_values(graph, subject, predicate):
                    normalized_reference = self._normalize_patient_reference(reference_value)
                    if normalized_reference is not None:
                        patient_uris.add(normalized_reference)
        return patient_uris

    def _validate_patient_references(
        self,
        graph: Graph,
        allowed_external_patient_uris: set[str] | None = None,
    ) -> list[dict]:
        package_patient_uris = {str(subject) for subject in graph.subjects(RDF.type, FHIR.Patient)}
        account_patient_uris = allowed_external_patient_uris or set()
        accepted_patient_uris = package_patient_uris | account_patient_uris
        validate_against_account = allowed_external_patient_uris is not None
        errors: list[dict] = []

        resources_with_patient_ref = (
            (FHIR.Procedure, FHIR["Procedure.subject"], "ProcedureSubject"),
            (FHIR.AllergyIntolerance, FHIR["AllergyIntolerance.patient"], "AllergyPatient"),
        )

        for resource_type, predicate, shape_name in resources_with_patient_ref:
            for subject in graph.subjects(RDF.type, resource_type):
                reference_values = self._extract_reference_values(graph, subject, predicate)
                for reference_value in reference_values:
                    normalized_reference = self._normalize_patient_reference(reference_value)
                    if normalized_reference is None:
                        errors.append(
                            {
                                "focus": str(subject),
                                "shape": shape_name,
                                "reason": f"La referencia de paciente '{reference_value}' no tiene un formato FHIR válido.",
                            }
                        )
                        continue

                    if accepted_patient_uris and normalized_reference not in accepted_patient_uris:
                        reason = (
                            f"La referencia '{reference_value}' no apunta a ningun Patient incluido en el paquete RDF."
                        )
                        if validate_against_account:
                            reason = (
                                f"La referencia '{reference_value}' no apunta a ningun Patient incluido en el "
                                "paquete RDF ni a un paciente vinculado a tu cuenta."
                            )
                        errors.append(
                            {
                                "focus": str(subject),
                                "shape": shape_name,
                                "reason": reason,
                            }
                        )

                if not accepted_patient_uris and reference_values:
                    reason = "Hay recursos clinicos con referencia a paciente, pero el paquete no incluye ningun recurso Patient."
                    if validate_against_account:
                        reason = (
                            f"La referencia '{reference_value}' no corresponde a ningun paciente vinculado a tu cuenta."
                        )
                    errors.append(
                        {
                            "focus": str(subject),
                            "shape": shape_name,
                            "reason": reason,
                        }
                    )
                    break

        return errors

    @staticmethod
    def _extract_reference_values(graph: Graph, subject: URIRef, predicate: URIRef) -> list[str]:
        values: list[str] = []
        for reference_node in graph.objects(subject, predicate):
            for reference_value in graph.objects(reference_node, FHIR["Reference.reference"]):
                if isinstance(reference_value, BNode):
                    nested_values = list(graph.objects(reference_value, FHIR.value))
                    if nested_values:
                        values.extend(str(value) for value in nested_values)
                        continue
                values.append(str(reference_value))
        return values

    @staticmethod
    def _normalize_patient_reference(reference_value: str) -> str | None:
        value = reference_value.strip()
        if value.startswith("http://hl7.org/fhir/Patient/"):
            return value
        if value.startswith("Patient/"):
            return f"http://hl7.org/fhir/{value}"
        if FHIR_ID_RE.fullmatch(value):
            return f"http://hl7.org/fhir/Patient/{value}"
        return None
