import io
import sys
import types
import unittest
import zipfile
from unittest.mock import patch

from _support import ReadableTestCase, configure_paths, load_default_schema_bytes, read_fixture_bytes

configure_paths()

from rdflib import Graph, RDF, URIRef

fake_rdf_store_module = types.ModuleType("rdf_store")
fake_rdf_store_module.get_allergy_graph = lambda: None
fake_rdf_store_module.get_patient_graph = lambda: None
fake_rdf_store_module.get_procedure_graph = lambda: None
fake_rdf_store_module.get_store = lambda: None
fake_rdf_store_module.get_user_graph = lambda: None
sys.modules["rdf_store"] = fake_rdf_store_module

fake_user_repo_module = types.ModuleType("repositories.user_repo")


class PlaceholderUserRepo:
    def set_favorite_patient(self, user_uri, patient_uri):
        return None


fake_user_repo_module.UserRepo = PlaceholderUserRepo
sys.modules["repositories.user_repo"] = fake_user_repo_module

from services.fhir_package_service import FHIR, SchemaValidationError
from services.import_service import EX, ImportService


class MemoryCommitGraph(Graph):
    def commit(self) -> None:
        return None


def load_valid_import_files() -> list[tuple[str, bytes]]:
    return [
        ("paciente.ttl", read_fixture_bytes("import_valid", "paciente.ttl")),
        ("procedimientos.ttl", read_fixture_bytes("import_valid", "procedimientos.ttl")),
        ("alergias.ttl", read_fixture_bytes("import_valid", "alergias.ttl")),
        ("fhir_r4_clinical.shex", load_default_schema_bytes()),
    ]


class RealRdfImportFlowTests(ReadableTestCase):
    suite_name = "Importacion RDF real"

    def setUp(self):
        self.service = ImportService()

    def test_preview_files_reads_a_real_fhir_package_from_disk(self):
        """Preview correcta: lee un paquete FHIR real desde ficheros TTL del repositorio."""
        preview = self.service.preview_files(load_valid_import_files())

        self.assertEqual([item["tipo"] for item in preview], ["paciente", "procedimiento", "alergia"])
        self.assertEqual(preview[0]["datos"]["http://hl7.org/fhir/Patient.active__http://hl7.org/fhir/value"], "true")
        self.assertEqual(
            preview[1]["datos"]["http://hl7.org/fhir/Procedure.code__http://hl7.org/fhir/CodeableConcept.text__http://hl7.org/fhir/value"],
            "Limpieza dental",
        )
        self.assertEqual(
            preview[2]["datos"]["http://hl7.org/fhir/AllergyIntolerance.code__http://hl7.org/fhir/CodeableConcept.text__http://hl7.org/fhir/value"],
            "Alergia a frutos secos",
        )

    @patch("services.import_service.UserRepo")
    @patch("services.import_service.get_allergy_graph")
    @patch("services.import_service.get_procedure_graph")
    @patch("services.import_service.get_patient_graph")
    @patch("services.import_service.get_user_graph")
    def test_confirm_files_imports_real_rdf_files_and_links_the_patient(
        self,
        get_user_graph,
        get_patient_graph,
        get_procedure_graph,
        get_allergy_graph,
        user_repo_cls,
    ):
        """Confirmacion correcta: importa TTL reales, guarda recursos y vincula el paciente."""
        user_graph = MemoryCommitGraph()
        patient_graph = MemoryCommitGraph()
        procedure_graph = MemoryCommitGraph()
        allergy_graph = MemoryCommitGraph()

        get_user_graph.return_value = user_graph
        get_patient_graph.return_value = patient_graph
        get_procedure_graph.return_value = procedure_graph
        get_allergy_graph.return_value = allergy_graph

        response = self.service.confirm_files(
            user_uri="http://example.org/fhir/custom#Usuario/ana",
            files=load_valid_import_files(),
            set_as_favorite=True,
        )

        patient_uri = URIRef("http://hl7.org/fhir/Patient/pac-001")
        procedure_uri = URIRef("http://hl7.org/fhir/Procedure/proc-001")
        allergy_uri = URIRef("http://hl7.org/fhir/AllergyIntolerance/al-001")

        self.assertEqual(response, {"redirect": "/paciente/pac-001"})
        self.assertIn((patient_uri, RDF.type, FHIR.Patient), patient_graph)
        self.assertIn((procedure_uri, RDF.type, FHIR.Procedure), procedure_graph)
        self.assertIn((allergy_uri, RDF.type, FHIR.AllergyIntolerance), allergy_graph)
        self.assertIn((URIRef("http://example.org/fhir/custom#Usuario/ana"), EX.tienePaciente, patient_uri), user_graph)
        user_repo_cls.return_value.set_favorite_patient.assert_called_once_with(
            "http://example.org/fhir/custom#Usuario/ana",
            "http://hl7.org/fhir/Patient/pac-001",
        )

    def test_preview_files_accepts_a_real_zip_export_with_multiple_rdf_files(self):
        """Preview desde ZIP: acepta una exportacion real con varios RDF y un ShEx."""
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, mode="w") as archive:
            for filename, content in load_valid_import_files():
                archive.writestr(filename, content)
            archive.writestr("notas.txt", "ignorar")

        preview = self.service.preview_files([("export_valid.zip", zip_buffer.getvalue())])

        self.assertEqual(len(preview), 3)
        self.assertEqual({item["tipo"] for item in preview}, {"paciente", "procedimiento", "alergia"})

    def test_preview_files_reports_real_reference_errors_when_the_patient_file_is_missing(self):
        """Preview invalida: detecta referencias a Patient cuando falta el fichero del paciente."""
        files = [
            ("procedimientos.ttl", read_fixture_bytes("import_invalid", "procedimiento_paciente_inexistente.ttl")),
            ("fhir_r4_clinical.shex", load_default_schema_bytes()),
        ]

        with self.assertRaises(SchemaValidationError) as ctx:
            self.service.preview_files(files)

        self.assertEqual(
            ctx.exception.message,
            "La previsualizaci\u00f3n ha detectado errores de validaci\u00f3n RDF/ShEx.",
        )
        self.assertTrue(
            any("ning\u00fan recurso Patient" in error["reason"] for error in ctx.exception.errors),
            ctx.exception.errors,
        )


if __name__ == "__main__":
    unittest.main()
