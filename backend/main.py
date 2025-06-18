import tempfile
from fastapi import FastAPI, UploadFile, HTTPException, Depends, File, Form
from rdflib import Graph, URIRef, RDF, Literal
from pyshex import ShExEvaluator
from database import SessionLocal, engine, Base
from models import Paciente, Practicante, Diente, Procedimiento, Genero, EstadoCivil
from sqlalchemy.orm import Session
from rdf_util import parse_enum

Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/updateModels/")
async def updateModels():
    # Borra todas las tablas (si existen)…
    Base.metadata.drop_all(bind=engine)
    # …y créalas de nuevo según tu modelo
    Base.metadata.create_all(bind=engine)

@app.post("/upload/")
async def upload_rdf_shex(rdf_file: UploadFile = File(...), shex_file: UploadFile = File(...), start_shape: str = Form(...), db: Session = Depends(get_db)):
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

        # Recolectamos todos los fallos en detalle
    errores = []
    for r in results:
        if not r.result:
            # 1) Introspección de atributos “públicos”
            info = {
                attr: getattr(r, attr)
                for attr in dir(r)
                if not attr.startswith("_") and not callable(getattr(r, attr))
            }
            errores.append(info)

    if errores:
        # Devolvemos todos los atributos disponibles para inspección
        raise HTTPException(
            status_code=400,
            detail={
                "validation_errors": errores,
                "note": "Mira las keys devueltas para saber qué atributos usar (p.ej. 'shape_label', 'value', etc.)"
            }
        )

    # You must provide a focus node and a start shape
    # If unknown, we can extract any URI subject from the graph
    FHIR_PATIENT = URIRef("http://hl7.org/fhir/Patient")
    """ focus_node = next(g.subjects(RDF.type, FHIR_PATIENT), None)
    if not focus_node:
        return {"error": "No subject with rdf:type fhir:Patient found"}
    start_shape = extract_start_shape(shex_schema) #"http://hl7.org/fhir/Patient"  # or a specific shape label like 'http://hl7.org/fhir/shape#PatientShape' """
    
    FHIR_PATIENT = URIRef("http://hl7.org/fhir/Patient")
    for subj in g.subjects(RDF.type, FHIR_PATIENT):
        pid = None
        
        for id_node in g.objects(subj, URIRef("http://hl7.org/fhir/Patient.identifier")):
            print(f"Procesando identificador: {id_node}")
            pid = str(g.value(id_node, URIRef("http://hl7.org/fhir/Identifier.value")))

        activo = g.value(subj, URIRef("http://hl7.org/fhir/Patient.active"))

        nombre = apellido = None
        for name_node in g.objects(subj, URIRef("http://hl7.org/fhir/Patient.name")):
            nombre  = str(g.value(name_node, URIRef("http://hl7.org/fhir/HumanName.given")))
            apellido = str(g.value(name_node, URIRef("http://hl7.org/fhir/HumanName.family")))
        raw_gender = g.value(subj, URIRef("http://hl7.org/fhir/Patient.gender"))
        genero = parse_enum(
            Genero,
            raw_gender,
            field_name="gender",
            focus=str(subj)
        )
        
        raw_estado = g.value(subj, URIRef("http://hl7.org/fhir/Patient.maritalStatus"))
        estado_civil = parse_enum(
            EstadoCivil,
            raw_estado,
            field_name="maritalStatus",
            focus=str(subj)
        )
        telefono = None
        for telecom_bn in g.objects(subj, URIRef("http://hl7.org/fhir/Patient.telecom")):
            sistema = g.value(telecom_bn, URIRef("http://hl7.org/fhir/ContactPoint.system"))
            if sistema and str(sistema).lower() == "phone":
                valor = g.value(telecom_bn, URIRef("http://hl7.org/fhir/ContactPoint.value"))
                if valor:
                    telefono = str(valor)
            break  # si solo te interesa el primero
        # Iteramos sobre cada blank node de address (aunque solo usemos la primera)
        for addr_bn in g.objects(subj, URIRef("http://hl7.org/fhir/Patient.address")):
            # línea de calle (puede ser múltiple, aquí solo la primera)
            line = g.value(addr_bn, URIRef("http://hl7.org/fhir/Address.line"))
            if line:
                calle = str(line)
            # ciudad
            city = g.value(addr_bn, URIRef("http://hl7.org/fhir/Address.city"))
            if city:
                ciudad = str(city)
            # provincia/estado
            state = g.value(addr_bn,  URIRef("http://hl7.org/fhir/Address.state"))
            if state:
                provincia = str(state)
            # código postal
            postal = g.value(addr_bn, URIRef("http://hl7.org/fhir/Address.postalCode"))
            if postal:
                codigo_postal = str(postal)
            # país
            country = g.value(addr_bn, URIRef("http://hl7.org/fhir/Address.country"))
            if country:
                pais = str(country)
            break   # si solo te interesa la primera dirección
        fecha = str(g.value(subj, URIRef("http://hl7.org/fhir/Patient.birthDate")))
        print(f"Procesando paciente: {pid}, {nombre} {apellido}, género: {genero.value}, fecha de nacimiento: {fecha} activo: {activo}, teléfono: {telefono}, dirección: {calle}, {ciudad}, {provincia}, {codigo_postal}, {pais}, estado civil: {estado_civil.value}")
        paciente = Paciente(
            id=pid,
            nombre=nombre,
            apellido=apellido,
            genero=genero.value,
            fecha_nacimiento=fecha,
            activo=bool(activo),
            telefono=telefono,
            calle=calle,
            ciudad=ciudad,
            provincia=provincia,
            codigo_postal=codigo_postal,
            pais=pais,
            estado_civil=estado_civil.value
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