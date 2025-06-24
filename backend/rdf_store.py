from rdflib import ConjunctiveGraph, URIRef
import rdflib_sqlalchemy   # esto registra automáticamente el plugin "SQLAlchemy" en rdflib

# URL de tu base de datos (SQLite en este ejemplo)
DATABASE_URL = "sqlite:///data/triplestore.db"

USERS_GRAPH_ID = URIRef("urn:app_salud:usuarios")
PATIENTS_GRAPH_ID    = URIRef("urn:app_salud:pacientes")
PROCEDURES_GRAPH_ID = URIRef("urn:app_salud:procedimientos")

# Creamos/abrimos el grafo persistido
g = ConjunctiveGraph('SQLAlchemy')
g.open(DATABASE_URL, create=True)

# Creamos/abrimos el Store como ConjunctiveGraph
store = ConjunctiveGraph('SQLAlchemy')
store.open(DATABASE_URL, create=True)

def get_store() -> ConjunctiveGraph:
    """
    Devuelve el store completo (unión de todos los grafos).
    Queries sobre este grafo verán la unión de todos los contexts.
    """
    return store

def get_user_graph() -> ConjunctiveGraph:
    return store.get_context(USERS_GRAPH_ID)

def get_patient_graph() -> ConjunctiveGraph:
    return store.get_context(PATIENTS_GRAPH_ID)

def get_procedure_graph() -> ConjunctiveGraph:
    return store.get_context(PROCEDURES_GRAPH_ID)
