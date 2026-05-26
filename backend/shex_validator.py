from pathlib import Path

from rdflib import Graph

from services.fhir_package_service import FhirPackageService


def validate_shex(rdf_path: str, shex_path: str, focus: str | None = None) -> list[tuple[str, str, str]]:
    graph = Graph()
    graph.parse(rdf_path, format="turtle")
    schema = Path(shex_path).read_text(encoding="utf-8")

    package_service = FhirPackageService()
    errors = package_service.validate_graph(graph=graph, schema_str=schema)

    if focus:
        errors = [item for item in errors if item["focus"] == focus]

    return [(item["focus"], item["shape"], item["reason"]) for item in errors]
