from pyshex import ShExEvaluator
from rdflib import Graph

def validate_shex(rdf_path: str, shex_path: str, focus: str) -> bool:
    g = Graph()
    g.parse(rdf_path, format="turtle")

    evaluator = ShExEvaluator(rdf=g, schema=shex_path, start=focus)

    results = evaluator.evaluate()
    return results

""" results = validate_shex("/data", "procedure.shex", "http://hl7.org/fhir/ProcedureShape")

for r in results:
    print(f"Focus: {r.focus}")
    print(f"Result: {r.result}")
    print(f"Reason: {r.reason}")
    print() """