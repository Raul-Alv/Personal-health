import unittest

from _support import ReadableTestCase, configure_paths

configure_paths()

from sparql.queries import (
    ALLERGY_GET_LIST_DETAILS,
    PATIENT_GET_ALL_DATA,
    PROCEDURE_GET_DETAILS,
    build_procedure_list_query,
    escape_sparql_literal,
)


class ProcedureListQueryBuilderTests(ReadableTestCase):
    suite_name = "Consultas SPARQL"

    def test_escape_sparql_literal_escapes_quotes_backslashes_and_line_breaks(self):
        """Escapado SPARQL: protege comillas, barras y saltos de linea."""
        value = 'nota "clinica" \\ final\nsegunda\r'

        escaped = escape_sparql_literal(value)

        self.assertEqual(escaped, 'nota \\"clinica\\" \\\\ final\\nsegunda\\r')

    def test_build_procedure_list_query_without_filters_targets_the_patient_reference(self):
        """Listado sin filtros: genera la consulta base del paciente."""
        query = build_procedure_list_query(patient_id="pac-1")

        self.assertIn('"Patient/pac-1"', query)
        self.assertNotIn("FILTER(", query)
        self.assertNotIn("GROUP_CONCAT", query)

    def test_build_procedure_list_query_adds_every_supported_filter(self):
        """Listado con filtros: incluye nombre, fecha, practicante y diente."""
        query = build_procedure_list_query(
            patient_id="pac-1",
            nombre=' Limpieza "Profunda" ',
            fecha="2026-05",
            practicante=" DENTISTA ",
            diente=" Molar Superior ",
        )

        self.assertEqual(query.count("FILTER("), 4)
        self.assertIn('limpieza \\"profunda\\"', query)
        self.assertIn('2026-05', query)
        self.assertIn('dentista', query)
        self.assertIn('molar superior', query)

    def test_procedure_detail_query_avoids_optional_note_aggregates(self):
        """Detalle de procedimiento: evita agregados opcionales que fallan en rdflib."""
        query = PROCEDURE_GET_DETAILS.format(procedure_uri="http://hl7.org/fhir/Procedure/proc-1")

        self.assertNotIn("GROUP_CONCAT", query)
        self.assertNotIn("?note", query)

    def test_context_queries_do_not_use_from_urn_graphs(self):
        """Consultas sobre contextos locales: no usan FROM urn porque rdflib intenta cargarlo."""
        procedure_query = build_procedure_list_query(patient_id="pac-1")
        patient_query = PATIENT_GET_ALL_DATA.format(patient_uri="http://hl7.org/fhir/Patient/pac-1")
        allergy_query = ALLERGY_GET_LIST_DETAILS.format(patient_id="pac-1")

        for query in (procedure_query, PROCEDURE_GET_DETAILS, patient_query, allergy_query):
            self.assertNotIn("FROM <urn:app_salud", query)


if __name__ == "__main__":
    unittest.main()
