from rdflib import Graph, Namespace, URIRef

from rdf_store import get_allergy_graph, get_patient_graph, get_procedure_graph
from rdf_util import copy_subgraph
from services.fhir_package_service import FhirPackageService
from sparql import queries

FHIR = Namespace("http://hl7.org/fhir/")


class ExportService:
    def __init__(self) -> None:
        self.package_service = FhirPackageService()

    def export_all_zip(self, patient_id: str) -> bytes:
        export_graph = self._build_export_graph(patient_id=patient_id)
        return self.package_service.build_export_zip(graph=export_graph, base_filename=f"export_{patient_id}")

    def export_selected_zip(self, patient_id: str, tipo: str, ids: list[str], incluir_paciente: bool) -> tuple[bytes, str]:
        g_patient = get_patient_graph()
        g_procedure = get_procedure_graph()
        g_allergy = get_allergy_graph()

        patient_uri = URIRef(f"http://hl7.org/fhir/Patient/{patient_id}")
        export_graph = Graph()
        exported_items = 0

        if incluir_paciente and (patient_uri, None, None) in g_patient:
            copy_subgraph(patient_uri, g_patient, export_graph)

        if tipo == "procedimientos":
            for item_id in ids:
                proc_uri = URIRef(f"http://hl7.org/fhir/Procedure/{item_id}")
                if (proc_uri, None, None) in g_procedure:
                    copy_subgraph(proc_uri, g_procedure, export_graph)
                    exported_items += 1
        elif tipo == "alergias":
            for item_id in ids:
                allergy_uri = URIRef(f"http://hl7.org/fhir/AllergyIntolerance/{item_id}")
                if (allergy_uri, None, None) in g_allergy:
                    copy_subgraph(allergy_uri, g_allergy, export_graph)
                    exported_items += 1
        else:
            raise ValueError("Tipo no valido (usa 'procedimientos' o 'alergias').")

        if exported_items == 0:
            raise ValueError("No se encontraron elementos para exportar.")

        export_graph.namespace_manager.bind("fhir", FHIR, override=True)
        suffix = "_con_paciente" if incluir_paciente else "_solo_items"
        filename = f"export_{tipo}_{patient_id}{suffix}.zip"
        content = self.package_service.build_export_zip(
            graph=export_graph,
            base_filename=f"export_{tipo}_{patient_id}{suffix}",
        )
        return content, filename

    @staticmethod
    def _build_export_graph(patient_id: str) -> Graph:
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
        return export_graph
