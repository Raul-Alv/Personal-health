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
        if tipo == "procedimientos":
            return self.export_mixed_zip(
                patient_id=patient_id,
                procedure_ids=ids,
                allergy_ids=[],
                incluir_paciente=incluir_paciente,
            )
        if tipo == "alergias":
            return self.export_mixed_zip(
                patient_id=patient_id,
                procedure_ids=[],
                allergy_ids=ids,
                incluir_paciente=incluir_paciente,
            )
        raise ValueError("Tipo no valido (usa 'procedimientos' o 'alergias').")

    def export_mixed_zip(
        self,
        patient_id: str,
        procedure_ids: list[str],
        allergy_ids: list[str],
        incluir_paciente: bool,
    ) -> tuple[bytes, str]:
        g_patient = get_patient_graph()
        g_procedure = get_procedure_graph()
        g_allergy = get_allergy_graph()

        patient_uri = URIRef(f"http://hl7.org/fhir/Patient/{patient_id}")
        export_graph = Graph()
        exported_items = 0

        if incluir_paciente and (patient_uri, None, None) in g_patient:
            copy_subgraph(patient_uri, g_patient, export_graph)

        exported_procedures = 0
        for item_id in procedure_ids:
            proc_uri = URIRef(f"http://hl7.org/fhir/Procedure/{item_id}")
            if (proc_uri, None, None) in g_procedure:
                copy_subgraph(proc_uri, g_procedure, export_graph)
                exported_items += 1
                exported_procedures += 1

        exported_allergies = 0
        for item_id in allergy_ids:
            allergy_uri = URIRef(f"http://hl7.org/fhir/AllergyIntolerance/{item_id}")
            if (allergy_uri, None, None) in g_allergy:
                copy_subgraph(allergy_uri, g_allergy, export_graph)
                exported_items += 1
                exported_allergies += 1

        if exported_items == 0:
            raise ValueError("No se encontraron elementos para exportar.")

        export_graph.namespace_manager.bind("fhir", FHIR, override=True)
        if exported_procedures and exported_allergies:
            export_type = "seleccion"
        elif exported_procedures:
            export_type = "procedimientos"
        else:
            export_type = "alergias"

        suffix = "_con_paciente" if incluir_paciente else "_solo_items"
        filename = f"export_{export_type}_{patient_id}{suffix}.zip"
        content = self.package_service.build_export_zip(
            graph=export_graph,
            base_filename=f"export_{export_type}_{patient_id}{suffix}",
            validate_patient_references=incluir_paciente,
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
