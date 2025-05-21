from fastapi import FastAPI, UploadFile, Form
from .rdf_util import parse_rdf_string
from .shex_validator import validate_shex
from .export_mapper import validate_shex

app = FastAPI()

@app.post("/upload/")
async def upload_rdf_shex(rdf_file: UploadFile, shex_file: UploadFile):
    rdf_path = f"/tmp/{rdf_file.filename}"
    shex_path = f"/tmp/{shex_file.filename}"

    """ with open(rdf_path, "wb") as r:
        r.write(await rdf_file.read())
    with open(shex_path, "wb") as s:
        s.write(await shex_file.read())

    result, reason = validate_shex(rdf_path, shex_path, focus="...")
    if not result:
        return {"error": "Invalid RDF", "reason": reason}

    data = parse_rdf_string(r) """
    rdf_bytes = await rdf_file.read()
    shex_bytes = await shex_file.read()

    rdf_string = rdf_bytes.decode("utf-8")
    shex_string = shex_bytes.decode("utf-8")

    data = parse_rdf_string(rdf_string)
    #shex_string = validate_shex(shex_string, focus="...")
    return data

@app.get("/export/")
def export_procedures(patient_id: str, system: str = "ada"):
    # stubbed
    raw_procedures = [...]  # get from cache or memory
    exported = [validate_shex(p.code, system) for p in raw_procedures]
    return exported

@app.get("/")
def read_root():
    return {"message": "Bienvenido a tu aplicacion personal de salud!"}