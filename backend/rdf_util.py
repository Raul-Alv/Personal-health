from rdflib import Graph, Namespace, Literal, URIRef
from typing import List
from pydantic import BaseModel
from . import Paciente, Practicante, Diente, Procedimiento, StatusProcedimiento



def parse_rdf_string(rdf_string: str) -> dict:
    g = Graph()
    g.parse(data=rdf_string, format="turtle")

    data = {}
    for s, p, o in g:
        subject = str(s)
        predicate = str(p)
        obj = str(o)
        if subject not in data:
            data[subject] = {}
        if predicate not in data[subject]:
            data[subject][predicate] = []
        data[subject][predicate].append(obj)
    return data


