from textwrap import dedent

# ----------------------------
# Usuarios / auth
# ----------------------------
ASK_USER_EXISTS = dedent("""
    PREFIX ex: <http://example.org/fhir/custom#>
    ASK {{
        ?u a ex:Usuario ;
           ex:email "{email}" .
    }}
""")

INSERT_USER = dedent("""
    PREFIX ex: <http://example.org/fhir/custom#>
    INSERT DATA {{
        <{usuario_uri}> a ex:Usuario ;
            ex:nombre "{nombre}" ;
            ex:email "{email}" ;
            ex:hashedPassword "{hashed}" .
    }}
""")

GET_USER_BY_EMAIL = dedent("""
    PREFIX ex: <http://example.org/fhir/custom#>
    SELECT ?usuario ?hashed
    WHERE {{
        ?usuario a ex:Usuario ;
                 ex:email "{email}" ;
                 ex:hashedPassword ?hashed .
    }}
""")

GET_USER_PROFILE = dedent("""
    PREFIX ex: <http://example.org/fhir/custom#>
    SELECT ?nombre ?email WHERE {{
        <{user_uri}> a ex:Usuario ;
            ex:nombre ?nombre ;
            ex:email ?email .
    }}
""")

GET_USER_PATIENTS = dedent("""
    PREFIX ex: <http://example.org/fhir/custom#>
    SELECT ?patient WHERE {{
        <{user_uri}> ex:tienePaciente ?patient .
    }}
""")

GET_USER_FAVORITE_PATIENT = dedent("""
    PREFIX ex: <http://example.org/fhir/custom#>
    SELECT ?patient WHERE {{
        <{user_uri}> ex:pacienteFavorito ?patient .
    }}
""")

ASK_USER_HAS_PATIENT = dedent("""
    PREFIX ex: <http://example.org/fhir/custom#>
    ASK {{
        <{user_uri}> ex:tienePaciente <{patient_uri}> .
    }}
""")

LINK_USER_PATIENT = dedent("""
    PREFIX ex: <http://example.org/fhir/custom#>
    INSERT DATA {{
        <{user_uri}> ex:tienePaciente <{patient_uri}> .
    }}
""")

SET_USER_FAVORITE_PATIENT = dedent("""
    PREFIX ex: <http://example.org/fhir/custom#>
    DELETE {{
        <{user_uri}> ex:pacienteFavorito ?current .
    }}
    INSERT {{
        <{user_uri}> ex:pacienteFavorito <{patient_uri}> .
    }}
    WHERE {{
        OPTIONAL {{ <{user_uri}> ex:pacienteFavorito ?current . }}
    }}
""")

# ----------------------------
# Pacientes
# ----------------------------
GET_ALL_PATIENTS = dedent("""
    PREFIX fhir: <http://hl7.org/fhir/>
    SELECT ?patient ?givenName ?familyName
    WHERE {{
        ?patient a fhir:Patient ;
                fhir:Patient.name ?nameNode .
        ?nameNode fhir:HumanName.given ?givenName ;
                  fhir:HumanName.family ?familyName .
    }}
""")

ASK_PATIENT_EXISTS = dedent("""
    PREFIX pa: <http://hl7.org/fhir/Patient/>
    ASK {{
        pa:{patient_id} ?p ?o .
    }}
""")

GET_PATIENT_TRIPLES = dedent("""
    PREFIX pa: <http://hl7.org/fhir/Patient/>
    SELECT ?p ?o
    WHERE {{
        pa:{patient_id} ?p ?o .
    }}
""")

DELETE_PATIENT_TRIPLES = dedent("""
    PREFIX pa: <http://hl7.org/fhir/Patient/>
    DELETE WHERE {{
        pa:{patient_id} ?p ?o .
    }}
""")

GET_NAME_SURNAME = dedent("""
    PREFIX fhir: <http://hl7.org/fhir/>
    SELECT ?given ?family WHERE {{
        <{patient_uri}> fhir:Patient.name ?n .
        OPTIONAL {{ ?n fhir:HumanName.given / fhir:value ?given . }}
        OPTIONAL {{ ?n fhir:HumanName.given ?given . }}
        OPTIONAL {{ ?n fhir:HumanName.family / fhir:value ?family . }}
        OPTIONAL {{ ?n fhir:HumanName.family ?family . }}
    }}
""")

