from textwrap import dedent

FHIR = "http://hl7.org/fhir/"
EX = "http://example.org/fhir/custom#"

FHIR_PATIENT = FHIR + "Patient/"
FHIR_PROCEDURE = FHIR + "Procedure/"
FHIR_ALLERGY = FHIR + "AllergyIntolerance/"

def format_query(query_template: str, **params) -> str:
    return query_template.format(**params)



# ------ AUTH -------
ASK_USER_EXISTS = dedent("""
    PREFIX ex: <http://example.org/fhir/custom#>
    ASK {
        ?u a ex:Usuario ;
            ex:email "{email}" .
    }
""")

ASK_USER_HAS_PATIENT = dedent("""
    PREFIX ex: <http://example.org/fhir/custom#>
    ASK { <{usuario_uri}> ex:tienePaciente <{paciente_uri}> . }
""")

INSERT_USER = dedent("""
    PREFIX ex: <http://example.org/fhir/custom#>
    INSERT DATA {
        <{usuario_uri}> a ex:Usuario ;
            ex:nombre "{nombre}" ;
            ex:email "{email}" ;
            ex:hashedPassword "{hashed}" .
    }
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
    SELECT ?nombre ?email WHERE {
        <{user_uri}> a ex:Usuario ;
            ex:nombre ?nombre ;
            ex:email ?email .
    }
""")

GET_USER_PATIENTS = dedent("""
    PREFIX ex: <http://example.org/fhir/custom#>
    SELECT ?patient WHERE {
        <{user_uri}> ex:tienePaciente ?patient .
    }
""")

ASK_USER_HAS_PATIENT = dedent("""
    PREFIX ex: <http://example.org/fhir/custom#>
    ASK {
        <{user_uri}> ex:tienePaciente <{patient_uri}> .
    }
""")

LINK_USER_PATIENT = dedent("""
    PREFIX ex: <http://example.org/fhir/custom#>
    INSERT DATA {
        <{user_uri}> ex:tienePaciente <{patient_uri}> .
    }
""")

# ------- GPATIENT DATA -------
GET_ALL_PATIENTS = dedent("""
    PREFIX fhir: <http://hl7.org/fhir/>
    SELECT ?patient ?givenName ?familyName
    WHERE {
        ?patient a fhir:Patient ;
                fhir:Patient.name ?nameNode .
        ?nameNode fhir:HumanName.given ?givenName ;
                fhir:HumanName.family ?familyName .
    }
""")

ASK_PATIENT_EXISTS = dedent("""
    PREFIX pa: <http://hl7.org/fhir/Patient/>
    ASK {
        pa:{patient_id} ?p ?o .
    }
""")

GET_PATIENT = dedent("""
    PREFIX pa: <http://hl7.org/fhir/Patient/>
    SELECT ?p ?o
    WHERE {{
        pa:<{patient_id}> ?p ?o .
    }}
""")

DELETE_PATIENT = dedent("""
    PREFIX pa: <http://hl7.org/fhir/Patient/>
    DELETE WHERE {{
    pa:<{patient_id}> ?p ?o .
    }}
""")

GET_USER_PATIENTS = dedent("""
    PREFIX ex: <http://example.org/fhir/custom#>
    SELECT ?patient WHERE {{ <{usuario_uri}> ex:tienePaciente ?patient . }}
""")

GET_NAME_SUERNAME = dedent("""
    PREFIX fhir: <http://hl7.org/fhir/>
    SELECT ?given ?family WHERE {{
        <{patient_uri}> fhir:Patient.name ?n . 
        ?n fhir:HumanName.given ?given ; 
            fhir:HumanName.family ?family . 
    }}
""")

