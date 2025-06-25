from collections import defaultdict
import tempfile
from fastapi import Body, FastAPI, UploadFile, HTTPException, status, File, Form, Depends, Query, Request, Response
from fastapi.security import OAuth2PasswordBearer
from pyshex import ShExEvaluator
from rdflib import RDF, Graph, Namespace, URIRef
from rdflib.query import Result
from rdf_store import  PATIENTS_GRAPH_ID, PROCEDURES_GRAPH_ID, USERS_GRAPH_ID, get_store, get_user_graph, get_patient_graph, get_procedure_graph
from textwrap import dedent
from rdf_util import copy_subgraph, crear_token, verify_password, save_registraion
from login_funcs import hash_password, verify_password, crear_token, decodificar_token

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

store = get_store()
g_user      = get_user_graph()
g_patient   = get_patient_graph()
g_procedure = get_procedure_graph()

FHIR = Namespace("http://hl7.org/fhir/")
EX = Namespace("http://example.org/fhir/custom#")

@app.post("/upload/")
async def upload_rdf_shex(rdf_file: UploadFile = File(...), shex_file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    usuario_uri = decodificar_token(token)
    #print("Usuario URI decodificado:", usuario_uri)
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

    g_temp = Graph()
    g_temp.parse(rdf_path, format="ttl")

    # 3) Validación ShEx idéntica
    schema_str = open(shex_path, encoding="utf-8").read()
    evaluator = ShExEvaluator(rdf=g_temp, schema=schema_str)

    errores = []
    for cls, shape in [(FHIR.Patient, "PatientShape"), (FHIR.Procedure, "ProcedureShape")]:
        for subj in g_temp.subjects(RDF.type, cls):
            for r in evaluator.evaluate(start=shape, focus=str(subj)):
                if not r.result:
                    errores.append({"focus": r.focus, "shape": r.shape_label, "message": r.message})
    if errores:
        raise HTTPException(status_code=400, detail={"validation_errors": errores})
    
    # 1) Copiar pacientes completos, incluídos blank nodes
    for subj in g_temp.subjects(RDF.type, FHIR.Patient):
        copy_subgraph(subj, g_temp, g_patient)

    # 2) Copiar procedimientos completos, incluídos blank nodes
    for subj in g_temp.subjects(RDF.type, FHIR.Procedure):
        copy_subgraph(subj, g_temp, g_procedure)


    # Asociar usuario -> paciente
    paciente_uri = next(g_temp.subjects(RDF.type, FHIR.Patient), None)
    if paciente_uri:
        g_user.add((URIRef(usuario_uri), EX.tienePaciente, paciente_uri))

    # Commit
    g_user.commit()
    g_patient.commit()
    g_procedure.commit()
    store.commit()

    n_pac = sum(1 for _ in store.triples((None, None, None), context=g_patient.identifier))
    n_proc = sum(1 for _ in store.triples((None, None, None), context=g_procedure.identifier))

    return {
        "status": "ok",
        "pacientes_triples": n_pac,
        "procedimientos_triples": n_proc
    }

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
    for row in g_patient.query(q):
        resultados.append({"uri": str(row.patient), "nombre": str(row.givenName), "apellido": str(row.familyName)})
    return resultados

@app.get("/paciente")
async def get_paciente(patient_id: str = Query( ..., alias="patient_id")):
    ask_q = dedent(f"""\
        PREFIX pa: <http://hl7.org/fhir/Patient/>
        ASK {{
          pa:{patient_id} ?p ?o .
        }}
    """)
    if not g_patient.query(ask_q).askAnswer:
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
        for p, o in g_patient.query(select_q)
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
    if not g_patient.query(ask_q).askAnswer:
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
    g_patient.update(q)
    g_patient.serialize(format="ttl", destination="data/triplestore.db")
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
    if g_user.query(ask_query).askAnswer:
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
    g_user.update(insert_query)
    g_user.commit()
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
    results = list(g_user.query(query))
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
        SELECT ?patient WHERE {{ <{usuario_uri}> ex:tienePaciente ?patient . }}
    """)
    pacientes = []
    for row in g_user.query(query):
        p_uri = row.patient
        # Luego obtenemos nombre y apellido del grafo de pacientes
        name_q = dedent(f"""
            PREFIX fhir: <http://hl7.org/fhir/>
            SELECT ?given ?family WHERE {{ <{p_uri}> fhir:Patient.name ?n . ?n fhir:HumanName.given ?given ; fhir:HumanName.family ?family . }}
        """)
        info = {"id": str(p_uri).split("/")[-1]}
        for nm in g_patient.query(name_q):
            info.update({"nombre": str(nm.given), "apellido": str(nm.family)})
        pacientes.append(info)
    return pacientes

@app.get("/mis_pacientes/{patient_id}/procedimientos")
def obtener_procedimientos_paciente(patient_id: str, token: str = Depends(oauth2_scheme)):
     # 1) Decodificar y validar token
    usuario_uri = decodificar_token(token)
    if not usuario_uri:
        raise HTTPException(status_code=401, detail="Token inválido")

    # 2) URI del paciente y verificación de vínculo en grafo de usuarios
    paciente_uri = URIRef(f"http://hl7.org/fhir/Patient/{patient_id}")
    ask_link = dedent(f"""
        PREFIX ex: <http://example.org/fhir/custom#>
        ASK {{ <{usuario_uri}> ex:tienePaciente <{paciente_uri}> . }}
    """)
    if not g_user.query(ask_link).askAnswer:
        raise HTTPException(status_code=403, detail="No autorizado o sin vinculación")
    else:
        print(f"Usuario {usuario_uri} tiene acceso al paciente {paciente_uri}")
    # 3) SPARQL para obtener todos los triples de cada Procedure que apunte al paciente
    id_consulta = paciente_uri.partition("Patient/")[1] + paciente_uri.partition("Patient/")[2]
    sparql = dedent(f"""
      PREFIX fhir: <http://hl7.org/fhir/>

      SELECT 
        ?proc
        ?code
        ?text
        ?status
        ?performedDateTime
        ?performerRef
      FROM <urn:app_salud:procedimientos>
      WHERE {{
        # match sólo si el subject apunta, tras dos blank-nodes, al literal "Patient/{patient_id}"
        ?proc a fhir:Procedure ;
            fhir:Procedure.subject
                / fhir:Reference.reference
                / fhir:value
                "{id_consulta}" .

          
        ?proc fhir:Procedure.code
                / fhir:CodeableConcept.coding
                / fhir:Coding.code ?code .
        ?proc fhir:Procedure.code
                / fhir:CodeableConcept.text ?text .
          
        ?proc fhir:Procedure.status ?status .
        ?proc fhir:Procedure.performedDateTime ?performedDateTime .
        
        ?proc fhir:Procedure.performer
                / fhir:Procedure.performer.actor
                / fhir:Reference.reference
                / fhir:value
                ?performerRef .
          
      }}
      ORDER BY ?proc
    """)
    # 3) Ejecutar la consulta sobre el ConjunctiveGraph
    results = store.query(sparql)

    # 4) Formatear en JSON
    procedimientos = []
    for row in results:
        procedimientos.append({
            "procedure_uri":     str(row.proc),
            "code":              str(row.code)              if row.code              else None,
            "text":              str(row.text)              if row.text              else None,
            "status":            str(row.status)            if row.status            else None,
            "performedDateTime": str(row.performedDateTime) if row.performedDateTime else None,
            "performerRef":      str(row.performerRef)      if row.performerRef      else None,
        })

    return procedimientos


@app.post("/asociar_paciente/")
def asociar_paciente(patient_id: str = Form(...), token: str = Depends(oauth2_scheme)):
    usuario_uri = decodificar_token(token)
    if not usuario_uri:
        raise HTTPException(status_code=401, detail="Token inválido")
    paciente_uri = URIRef(f"http://hl7.org/fhir/Patient/{patient_id}")
    insert_q = f"PREFIX ex: <http://example.org/fhir/custom#> INSERT DATA {{ <{usuario_uri}> ex:tienePaciente <{paciente_uri}> . }}"
    g_user.update(insert_q)
    g_user.commit()
    return {"message": f"Paciente {patient_id} vinculado a {usuario_uri}"}

@app.post("/query/")
async def ejecutar_query(sparql: str = Body(..., media_type="text/plain"), token: str = Depends(oauth2_scheme)):
    usuario_uri = decodificar_token(token)
    if not usuario_uri:
        raise HTTPException(status_code=401, detail="Token inválido")
    try:
        stmt = sparql.strip().lower()
        if stmt.startswith(("select", "ask", "construct", "describe", "prefix")):
            resultado = store.query(sparql)
        else:
            resultado = store.update(sparql)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    if isinstance(resultado, Graph):
        return Response(content=resultado.serialize(format="turtle"), media_type="text/turtle")
    if isinstance(resultado, Result):
        return Response(content=resultado.serialize(format="json"), media_type="application/sparql-results+json")
    return Response(status_code=204)

@app.delete("/graph/clear", status_code=200)
async def clear_graph():
    try:
        # Ejecuta un SPARQL UPDATE para limpiar el grafo
        # Dependiendo del backend puede ser CLEAR DEFAULT o CLEAR GRAPH <tu-graph-uri>
        g_patient.update("CLEAR DEFAULT")
        g_patient.commit()

        g_procedure.update("CLEAR DEFAULT")
        g_procedure.commit()

        g_user.update("CLEAR DEFAULT")
        g_user.commit()
        return {
            "status": "ok",
            "message": "Grafo vaciado vía SPARQL UPDATE.",
            "triples_restantes": len(g_user) + len(g_patient) + len(g_procedure)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al limpiar el grafo: {e}"
        )
    
@app.get("/triples")
def list_all_triples():
    store = get_store()
    graphs = {
        "usuarios": USERS_GRAPH_ID,
        "pacientes": PATIENTS_GRAPH_ID,
        "procedimientos": PROCEDURES_GRAPH_ID
    }
    output = []
    for name, graph_id in graphs.items():
        ctx = store.get_context(graph_id)
        for s, p, o in ctx.triples((None, None, None)):
            output.append({
                "grafo": name,
                "sujeto": str(s),
                "predicado": str(p),
                "objeto": str(o)
            })
    return output