PATIENT_GET_ALL_DATA = dedent("""
    PREFIX fhir: <http://hl7.org/fhir/>
    SELECT
        ?nombre ?apellidos ?genero ?fechaNacimiento
        (COALESCE(?estado_civil_simple, ?estado_civil_codigo) AS ?estado_civil)
        ?telefono ?ss ?calle ?cp ?ciudad ?provincia ?pais
    FROM <urn:app_salud:pacientes>
    WHERE {{
        <{patient_uri}> fhir:Patient.name / fhir:HumanName.given / fhir:value ?nombre ;
                       fhir:Patient.name / fhir:HumanName.family / fhir:value ?apellidos ;
                       fhir:Patient.gender / fhir:value ?genero ;
                       fhir:Patient.birthDate / fhir:value ?fechaNacimiento .
        OPTIONAL {{ <{patient_uri}> fhir:Patient.maritalStatus / fhir:value ?estado_civil_simple . }}
        OPTIONAL {{
            <{patient_uri}> fhir:Patient.maritalStatus / fhir:CodeableConcept.coding / fhir:Coding.code / fhir:value ?estado_civil_codigo .
        }}
        OPTIONAL {{ <{patient_uri}> fhir:Patient.identifier / fhir:Identifier.value / fhir:value ?ss . }}
        OPTIONAL {{ <{patient_uri}> fhir:Patient.telecom / fhir:ContactPoint.value / fhir:value ?telefono . }}
        OPTIONAL {{ <{patient_uri}> fhir:Patient.address / fhir:Address.line / fhir:value ?calle . }}
        OPTIONAL {{ <{patient_uri}> fhir:Patient.address / fhir:Address.postalCode / fhir:value ?cp . }}
        OPTIONAL {{ <{patient_uri}> fhir:Patient.address / fhir:Address.city / fhir:value ?ciudad . }}
        OPTIONAL {{ <{patient_uri}> fhir:Patient.address / fhir:Address.state / fhir:value ?provincia . }}
        OPTIONAL {{ <{patient_uri}> fhir:Patient.address / fhir:Address.country / fhir:value ?pais . }}
    }}
""")

# ----------------------------
# Procedimientos
# ----------------------------
PROCEDURE_LIST_QUERY_TEMPLATE = dedent("""
    PREFIX fhir: <http://hl7.org/fhir/>
    SELECT DISTINCT ?proc ?code ?text ?status ?performedDateTime ?performerRef
    FROM <urn:app_salud:procedimientos>
    WHERE {{
        ?proc a fhir:Procedure ;
              fhir:Procedure.subject / fhir:Reference.reference / fhir:value "Patient/{patient_id}" .
        OPTIONAL {{ ?proc fhir:Procedure.code / fhir:CodeableConcept.coding / fhir:Coding.code / fhir:value ?code . }}
        OPTIONAL {{ ?proc fhir:Procedure.code / fhir:CodeableConcept.text / fhir:value ?text . }}
        OPTIONAL {{ ?proc fhir:Procedure.status / fhir:value ?status . }}
        OPTIONAL {{ ?proc fhir:Procedure.performedDateTime / fhir:value ?performedDateTime . }}
        OPTIONAL {{
            ?proc fhir:Procedure.performer / fhir:Procedure.performer.actor / fhir:Reference.reference / fhir:value ?performerRef .
        }}
        OPTIONAL {{
            ?proc fhir:Procedure.bodySite / fhir:CodeableConcept.coding / fhir:Coding.code / fhir:value ?dienteCode .
        }}
        OPTIONAL {{
            ?proc fhir:Procedure.bodySite / fhir:CodeableConcept.coding / fhir:Coding.display / fhir:value ?dienteDisplay .
        }}
        {extra_filters}
    }}
    ORDER BY DESC(?performedDateTime) ?proc
""")


def escape_sparql_literal(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )


def build_procedure_list_query(
    patient_id: str,
    nombre: str | None = None,
    fecha: str | None = None,
    practicante: str | None = None,
    diente: str | None = None,
) -> str:
    filters: list[str] = []

    if nombre and nombre.strip():
        nombre_escaped = escape_sparql_literal(nombre.strip().lower())
        filters.append(f'FILTER(CONTAINS(LCASE(STR(?text)), "{nombre_escaped}"))')

    if fecha and fecha.strip():
        fecha_escaped = escape_sparql_literal(fecha.strip())
        filters.append(f'FILTER(CONTAINS(STR(?performedDateTime), "{fecha_escaped}"))')

    if practicante and practicante.strip():
        practicante_escaped = escape_sparql_literal(practicante.strip().lower())
        filters.append(f'FILTER(CONTAINS(LCASE(STR(?performerRef)), "{practicante_escaped}"))')

    if diente and diente.strip():
        diente_escaped = escape_sparql_literal(diente.strip().lower())
        filters.append(
            "FILTER("
            f'CONTAINS(LCASE(STR(COALESCE(?dienteCode, ""))), "{diente_escaped}") || '
            f'CONTAINS(LCASE(STR(COALESCE(?dienteDisplay, ""))), "{diente_escaped}")'
            ")"
        )

    return PROCEDURE_LIST_QUERY_TEMPLATE.format(
        patient_id=escape_sparql_literal(patient_id),
        extra_filters="\n        ".join(filters),
    )

