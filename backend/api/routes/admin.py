from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from rdflib import Graph
from rdflib.query import Result

from api.deps import get_current_user_uri
from rdf_store import ALERGIAS_GRAPH_ID, PATIENTS_GRAPH_ID, PROCEDURES_GRAPH_ID, USERS_GRAPH_ID, get_allergy_graph, get_patient_graph, get_procedure_graph, get_store, get_user_graph

router = APIRouter()


@router.post("/query/")
def ejecutar_query(sparql: str = Body(..., media_type="text/plain"), user_uri: str = Depends(get_current_user_uri)):
    store = get_store()
    try:
        stmt = sparql.strip().lower()
        if stmt.startswith(("select", "ask", "construct", "describe", "prefix")):
            resultado = store.query(sparql)
        else:
            resultado = store.update(sparql)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if isinstance(resultado, Graph):
        return Response(content=resultado.serialize(format="turtle"), media_type="text/turtle")
    if isinstance(resultado, Result):
        return Response(content=resultado.serialize(format="json"), media_type="application/sparql-results+json")
    return Response(status_code=204)


@router.delete("/graph/clear", status_code=200)
def clear_graph():
    try:
        for graph in (get_patient_graph(), get_procedure_graph(), get_user_graph(), get_allergy_graph()):
            graph.remove((None, None, None))
            graph.commit()
        return {
            "status": "ok",
            "message": "Grafo vaciado.",
            "triples_restantes": len(get_user_graph()) + len(get_patient_graph()) + len(get_procedure_graph()) + len(get_allergy_graph()),
        }
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al limpiar el grafo: {exc}") from exc


@router.get("/triples")
def list_all_triples():
    store = get_store()
    graphs = {
        "usuarios": USERS_GRAPH_ID,
        "pacientes": PATIENTS_GRAPH_ID,
        "procedimientos": PROCEDURES_GRAPH_ID,
        "alergias": ALERGIAS_GRAPH_ID,
    }
    output = []
    for name, graph_id in graphs.items():
        ctx = store.get_context(graph_id)
        for s, p, o in ctx.triples((None, None, None)):
            output.append({"grafo": name, "sujeto": str(s), "predicado": str(p), "objeto": str(o)})
    return output


@router.get("/ping")
def ping():
    return {"pong": True}
