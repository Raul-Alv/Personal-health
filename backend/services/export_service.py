import io
import zipfile
from pathlib import Path

from rdflib import Graph, Namespace, URIRef

from rdf_store import get_allergy_graph, get_patient_graph, get_procedure_graph
from rdf_util import copy_subgraph
from sparql import queries

FHIR = Namespace("http://hl7.org/fhir/")
BASE_DIR = Path(__file__).resolve().parent.parent


class ExportService:
    def export_all_zip(self, patient_id: str) -> bytes:
        g_patient = get_patient_graph()
        g_procedure = get_procedure_graph()
        g_allergy = get_allergy_graph()

        patient_uri = URIRef(f"http://hl7.org/fhir/Patient/{patient_id}")
        export_graph = Graph()
        copy_subgraph(patient_uri, g_patient, export_graph)

        for row in g_procedure.query(queries.PROCEDURE_GET_BY_PATIENT.format(patient_id=patient_id)):
            copy_subgraph(row.proc, g_procedure, export_graph)

        for row in g_allergy.query(queries.ALLERGY_GET_BY_PATIENT.format(patient_id=patient_id)):
            copy_subgraph(row.alergia, g_allergy, export_graph)

        export_graph.namespace_manager.bind("fhir", FHIR, override=True)
        turtle_data = export_graph.serialize(format="turtle")
        shex_schema = (BASE_DIR / "schemas" / "exports" / "paciente_proc_schema.shex").read_text(encoding="utf-8")

        mem = io.BytesIO()
        with zipfile.ZipFile(mem, mode="w") as zf:
            zf.writestr(f"{patient_id}.ttl", turtle_data)
            zf.writestr(f"{patient_id}.shex", shex_schema)
        mem.seek(0)
        return mem.read()

    def export_selected_turtle(self, patient_id: str, tipo: str, ids: list[str], incluir_paciente: bool) -> tuple[str, str]:
        g_patient = get_patient_graph()
        g_procedure = get_procedure_graph()
        g_allergy = get_allergy_graph()

        patient_uri = URIRef(f"http://hl7.org/fhir/Patient/{patient_id}")
        export_graph = Graph()

        if incluir_paciente and (patient_uri, None, None) in g_patient:
            copy_subgraph(patient_uri, g_patient, export_graph)

        if tipo == "procedimientos":
            for item_id in ids:
                proc_uri = URIRef(f"http://hl7.org/fhir/Procedure/{item_id}")
                if (proc_uri, None, None) in g_procedure:
                    copy_subgraph(proc_uri, g_procedure, export_graph)
        elif tipo == "alergias":
            for item_id in ids:
                allergy_uri = URIRef(f"http://hl7.org/fhir/AllergyIntolerance/{item_id}")
                if (allergy_uri, None, None) in g_allergy:
                    copy_subgraph(allergy_uri, g_allergy, export_graph)
        else:
            raise ValueError("Tipo no válido (usa 'procedimientos' o 'alergias').")

        export_graph.namespace_manager.bind("fhir", FHIR, override=True)
        turtle_data = export_graph.serialize(format="turtle")
        suffix = "_con_paciente" if incluir_paciente else "_solo_items"
        filename = f"export_{tipo}_{patient_id}{suffix}.ttl"
        return turtle_data, filename
