from rdflib import BNode, Graph, Namespace, URIRef

FHIR = Namespace("http://hl7.org/fhir/")
EX = Namespace("http://example.org/fhir/custom#")


def copy_subgraph(subject, source: Graph, target: Graph) -> None:
    """Copia un recurso completo, incluyendo blank nodes descendientes.

    Es la utilidad clave para importaciones y exportaciones, porque muchos nodos
    FHIR están modelados como estructuras anidadas con BNodes.
    """
    for predicate, obj in source.predicate_objects(subject):
        target.add((subject, predicate, obj))
        if isinstance(obj, BNode):
            copy_subgraph(obj, source, target)



def extraer_valores(graph: Graph, node, depth: int = 0, max_depth: int = 4) -> dict:
    """Extrae un dict plano y legible para la preview de importación."""
    if depth > max_depth:
        return {}

    data: dict[str, str] = {}
    for predicate, obj in graph.predicate_objects(node):
        pred = str(predicate)
        if isinstance(obj, BNode):
            nested = extraer_valores(graph, obj, depth + 1, max_depth)
            for key, value in nested.items():
                data[f"{pred}__{key}"] = value
        else:
            data[pred] = str(obj)
    return data



def resource_uri(resource_type: str, resource_id: str) -> URIRef:
    return URIRef(f"http://hl7.org/fhir/{resource_type}/{resource_id}")