PATIENT_GET_ALL_DATA = dedent("""
    PREFIX fhir: <http://hl7.org/fhir/>
    SELECT
        ?nombre 
        ?apellidos
        ?genero
        ?fechaNacimiento
        ?estado_civil
        ?telefono
        ?ss
        ?calle
        ?cp
        ?ciudad
        ?provincia
        ?pais
    FROM <urn:app_salud:pacientes>
    WHERE {{
        <{paciente_uri}> fhir:Patient.name
                / fhir:HumanName.given
                / fhir:value ?nombre ;

            fhir:Patient.name
                / fhir:HumanName.family
                / fhir:value ?apellidos ;

            fhir:Patient.gender
                / fhir:value ?genero ;
            
            fhir:Patient.birthDate
                / fhir:value ?fechaNacimiento ;

            fhir:Patient.maritalStatus
                / fhir:value ?estado_civil ;
            
            fhir:Patient.identifier
                / fhir:Identifier.value
                / fhir:value ?ss ;
            
            fhir:Patient.telecom
                / fhir:ContactPoint.value
                / fhir:value ?telefono ;
            
            fhir:Patient.address
                / fhir:Address.line
                / fhir:value ?calle ;
                              
            fhir:Patient.address
                / fhir:Address.postalCode
                / fhir:value ?cp ;
                              
            fhir:Patient.address
                / fhir:Address.city
                / fhir:value ?ciudad ;
                              
            fhir:Patient.address
                / fhir:Address.state
                / fhir:value ?provincia ;
                              
            fhir:Patient.address
                / fhir:Address.country
                / fhir:value ?pais .
    }}
""")

# -------- PROCEDURES -------
PROCEDURE_GET_PATIENT_PROCEDURES = dedent("""
    PREFIX fhir: <{FHIR}>
    SELECT DISTINCT ?proc WHERE {{
        ?proc a fhir:Procedure ;
                fhir:Procedure.subject / fhir:Reference.reference / fhir:value "Patient/{patient_id}" .
    }
""")

PROCEDURE_GET_LIST_DETAILS = dedent("""
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

PROCEDURE_GET_DETAILS = dedent("""
    PREFIX fhir: <http://hl7.org/fhir/>
    SELECT
        ?code
        ?text
        ?status
        ?performedDateTime
        ?performerRef
        ?dienteCode
        ?dienteDisplay
    FROM <urn:app_salud:procedimientos>
    WHERE {{
        <{procedure_uri}> fhir:Procedure.code
                / fhir:CodeableConcept.coding
                / fhir:Coding.code
                / fhir:value ?code ;
                               
            fhir:Procedure.code
                / fhir:CodeableConcept.text
                / fhir:value ?text ;
                               
            fhir:Procedure.status
                / fhir:value ?status ;
                               
            fhir:Procedure.performedDateTime
                / fhir:value ?performedDateTime ;
                               
            fhir:Procedure.performer
                / fhir:Procedure.performer.actor
                / fhir:Reference.reference
                / fhir:value ?performerRef ;
                               
            OPTIONAL {{
                <{procedure_uri}> fhir:Procedure.bodySite
                    / fhir:CodeableConcept.coding
                    / fhir:Coding.code
                    / fhir:value ?dienteCode ;
                               
                fhir:Procedure.bodySite
                    / fhir:CodeableConcept.coding
                    / fhir:Coding.display
                    / fhir:value ?dienteDisplay .
            }}
    }}
""")   

# -------- ALERGIAS -------
ALLERGY_GET_PATIENT_ALLERGIES = dedent("""
    PREFIX fhir: <{FHIR}>
    SELECT DISTINCT ?alergia WHERE {{
        ?alergia a fhir:AllergyIntolerance ;
            fhir:AllergyIntolerance.patient 
                / fhir:Reference.reference 
                l / fhir:value "Patient/{patient_id}" .
    }}
""")

ALLERGY_GET_LIST_DETAILS = dedent("""
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

# -------- LOGIN -------
REGISTER_USER = dedent("""
   PREFIX ex: <http://example.org/fhir/custom#>
    INSERT DATA {{
        <{usuario_uri}> a ex:Usuario ;
            ex:nombre "{nombre}" ;
            ex:email "{email}" ;
            ex:hashedPassword "{hashed}" .
    }}
""")

LOGIN_USER = dedent("""
PREFIX ex: <http://example.org/fhir/custom#>
    SELECT ?usuario ?hashed
    WHERE {{
        ?usuario a ex:Usuario ;
                    ex:email "{email}" ;
                    ex:hashedPassword ?hashed .
    }}
""")

