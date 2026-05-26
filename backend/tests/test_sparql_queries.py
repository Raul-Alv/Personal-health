import unittest

from _support import ReadableTestCase, configure_paths

configure_paths()

from sparql.queries import build_procedure_list_query, escape_sparql_literal


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


if __name__ == "__main__":
    unittest.main()
