import tempfile
from fastapi import Body, FastAPI, UploadFile, HTTPException, status, File, Form, Depends, Query, Request, Response
from fastapi.security import OAuth2PasswordBearer
from pyshex import ShExEvaluator
from rdflib import RDF, Graph, Namespace
from rdflib.query import Result
from rdf_store import get_graph
from textwrap import dedent
from rdf_util import crear_token, verify_password, save_registraion
from login_funcs import hash_password, verify_password, crear_token, decodificar_token

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
g = get_graph()
FHIR = Namespace("http://hl7.org/fhir/")
EX = Namespace("http://example.org/fhir/custom#")

@app.post("/upload/")
async def upload_rdf_shex(rdf_file: UploadFile = File(...), shex_file: UploadFile = File(...), start_shape: str = Form(...), token: str = Depends(oauth2_scheme)):
    usuario_uri = decodificar_token(token)
    print("Usuario URI decodificado:", usuario_uri)
    if not usuario_uri:
        raise HTTPException(status_code=401, detail="Token inválido")
    # Save uploaded files to temp
    with tempfile.NamedTemporaryFile(suffix=".ttl", delete=False) as rdf_temp, tempfile.NamedTemporaryFile(suffix=".shex", delete=False) as shex_temp:
        rdf_bytes = await rdf_file.read()
        shex_bytes = await shex_file.read()

        rdf_temp.write(rdf_bytes)
        shex_temp.write(shex_bytes)

        rdf_path = rdf_temp.name
        shex_path = shex_temp.name

    # Load the RDF data
    g_temp = Graph()
    g_temp.parse(rdf_path, format="ttl")

    errores = []

    # Decode the ShEx schema from the file
    schema_str = open(shex_path, "r", encoding="utf-8").read()
    evaluator = ShExEvaluator(rdf=g_temp, schema=schema_str)

    for pac in g_temp.subjects(RDF.type, FHIR.Patient):
        results = evaluator.evaluate(start="PatientShape", focus=str(pac))
        for r in results:
            if not r.result:
                errores.append(r)
    
    for proc in g_temp.subjects(RDF.type, FHIR.Procedure):
        results = evaluator.evaluate(start="ProcedureShape", focus=str(proc))
        for r in results:
            if not r.result:
                errores.append(r)
    
    # Recolectamos todos los fallos en detalle
    
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
    paciente_uri = next(g_temp.subjects(RDF.type, FHIR.Patient))
    patient_triples = []
    for s, p, o in g_temp.triples((paciente_uri, None, None)):
        patient_triples.append(f"{s.n3()} {p.n3()} {o.n3()} .")
    nt_patient = "\n".join(patient_triples)
    print("Patient triples:", nt_patient)
    insert_patient = f"""
        PREFIX fhir: <{FHIR}>
        INSERT DATA {{
            {nt_patient}
        }}
    """
    g.update(insert_patient)


    proc_triples = []
    for proc_uri in g_temp.subjects(RDF.type, FHIR.Procedure):
        for s, p, o in g_temp.triples((proc_uri, None, None)):
            proc_triples.append(f"{s.n3()} {p.n3()} {o.n3()} .")
    nt_procs = "\n".join(proc_triples)

    insert_procs = f"""
        PREFIX fhir: <{FHIR}>
        INSERT DATA {{
            {nt_procs}
        }}
        """
    g.update(insert_procs)

    
    insert_link = f"""
        PREFIX ex: <{EX}>
        INSERT DATA {{
            <{usuario_uri}> ex:tienePaciente <{paciente_uri}> .
        }}
    """
    g.update(insert_link)

    # ✅ Unir el RDF subido al grafo persistente
    for triple in g_temp:
        g.add(triple)

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

@app.get("/paciente")
async def get_paciente(patient_id: str = Query( ..., alias="patient_id",
                                                   title="ID del paciente",
                                                   description="ID del paciente a eliminar")):
    # Verificamos que el paciente existe
    # 1) Verifica que exista ese sujeto
    ask_q = dedent(f"""\
        PREFIX pa: <http://hl7.org/fhir/Patient/>
        ASK {{
          pa:{patient_id} ?p ?o .
        }}
    """)
    if not g.query(ask_q).askAnswer:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    select_q = dedent(f"""\
        PREFIX pa: <http://hl7.org/fhir/Patient/>
        SELECT ?p ?o
        WHERE {{
            pa:{patient_id} ?p ?o .
        }}
    """)
    resultados = [
        {"predicado": str(p), "objeto": str(o)}
        for p, o in g.query(select_q)
    ]
    return {"id": patient_id, "tripletas": resultados}

