import io
import unittest
import zipfile

from _support import ReadableTestCase, configure_paths

configure_paths()

from rdflib import BNode, Graph, Literal, RDF, URIRef

from services.fhir_package_service import FHIR, FhirPackageService


class FhirPackageLowLevelBehaviorTests(ReadableTestCase):
    suite_name = "Paquete FHIR"

    def setUp(self):
        self.service = FhirPackageService()

    def test_normalize_patient_reference_accepts_relative_and_absolute_forms(self):
        """Normalizacion: acepta referencias de paciente relativas y absolutas."""
        self.assertEqual(
            self.service._normalize_patient_reference("Patient/pac-1"),
            "http://hl7.org/fhir/Patient/pac-1",
        )
        self.assertEqual(
            self.service._normalize_patient_reference("http://hl7.org/fhir/Patient/pac-1"),
            "http://hl7.org/fhir/Patient/pac-1",
        )
        self.assertIsNone(self.service._normalize_patient_reference("Observation/obs-1"))

    def test_validate_patient_references_accepts_matching_patient_references(self):
        """Referencias validas: acepta procedimientos enlazados a un Patient incluido."""
        graph = Graph()
        patient = URIRef("http://hl7.org/fhir/Patient/pac-1")
        procedure = URIRef("http://hl7.org/fhir/Procedure/proc-1")
        reference_node = BNode()
        reference_value = BNode()

        graph.add((patient, RDF.type, FHIR.Patient))
        graph.add((procedure, RDF.type, FHIR.Procedure))
        graph.add((procedure, FHIR["Procedure.subject"], reference_node))
        graph.add((reference_node, FHIR["Reference.reference"], reference_value))
        graph.add((reference_value, FHIR.value, Literal("Patient/pac-1")))

        errors = self.service._validate_patient_references(graph)

        self.assertEqual(errors, [])

    def test_validate_patient_references_reports_missing_patient_resources(self):
        """Referencias invalidas: detecta procedimientos cuyo Patient no viene en el paquete."""
        graph = Graph()
        procedure = URIRef("http://hl7.org/fhir/Procedure/proc-1")
        reference_node = BNode()
        reference_value = BNode()

        graph.add((procedure, RDF.type, FHIR.Procedure))
        graph.add((procedure, FHIR["Procedure.subject"], reference_node))
        graph.add((reference_node, FHIR["Reference.reference"], reference_value))
        graph.add((reference_value, FHIR.value, Literal("Patient/pac-1")))

        errors = self.service._validate_patient_references(graph)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["shape"], "ProcedureSubject")
        self.assertIn("no incluye ning", errors[0]["reason"].lower())

    def test_split_graph_by_resource_type_groups_every_resource_family(self):
        """Separacion por tipo: reparte el grafo en paciente, procedimientos y alergias."""
        graph = Graph()
        patient = URIRef("http://hl7.org/fhir/Patient/pac-1")
        procedure = URIRef("http://hl7.org/fhir/Procedure/proc-1")
        allergy = URIRef("http://hl7.org/fhir/AllergyIntolerance/al-1")

        graph.add((patient, RDF.type, FHIR.Patient))
        graph.add((patient, FHIR.value, Literal("Paciente")))
        graph.add((procedure, RDF.type, FHIR.Procedure))
        graph.add((procedure, FHIR.value, Literal("Procedimiento")))
        graph.add((allergy, RDF.type, FHIR.AllergyIntolerance))
        graph.add((allergy, FHIR.value, Literal("Alergia")))

        graphs = self.service.split_graph_by_resource_type(graph)

        self.assertEqual(
            set(graphs.keys()),
            {"paciente.ttl", "procedimientos.ttl", "alergias.ttl"},
        )
        self.assertTrue(all(len(resource_graph) > 0 for resource_graph in graphs.values()))

    def test_expand_archives_extracts_only_supported_import_files(self):
        """ZIP de importacion: solo extrae RDF y ShEx compatibles."""
        mem = io.BytesIO()
        with zipfile.ZipFile(mem, mode="w") as archive:
            archive.writestr("paciente.ttl", "@prefix fhir: <http://hl7.org/fhir/> .")
            archive.writestr("schema.shex", "start=@<PatientShape>")
            archive.writestr("notas.txt", "ignorar")

        extracted = self.service._expand_archives([("export.zip", mem.getvalue())])

        self.assertEqual(
            extracted,
            [
                ("paciente.ttl", b"@prefix fhir: <http://hl7.org/fhir/> ."),
                ("schema.shex", b"start=@<PatientShape>"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
