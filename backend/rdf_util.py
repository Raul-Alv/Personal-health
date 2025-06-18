from rdflib import Graph, Namespace, Literal, URIRef, RDF
from typing import List
from pydantic import BaseModel
from pyshex import ShExEvaluator
from models import Paciente, Practicante, Diente, Procedimiento, StatusProcedimiento, Genero
import re
from fastapi import HTTPException
from sqlalchemy.orm import Session

FHIR = Namespace("http://hl7.org/fhir/")
EX = Namespace("http://example.org/fhir/custom#")

def shex_validate_rdf(rdf_string: str, shex_schema: str) -> bool:
    g = Graph()
    g.parse("data.ttl", format="ttl")

    # Load ShEx schema
    #shex_schema = open("fhir.shex", "r").read()

    # Validate against a specific shape
    results = ShExEvaluator().evaluate(
        rdf=g,
        schema=shex_schema,
        focus=None,  # or specific subject URI
        start=None   # or specific shape
    )

    # Extract matched triples
    for r in results:
        if r.result:
            print(f"Matched Shape: {r.shape}")
            for triple in g.triples((r.focus, None, None)):
                print(triple)


""" def parse_rdf_string(rdf_string: str) -> dict:
    g = Graph()
    g.parse(data=rdf_string, format="turtle")

    for s in g.subjects(RDF.type, FHIR.Patient):
        id = get_literal(g, s, FHIR["Resource.id"])
        nombre = get_literal(g, s, FHIR["HumanName.given"])
        apellido = get_literal(g, s, FHIR["HumanName.family"])
        genero = get_literal(g, s, FHIR["Patient.gender"])
        fecha_nacimiento = get_literal(g, s, FHIR["Patient.birthDate"])
        save_patient(Paciente(
            id=id,
            nombre=nombre,
            apellido=apellido,
            genero=Genero(genero.upper()),
            fecha_nacimiento=fecha_nacimiento
        ))

    for s in g.subjects(RDF.type, FHIR.Practitioner):
        id = get_literal(g, s, FHIR["Resource.id"])
        activo = get_literal(g, s, FHIR["Practitioner.active"]) == "true"
        nombre = get_literal(g, s, FHIR["HumanName.given"])
        apellido = get_literal(g, s, FHIR["HumanName.family"])
        genero = get_literal(g, s, FHIR["Practitioner.gender"])
        telefono = get_literal(g, s, FHIR["ContactPoint.value"])
        cualificacion = get_literal(g, s, FHIR["Practitioner.qualification"])
        save_practitioner(Practicante(
            id=id,
            activo=activo,
            nombre=nombre,
            apellido=apellido,
            genero=Genero(genero.upper()),
            telefono=telefono,
            cualificacion=cualificacion
        ))

    for s in g.subjects(RDF.type, FHIR.Procedure):
        id = get_literal(g, s, FHIR["Resource.id"])
        codigo = get_literal(g, s, FHIR["Coding.code"])
        descripcion = get_literal(g, s, FHIR["CodeableConcept.text"])
        fecha = get_literal(g, s, FHIR["Procedure.performedDateTime"])

        paciente_node = g.value(subject=s, predicate=FHIR["Procedure.subject"])
        paciente_id = get_literal(g, paciente_node, FHIR["Reference.reference"]).split("/")[-1]

        actor_node = g.value(subject=s, predicate=FHIR["Procedure.performer"])
        pract_node = g.value(subject=actor_node, predicate=FHIR["Procedure.performer.actor"])
        pract_id = get_literal(g, pract_node, FHIR["Reference.reference"]).split("/")[-1]

        diente_node = g.value(subject=s, predicate=EX["tooth"])
        diente = Diente(
            codigo=get_literal(g, diente_node, EX["code"]),
            descripcion=get_literal(g, diente_node, EX["description"]),
            titulo=get_literal(g, diente_node, EX["title"])
        )

        save_procedure(Procedimiento(
            id=id,
            codigo=codigo,
            descripcion=descripcion,
            fecha=fecha,
            paciente_id=paciente_id,
            practicante_id=pract_id,
            diente=diente
        ))
 """
def get_literal(graph: Graph, subject, predicate):
    value = graph.value(subject=subject, predicate=predicate)
    if isinstance(value, Literal):
        return str(value)
    elif isinstance(value, URIRef):
        return str(value)
    return ""

def parse_enum(enum_cls, raw, field_name: str, focus: str):
    """
    _enum_cls_: la clase Enum a usar (p.ej. Genero)
    _raw_: el valor crudo del graph (puede ser None)
    _field_name_: nombre del campo (para el mensaje)
    _focus_: el URI del recurso que estás parseando
    """
    if raw is None:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required field `{field_name}` on node {focus}"
        )
    val = str(raw)
    try:
        return enum_cls(val)
    except ValueError:
        allowed = ", ".join([e.value for e in enum_cls])
        raise HTTPException(
            status_code=400,
            detail=(
                f"Invalid value `{val}` for `{field_name}` on node {focus}; "
                f"expected one of [{allowed}]"
            )
        )

def extract_start_shape(shex_str: str) -> str | None:
    # Match lines like: start = @<Patient> or start=@<http://hl7.org/fhir/Patient>
    """ match = re.search(r"start\s*=\s*@?<([^>]+)>", shex_str)
    if match:
        shape_label = match.group(1)
        # Add your namespace prefix logic if needed
        if ":" in shape_label and not shape_label.startswith("http"):
            # Expand prefix (e.g. fhir:Patient)
            prefix, local = shape_label.split(":", 1)
            prefixes = {
                "fhir": "http://hl7.org/fhir/",
                "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                "xsd": "http://www.w3.org/2001/XMLSchema#"
            }
            if prefix in prefixes:
                return prefixes[prefix] + local
        return shape_label  # already a full URI """
    return None