@app.delete("/pacientes/delete")
async def eliminar_paciente(patient_id: str = Query(
        ..., 
        alias="patient_id", 
        title="ID del paciente",
        description="UUID o identificador del paciente a eliminar"
    )):
    # 1) Verificamos que exista al menos un paciente con ese identifier
    ask_q = dedent(f"""\
        PREFIX pa: <http://hl7.org/fhir/Patient/>
        ASK {{
            pa:{patient_id} ?p ?o.
        }}
    """)
    if not g.query(ask_q).askAnswer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ningún paciente con ID {patient_id}"
        )

    # 2) SPARQL UPDATE: borrado explícito en dos fases (DELETE{…} WHERE{…})
    q = dedent(f"""
        PREFIX pa: <http://hl7.org/fhir/Patient/>
        DELETE WHERE {{
        pa:{patient_id} ?p ?o .
        }}
    """)
    g.update(q)
    g.serialize(format="ttl", destination="data/triplestore.db")
    return {"status": "ok", "message": f"Paciente {patient_id} eliminado."}

@app.get("/procedures/")
def get_procedures():
    # stubbed
    return None

@app.get("/procedures/{procedure_id}") 
def get_procedure(procedure_id: str):
    # stubbed
    procedure = [...]

@app.post("/registro/")
def registrar_usuario(email: str = Form(...), password: str = Form(...), nombre: str = Form(...)):
    usuario_id = email.split("@")[0]
    usuario_uri = f"http://example.org/fhir/custom#Usuario/{usuario_id}"

    # Verifica si ya existe con ASK
    ask_query = dedent(f"""
        PREFIX ex: <http://example.org/fhir/custom#>
        ASK {{
            ?u a ex:Usuario ;
               ex:email "{email}" .
        }}
    """)
    if g.query(ask_query).askAnswer:
        raise HTTPException(status_code=400, detail="Usuario ya registrado")

    # Si no existe, lo insertamos
    hashed = hash_password(password)
    insert_query = dedent(f"""
        PREFIX ex: <http://example.org/fhir/custom#>
        INSERT DATA {{
            <{usuario_uri}> a ex:Usuario ;
                ex:nombre "{nombre}" ;
                ex:email "{email}" ;
                ex:hashedPassword "{hashed}" .
        }}
    """)
    g.update(insert_query)
    g.commit()
    return {"message": "Usuario registrado correctamente"}

@app.post("/login/")
def login_usuario(email: str = Form(...), password: str = Form(...)):
    query = dedent(f"""
        PREFIX ex: <http://example.org/fhir/custom#>
        SELECT ?usuario ?hashed
        WHERE {{
            ?usuario a ex:Usuario ;
                     ex:email "{email}" ;
                     ex:hashedPassword ?hashed .
        }}
    """)
    results = list(g.query(query))
    if not results:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    usuario_uri, stored_hashed = results[0]
    if not verify_password(password, str(stored_hashed)):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    token = crear_token(str(usuario_uri))
    return {"access_token": token, "token_type": "bearer"}



@app.get("/mis_pacientes/")
def obtener_mis_pacientes(token: str = Depends(oauth2_scheme)):
    usuario_uri = decodificar_token(token)
    if not usuario_uri:
        raise HTTPException(status_code=401, detail="Token inválido")
    print("Usuario URI decodificado:", usuario_uri)
    query = dedent(f"""
        PREFIX ex: <http://example.org/fhir/custom#>
        PREFIX fhir: <http://hl7.org/fhir/>
        SELECT ?paciente ?nombre ?apellido
        WHERE {{
            <{usuario_uri}> ex:tienePaciente ?paciente .
            ?paciente fhir:HumanName.given ?nombre ;
                      fhir:HumanName.family ?apellido .
        }}
    """)

    resultados = []
    for row in g.query(query):
        resultados.append({
            "id": row.paciente.split("/")[-1],
            "nombre": str(row.nombre),
            "apellido": str(row.apellido)
        })
    return resultados

