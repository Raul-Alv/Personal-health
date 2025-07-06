import tempfile
from fastapi import Body, FastAPI, UploadFile, HTTPException, status, File, Form, Depends, Query, Response, APIRouter
from fastapi.security import OAuth2PasswordBearer
from pyshex import ShExEvaluator
from rdflib import RDF, XSD, BNode, Graph, Literal, Namespace, URIRef, ConjunctiveGraph
from rdflib.query import Result
from rdf_store import  ALERGIAS_GRAPH_ID, PATIENTS_GRAPH_ID, PROCEDURES_GRAPH_ID, USERS_GRAPH_ID, get_allergy_graph, get_store, get_user_graph, get_patient_graph, get_procedure_graph
from textwrap import dedent
from rdf_util import copy_subgraph, crear_token, verify_password, save_registraion
from login_funcs import hash_password, verify_password, crear_token, decodificar_token
import io
import zipfile

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

store = get_store()
g_user      = get_user_graph()
g_patient   = get_patient_graph()
g_procedure = get_procedure_graph()
g_allergy  = get_allergy_graph()

FHIR = Namespace("http://hl7.org/fhir/")
EX = Namespace("http://example.org/fhir/custom#")

router = APIRouter(prefix="/api")

@router.post("/upload/")
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
    for pac in g_temp.subjects(RDF.type, FHIR.Patient):
        results = evaluator.evaluate(start="PatientShape", focus=str(pac))
        for r in results:
            if not r.result:
                errores.append({
                    "focus": str(r.focus),
                    "shape": r.start,       # en lugar de r.shape_label
                    "reason": r.reason      # en lugar de r.message
                })

    for proc in g_temp.subjects(RDF.type, FHIR.Procedure):
        results = evaluator.evaluate(start="ProcedureShape", focus=str(proc))
        for r in results:
            if not r.result:
                errores.append({
                    "focus": str(r.focus),
                    "shape": r.start,
                    "reason": r.reason
                })

    for alergia in g_temp.subjects(RDF.type, FHIR.AllergyIntolerance):
        results = evaluator.evaluate(start="AllergyIntoleranceShape", focus=str(alergia))
        for r in results:
            if not r.result:
                errores.append({
                    "focus": str(r.focus),
                    "shape": r.start,
                    "reason": r.reason
                })

    if errores:
        raise HTTPException(
            status_code=400,
            detail={"validation_errors": errores}
        )
        
    # 1) Copiar pacientes completos, incluídos blank nodes
    for subj in g_temp.subjects(RDF.type, FHIR.Patient):
        if (subj, RDF.type, FHIR.Patient) in g_patient:
            continue
        copy_subgraph(subj, g_temp, g_patient)

    # 2) Copiar procedimientos completos, incluídos blank nodes
    for subj in g_temp.subjects(RDF.type, FHIR.Procedure):
        if (subj, RDF.type, FHIR.Procedure) in g_procedure:
            continue
        copy_subgraph(subj, g_temp, g_procedure)

    # 3) Copiar alergias completas, incluídos blank nodes
    for subj in g_temp.subjects(RDF.type, FHIR.AllergyIntolerance):
        if (subj, RDF.type, FHIR.AllergyIntolerance) in g_allergy:
            continue
        copy_subgraph(subj, g_temp, g_allergy)

    # Asociar usuario -> paciente
    paciente_uri = next(g_temp.subjects(RDF.type, FHIR.Patient), None)
    if paciente_uri:
        g_user.add((URIRef(usuario_uri), EX.tienePaciente, paciente_uri))

    # Commit
    g_user.commit()
    g_patient.commit()
    g_procedure.commit()
    g_allergy.commit()
    store.commit()

    n_pac = sum(1 for _ in store.triples((None, None, None), context=g_patient.identifier))
    n_proc = sum(1 for _ in store.triples((None, None, None), context=g_procedure.identifier))

    return {
        "status": "ok",
        "pacientes_triples": n_pac,
        "procedimientos_triples": n_proc
    }

@router.get("/")
def read_root():
    return {"message": "Bienvenido a tu aplicacion personal de salud!"}

@router.get("/pacientes/")
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

@router.get("/paciente")
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

@router.delete("/pacientes/delete")
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

@router.get("/procedures/")
def get_procedures():
    # stubbed
    return None

@router.get("/procedures/{procedure_id}") 
def get_procedure(procedure_id: str):
    # stubbed
    procedure = [...]

@router.post("/registro/")
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

@router.post("/login/")
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

