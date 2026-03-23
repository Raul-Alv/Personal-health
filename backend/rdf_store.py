from pathlib import Path

from rdflib import ConjunctiveGraph, URIRef
import rdflib_sqlalchemy  # noqa: F401  # registra el plugin SQLAlchemy en rdflib

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DATA_DIR / 'triplestore.db'}"

USERS_GRAPH_ID = URIRef("urn:app_salud:usuarios")
PATIENTS_GRAPH_ID = URIRef("urn:app_salud:pacientes")
PROCEDURES_GRAPH_ID = URIRef("urn:app_salud:procedimientos")
ALERGIAS_GRAPH_ID = URIRef("urn:app_salud:alergias")

_store = ConjunctiveGraph("SQLAlchemy")
_store.open(DATABASE_URL, create=True)


def get_store() -> ConjunctiveGraph:
    return _store


def get_user_graph():
    return _store.get_context(USERS_GRAPH_ID)


def get_patient_graph():
    return _store.get_context(PATIENTS_GRAPH_ID)


def get_procedure_graph():
    return _store.get_context(PROCEDURES_GRAPH_ID)


def get_allergy_graph():
    return _store.get_context(ALERGIAS_GRAPH_ID)
