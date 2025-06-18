import tempfile
from fastapi import FastAPI, UploadFile, HTTPException, Depends
from rdflib import Graph, URIRef, RDF, Literal
from pyshex import ShExEvaluator
from database import SessionLocal, engine, Base
from models import Paciente, Practicante, Diente, Procedimiento, Genero, EstadoCivil
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/upload/")
async def upload_rdf_shex(rdf_file: UploadFile, shex_file: UploadFile, start_shape: str, db: Session = Depends(get_db)):
    # Save uploaded files to temp
    with tempfile.NamedTemporaryFile(suffix=".ttl", delete=False) as rdf_temp, tempfile.NamedTemporaryFile(suffix=".shex", delete=False) as shex_temp:
        rdf_bytes = await rdf_file.read()
        shex_bytes = await shex_file.read()

        rdf_temp.write(rdf_bytes)
        shex_temp.write(shex_bytes)

        rdf_path = rdf_temp.name
        shex_path = shex_temp.name

    # Load the RDF data
    g = Graph()
    g.parse(rdf_path, format="ttl")

    # Decode the ShEx schema from the file
    schema_str = open(shex_path, "r", encoding="utf-8").read()
    evaluator = ShExEvaluator(rdf=g, schema=schema_str, start=start_shape)
    results = evaluator.evaluate()

    # gestion de errores
    for r in results:
        if not r.result:
            raise HTTPException(400, detail=f"ShEx failed on focus {r.focus}: {r.reason}")

    # You must provide a focus node and a start shape
    # If unknown, we can extract any URI subject from the graph
    FHIR_PATIENT = URIRef("http://hl7.org/fhir/Patient")
    """ focus_node = next(g.subjects(RDF.type, FHIR_PATIENT), None)
    if not focus_node:
        return {"error": "No subject with rdf:type fhir:Patient found"}
    start_shape = extract_start_shape(shex_schema) #"http://hl7.org/fhir/Patient"  # or a specific shape label like 'http://hl7.org/fhir/shape#PatientShape' """
    
    FHIR_PATIENT = URIRef("http://hl7.org/fhir/Patient")
    for subj in g.subjects(RDF.type, FHIR_PATIENT):
        pid = str(g.value(subj, URIRef("http://hl7.org/fhir/Resource.id")))
        nombre = str(g.value(subj, URIRef("http://hl7.org/fhir/HumanName.given")))
        apellido = str(g.value(subj, URIRef("http://hl7.org/fhir/HumanName.family")))
        genero = Genero(str(g.value(subj, URIRef("http://hl7.org/fhir/Patient.gender"))).upper())
        fecha = str(g.value(subj, URIRef("http://hl7.org/fhir/Patient.birthDate")))
        paciente = Paciente(
            id=pid,
            nombre=nombre,
            apellido=apellido,
            genero=genero,
            fecha_nacimiento=fecha,
            activo=True,
            telefono=None,
            direccion=None,
            estado_civil=None
        )
        db.merge(paciente)

    # Aquí harías lo mismo para Practicante, Diente y Procedimiento,
    # extrayendo sus predicados y haciendo db.merge(…) o db.add(…).

    db.commit()
    return {"status": "ok", "message": "Datos validados y almacenados en DB."}

@app.get("/export/")
def export_procedures(patient_id: str, system: str = "ada"):
    # stubbed
    raw_procedures = [...]  # get from cache or memory
    #exported = [validate_shex(p.code, system) for p in raw_procedures]
    return 0

@app.get("/")
def read_root():
    return {"message": "Bienvenido a tu aplicacion personal de salud!"}

@app.get("/procedures/")
def get_procedures():
    # stubbed
    procedures = get_procedures()
    return procedures

@app.get("/procedures/{procedure_id}") 
def get_procedure(procedure_id: str):
    # stubbed
    procedure = [...]