@router.get("/mis_pacientes/")
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

@router.get("/mis_pacientes/{patient_id}/get/procedimientos")
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
                / fhir:Coding.code 
                /fhir:value ?code .
        ?proc fhir:Procedure.code
                / fhir:CodeableConcept.text 
                / fhir:value ?text .
          
        ?proc fhir:Procedure.status 
                /fhir:value ?status .
        ?proc fhir:Procedure.performedDateTime 
                /fhir:value ?performedDateTime .
        
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

@router.get("/mis_pacientes/{patient_id}/get/alergias")
def obtener_alergias_paciente(patient_id: str, token: str = Depends(oauth2_scheme)):
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
        ?alergia
        ?display
        ?code
        ?status
        ?onsetDateTime
        ?performerRef
        ?category
      FROM <urn:app_salud:alergias>
      WHERE {{ 
        ?alergia a fhir:AllergyIntolerance ;
            fhir:AllergyIntolerance.patient
                / fhir:Reference.reference
                / fhir:value
                "{id_consulta}" .

          
        ?alergia fhir:AllergyIntolerance.code
                / fhir:CodeableConcept.coding
                / fhir:Coding.code 
                /fhir:value ?code .

        ?alergia fhir:AllergyIntolerance.code
                / fhir:CodeableConcept.coding 
                / fhir:Coding.display
                / fhir:value ?display .
          
        ?alergia fhir:AllergyIntolerance.clinicalStatus
                / fhir:CodeableConcept.coding
                / fhir:Coding.code 
                / fhir:value ?status .

        ?alergia fhir:AllergyIntolerance.onsetDateTime
                / fhir:value ?onsetDateTime . 
        
        ?alergia fhir:AllergyIntolerance.actor
                / fhir:Reference.reference
                / fhir:value ?performerRef .
        
        ?alergia fhir:AllergyIntolerance.category
                / fhir:value ?category .
          
      }}
      ORDER BY ?alergia
    """)
    # 3) Ejecutar la consulta sobre el ConjunctiveGraph
    results = store.query(sparql)
    # 4) Formatear en JSON
    alergias = []
    for row in results:
        alergias.append({
            "alergia_uri":     str(row.alergia),
            "display":         str(row.display)           if row.display           else None,
            "code":            str(row.code)              if row.code              else None,
            "status":          str(row.status)            if row.status            else None,
            "onsetDateTime":   str(row.onsetDateTime)     if row.onsetDateTime     else None,
            "performerRef":    str(row.performerRef)      if row.performerRef      else None,
            "category":        str(row.category)          if row.category          else None,
        })

    return alergias

@router.get("/export_all/{patient_id}")
def export_patient_data(patient_id: str, token: str = Depends(oauth2_scheme)):
    """
    Exporta los datos de un paciente y sus procedimientos en un ZIP: Turtle + ShEx.
    Requiere token válido y que el usuario esté vinculado al paciente.
    """
    # 1. Validar token y obtener URI de usuario
    usuario_uri = decodificar_token(token)
    if not usuario_uri:
        raise HTTPException(status_code=401, detail="Token inválido")

    # 2. Verificar vínculo usuario -> paciente con SPARQL ASK
    paciente_uri = URIRef(f"{FHIR}Patient/{patient_id}")
    ask_q = f"""
    PREFIX ex: <{EX}>
    ASK {{ <{usuario_uri}> ex:tienePaciente <{paciente_uri}> . }}
    """
    if not g_user.query(ask_q).askAnswer:
        raise HTTPException(status_code=403, detail="Acceso denegado al paciente.")

    # 3. Construir grafo de exportación con paciente
    export_graph = Graph()
    copy_subgraph(paciente_uri, g_patient, export_graph)
    #print(f"Exportando datos del paciente {patient_id}...")
    # 4. Consultar procedimientos asociados y copiar subgrafos
    proc_q = f"""
    PREFIX fhir: <{FHIR}>
    SELECT DISTINCT ?proc WHERE {{
        ?proc a fhir:Procedure ;
                fhir:Procedure.subject / fhir:Reference.reference / fhir:value "Patient/{patient_id}" .
    }}
    """
    result = g_procedure.query(proc_q)
    print(f"Procedimientos asociados al paciente {patient_id}: {len(result)} encontrados.")
    for row in result:
        print(f"Copiando procedimiento {row.proc}...")
        copy_subgraph(row.proc, g_procedure, export_graph)

    alergias_q = f"""
    PREFIX fhir: <{FHIR}>
    SELECT DISTINCT ?alergia WHERE {{
        ?alergia a fhir:AllergyIntolerance ;
            fhir:AllergyIntolerance.patient 
                / fhir:Reference.reference 
                l / fhir:value "Patient/{patient_id}" .
    }}
    """
    result = g_allergy.query(alergias_q)
    print(f"Alergias asociadas al paciente {patient_id}: {len(result)} encontradas.")
    for row in result:
        print(f"Copiando alergia {row.alergia}...")
        copy_subgraph(row.alergia, g_allergy, export_graph)

    if len(export_graph) == 0:
        raise HTTPException(status_code=404, detail="Paciente no encontrado o sin datos.")

    # 5. Serializar a Turtle
    export_graph.namespace_manager.bind("fhir", FHIR, override=True)
    turtle_data = export_graph.serialize(format="turtle")

    # 6. Cargar esquema ShEx estático
    schema_path = "schemas/exports/paciente_proc_schema.shex"
    try:
        with open(schema_path, "r", encoding="utf-8") as f:
            shex_schema = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error leyendo el esquema ShEx: {e}")

    # 7. Empaquetar en ZIP y devolver
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode="w") as zf:
        zf.writestr(f"{patient_id}.ttl", turtle_data)
        zf.writestr(f"{patient_id}.shex", shex_schema)
    mem.seek(0)

    return Response(
        content=mem.read(),
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=export_{patient_id}.zip"}
    )

@router.post("/asociar_paciente/")
def asociar_paciente(patient_id: str = Form(...), token: str = Depends(oauth2_scheme)):
    usuario_uri = decodificar_token(token)
    if not usuario_uri:
        raise HTTPException(status_code=401, detail="Token inválido")
    paciente_uri = URIRef(f"http://hl7.org/fhir/Patient/{patient_id}")
    insert_q = f"PREFIX ex: <http://example.org/fhir/custom#> INSERT DATA {{ <{usuario_uri}> ex:tienePaciente <{paciente_uri}> . }}"
    g_user.update(insert_q)
    g_user.commit()
    return {"message": f"Paciente {patient_id} vinculado a {usuario_uri}"}

@router.post("/query/")
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

@router.delete("/graph/clear", status_code=200)
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

        g_allergy.update("CLEAR DEFAULT")
        g_allergy.commit()
        
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
    
@router.get("/triples")
def list_all_triples():
    store = get_store()
    graphs = {
        "usuarios": USERS_GRAPH_ID,
        "pacientes": PATIENTS_GRAPH_ID,
        "procedimientos": PROCEDURES_GRAPH_ID,
        "alergias": ALERGIAS_GRAPH_ID
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

@router.patch("/mis_pacientes/{patient_id}/actualizar")
async def update_patient(
    patient_id: str,
    update: str = Body(...),
    token: str = Depends(oauth2_scheme)):

    usuario_uri = decodificar_token(token)
    if not usuario_uri:
        raise HTTPException(status_code=401, detail="Token inválido")
    paciente_uri = URIRef(f"http://hl7.org/fhir/Patient/{patient_id}")
    ask_link = dedent(f"""
        PREFIX ex: <http://example.org/fhir/custom#>
            ASK {{ <{usuario_uri}> ex:tienePaciente <{paciente_uri}> . }}
    """)
    if not g_user.query(ask_link).askAnswer:  
        raise HTTPException(status_code=403, detail="No autorizado o sin vinculación")
    
     # 2) Parsear fragmento de patch en grafo temporal
    g_temp = Graph()
    g_temp.parse(data=update, format="turtle")

    # 3) Para cada predicado que llegue en el patch…
    for p, o in g_temp.predicate_objects(paciente_uri):
        # 3a) Borrar cualquier valor anterior para ese predicado
        g_patient.update(f"""
            DELETE WHERE {{ <{paciente_uri}> <{p}> ?old . }}
        """)
        # 3b) Si el objeto es blank node, copiar su subgrafo
        if isinstance(o, BNode):
            # primero enlazamos el blank node al paciente
            g_patient.add((paciente_uri, p, o))
            # luego copiamos todo su subgrafo recursivamente
            copy_subgraph(o, g_temp, g_patient)
        else:
            # literal o URI: añadir directamente
            g_patient.add((paciente_uri, p, o))

    # 4) Persistir cambios
    g_patient.commit()

    return {"status": "ok", "message": f"Paciente {patient_id} parcheado correctamente."}
    
@router.get("/ping")
def ping():
    return {"pong": True}
