from pyshex import ShExEvaluator
from rdflib import Graph

def validate_shex(rdf_path:str, shex_path:str, focus: str) -> bool:
    with open(shex_path, 'r') as f:
        schema = f.read()

    g = Graph()
    g.parse(data=rdf_path, format="turtle")

    evaluator = ShExEvaluator(
        rdf = g.serialize(format="turtle"),
        schema = schema,
        focus=focus,
        start="start"
    ).evaluate()

    return [(r.focus, r.result, r.reason) for r in evaluator]