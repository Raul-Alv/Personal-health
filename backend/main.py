import tempfile
from fastapi import FastAPI, UploadFile, HTTPException, File, Form
from pyshex import ShExEvaluator
from rdf_store import get_graph

app = FastAPI()
g = get_graph()

@app.post("/upload/")
async def upload_rdf_shex(rdf_file: UploadFile = File(...), shex_file: UploadFile = File(...), start_shape: str = Form(...)):
    # Save uploaded files to temp
    with tempfile.NamedTemporaryFile(suffix=".ttl", delete=False) as rdf_temp, tempfile.NamedTemporaryFile(suffix=".shex", delete=False) as shex_temp:
        rdf_bytes = await rdf_file.read()
        shex_bytes = await shex_file.read()

        rdf_temp.write(rdf_bytes)
        shex_temp.write(shex_bytes)

        rdf_path = rdf_temp.name
        shex_path = shex_temp.name

    # Load the RDF data
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
    g.commit()  # Persistimos los cambios en el grafo
    return {"status": "ok", "triples": len(g)}

@app.get("/export/")
def export_procedures(patient_id: str, system: str = "ada"):
    # stubbed
    raw_procedures = [...]  # get from cache or memory
    #exported = [validate_shex(p.code, system) for p in raw_procedures]
    return 0

@app.get("/")
def read_root():
    return {"message": "Bienvenido a tu aplicacion personal de salud!"}

@app.get("/pacientes/")
async def listar_pacientes():
    q = """
    PREFIX fhir: <http://hl7.org/fhir/>
    SELECT ?patient ?givenName ?familyName
    WHERE {
        ?patient a fhir:Patient ;
                fhir:Patient.name ?nameNode .
        ?nameNode fhir:HumanName.given ?givenName ;
                fhir:HumanName.family ?familyName .
    }
    """
    resultados = []
    for row in g.query(q):
        resultados.append({"uri": str(row.patient), "nombre": str(row.givenName), "apellido": str(row.familyName)})
    return resultados

@app.get("/procedures/")
def get_procedures():
    # stubbed
    return None

@app.get("/procedures/{procedure_id}") 
def get_procedure(procedure_id: str):
    # stubbed
    procedure = [...]