PROCEDURE_GET_DETAILS = dedent("""
    PREFIX fhir: <http://hl7.org/fhir/>
    SELECT ?code ?text ?status ?performedDateTime ?performerRef ?dienteCode ?dienteDisplay
    FROM <urn:app_salud:procedimientos>
    WHERE {{
        <{procedure_uri}> a fhir:Procedure .
        OPTIONAL {{ <{procedure_uri}> fhir:Procedure.code / fhir:CodeableConcept.coding / fhir:Coding.code / fhir:value ?code . }}
        OPTIONAL {{ <{procedure_uri}> fhir:Procedure.code / fhir:CodeableConcept.text / fhir:value ?text . }}
        OPTIONAL {{ <{procedure_uri}> fhir:Procedure.status / fhir:value ?status . }}
        OPTIONAL {{ <{procedure_uri}> fhir:Procedure.performedDateTime / fhir:value ?performedDateTime . }}
        OPTIONAL {{
            <{procedure_uri}> fhir:Procedure.performer / fhir:Procedure.performer.actor / fhir:Reference.reference / fhir:value ?performerRef .
        }}
        OPTIONAL {{
            <{procedure_uri}> fhir:Procedure.bodySite / fhir:CodeableConcept.coding / fhir:Coding.code / fhir:value ?dienteCode .
            OPTIONAL {{
                <{procedure_uri}> fhir:Procedure.bodySite / fhir:CodeableConcept.coding / fhir:Coding.display / fhir:value ?dienteDisplay .
            }}
        }}
    }}
""")

PROCEDURE_GET_BY_PATIENT = dedent("""
    PREFIX fhir: <http://hl7.org/fhir/>
    SELECT DISTINCT ?proc WHERE {{
        ?proc a fhir:Procedure ;
              fhir:Procedure.subject / fhir:Reference.reference / fhir:value "Patient/{patient_id}" .
    }}
""")

# ----------------------------
# Alergias
# ----------------------------
ALLERGY_GET_LIST_DETAILS = dedent("""
    PREFIX fhir: <http://hl7.org/fhir/>
    SELECT ?alergia ?display ?code ?status ?onsetDateTime ?performerRef ?category
    FROM <urn:app_salud:alergias>
    WHERE {{
        ?alergia a fhir:AllergyIntolerance ;
                 fhir:AllergyIntolerance.patient / fhir:Reference.reference / fhir:value "Patient/{patient_id}" .
        OPTIONAL {{ ?alergia fhir:AllergyIntolerance.code / fhir:CodeableConcept.coding / fhir:Coding.code / fhir:value ?code . }}
        OPTIONAL {{ ?alergia fhir:AllergyIntolerance.code / fhir:CodeableConcept.coding / fhir:Coding.display / fhir:value ?display . }}
        OPTIONAL {{
            ?alergia fhir:AllergyIntolerance.clinicalStatus / fhir:CodeableConcept.coding / fhir:Coding.code / fhir:value ?status .
        }}
        OPTIONAL {{ ?alergia fhir:AllergyIntolerance.onsetDateTime / fhir:value ?onsetDateTime . }}
        OPTIONAL {{ ?alergia fhir:AllergyIntolerance.actor / fhir:Reference.reference / fhir:value ?actorRef . }}
        OPTIONAL {{ ?alergia fhir:AllergyIntolerance.recorder / fhir:Reference.reference / fhir:value ?recorderRef . }}
        OPTIONAL {{ ?alergia fhir:AllergyIntolerance.asserter / fhir:Reference.reference / fhir:value ?asserterRef . }}
        BIND(COALESCE(?actorRef, ?recorderRef, ?asserterRef) AS ?performerRef)
        OPTIONAL {{ ?alergia fhir:AllergyIntolerance.category / fhir:value ?category . }}
    }}
    ORDER BY ?alergia
""")

ALLERGY_GET_BY_PATIENT = dedent("""
    PREFIX fhir: <http://hl7.org/fhir/>
    SELECT DISTINCT ?alergia WHERE {{
        ?alergia a fhir:AllergyIntolerance ;
                 fhir:AllergyIntolerance.patient / fhir:Reference.reference / fhir:value "Patient/{patient_id}" .
    }}
""")