@app.get("/mis_pacientes/{patient_id}/procedimientos")
def obtener_procedimientos_paciente(patient_id: str, token: str = Depends(oauth2_scheme)):
    usuario_uri = decodificar_token(token)
    if not usuario_uri:
        raise HTTPException(status_code=401, detail="Token inválido")
    paciente_uri = f"http://hl7.org/fhir/Patient/{patient_id}" 
    print("Paciente URI:", paciente_uri)
    print("Usuario URI:", usuario_uri)
    print("Patient ID:", patient_id)
    query = dedent(f"""
        PREFIX ex:   <http://example.org/fhir/custom#>
        PREFIX fhir: <http://hl7.org/fhir/>
        PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>

        SELECT 
        ?patient
        ?code 
        ?performedDateTime 
        ?performerURI 
        ?status 
        ?patientID

        WHERE {{
            <{usuario_uri}> ex:tienePaciente ?patient .
            ?proc a                            fhir:Procedure ;
                fhir:Procedure.code         ?cc ;
                fhir:Procedure.performedDateTime ?performedDateTime ;
                fhir:Procedure.status       ?status ;
                fhir:Procedure.performer      ?perfNode .


            ?coding fhir:CodeableConcept.coding ?cd ;
                fhir:CodeableConcept.text ?text .
            ?cd fhir:Coding.code ?code;
                fhir:Coding.system ?system .

            ?perfNode fhir:Procedure.performer.actor  ?actorNode .
            ?actorNode fhir:Reference.reference       ?refNode .
            ?refNode  fhir:value                      ?performerValue . 
        }}

        ORDER BY ?patient ?performedDateTime
    """)
    resultados = []
    for row in g.query(query):
        resultados.append({
            "patient": str(row.patient),
            "code": str(row.code),
            "performedDateTime": str(row.performedDateTime),
            "performerURI": str(row.performerURI),
            "status": str(row.status),
            "patientID": str(row.patientID)
        })
    return resultados

@app.post("/asociar_paciente/")
def asociar_paciente(patient_id: str = Form(...), token: str = Depends(oauth2_scheme)):
    usuario_uri = decodificar_token(token)
    if not usuario_uri:
        raise HTTPException(status_code=401, detail="Token inválido")

    paciente_uri = f"http://hl7.org/fhir/Patient/{patient_id}"

    insert = f"""
        PREFIX ex: <http://example.org/fhir/custom#>
        PREFIX fhir: <http://hl7.org/fhir/>
        INSERT DATA {{
            <{usuario_uri}> ex:tienePaciente <{paciente_uri}> .
        }}
    """
    g.update(insert)
    g.commit()
    return {"message": f"Paciente {patient_id} vinculado a {usuario_uri}"}

@app.post("/query/")
async def ejecutar_query(sparql: str = Body(..., media_type="text/plain"), token: str = Depends(oauth2_scheme)):
    # 1) Autorización
    usuario_uri = decodificar_token(token)
    if not usuario_uri:
        raise HTTPException(status_code=401, detail="Token inválido")

    # 2) Ejecutamos la query
    try:
        resultado = g.query(sparql)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 3) Si es un Graph (CONSTRUCT o DESCRIBE)
    if isinstance(resultado, Graph):
        turtle = resultado.serialize(format="turtle")
        return Response(content=turtle, media_type="text/turtle")

    # 4) Si es un Result (SELECT o ASK)
    if isinstance(resultado, Result):
        # RDFlib usa `.vars` no `.labels`
        # Y tiene un serializador para SPARQL-JSON tras forzar la importación:
        import rdflib.plugins.sparql.results.jsonresults
        sparql_json = resultado.serialize(format="json")
        return Response(content=sparql_json, media_type="application/sparql-results+json")

    # 5) Fallback: no debería llegar aquí
    return Response(status_code=204)

@app.delete("/graph/clear", status_code=200)
async def clear_graph():
    try:
        # Ejecuta un SPARQL UPDATE para limpiar el grafo
        # Dependiendo del backend puede ser CLEAR DEFAULT o CLEAR GRAPH <tu-graph-uri>
        g.update("CLEAR DEFAULT")
        g.commit()
        return {
            "status": "ok",
            "message": "Grafo vaciado vía SPARQL UPDATE.",
            "triples_restantes": len(g)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al limpiar el grafo: {e}"
        )