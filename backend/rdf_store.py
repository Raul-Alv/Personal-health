from rdflib import Graph
import rdflib_sqlalchemy   # esto registra automáticamente el plugin "SQLAlchemy" en rdflib

# URL de tu base de datos (SQLite en este ejemplo)
DATABASE_URL = "sqlite:///data/triplestore.db"
GRAPH_ID    = "urn:app_salud:grafico"

# Creamos/abrimos el grafo persistido
g = Graph('SQLAlchemy', identifier=GRAPH_ID)
g.open(DATABASE_URL, create=True)

"""
    Devuelve la instancia del grafo RDF para hacer add(), query(), commit(), etc.
"""
def get_graph() -> Graph:
    return g
