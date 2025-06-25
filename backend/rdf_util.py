from rdflib import Graph, Namespace, Literal, URIRef, RDF, BNode
from typing import List
from pydantic import BaseModel
from pyshex import ShExEvaluator
from fastapi import HTTPException
from sqlalchemy.orm import Session
from hashlib import sha256
from login_funcs import hash_password, verify_password, crear_token

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

def save_registraion(usuario_uri: URIRef, email: str, nombre: str, password: str, db: Session, g: Graph):
    usuario_id = email.split("@")[0]
    usuario_uri = EX[f"Usuario/{usuario_id}"]

    if (usuario_uri, RDF.type, EX.Usuario) in g:
        raise HTTPException(status_code=400, detail="Usuario ya registrado")

    g.add((usuario_uri, RDF.type, EX.Usuario))
    g.add((usuario_uri, EX.email, Literal(email)))
    g.add((usuario_uri, EX.nombre, Literal(nombre)))
    g.add((usuario_uri, EX.hashedPassword, Literal(hash_password(password))))

def login_usuario(email: str, password: str, g: Graph) -> str:
    for subj in g.subjects(EX.email, Literal(email)):
        hashed = g.value(subj, EX.hashedPassword)
        if hashed and verify_password(password, str(hashed)):
            token = crear_token(str(subj))
            return {"access_token": token, "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Credenciales inválidas")

def copy_subgraph(subject, source: Graph, target_ctx):
    """
    Copia todas las triples cuyo sujeto sea 'subject' desde 'source' al contexto 'target_ctx',
    y recursivamente desciende en los objetos que sean BNode.
    """
    for p, o in source.predicate_objects(subject):
        target_ctx.add((subject, p, o))
        if isinstance(o, BNode):
            copy_subgraph(o, source, target_ctx)
    