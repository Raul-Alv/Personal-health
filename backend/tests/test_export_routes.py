import unittest
import sys
import types
from unittest.mock import patch

from _support import ReadableTestCase, configure_paths

configure_paths()

from fastapi import FastAPI
from fastapi.testclient import TestClient

fake_user_repo_module = types.ModuleType("repositories.user_repo")


class PlaceholderUserRepo:
    def has_patient_access(self, user_uri, patient_uri):
        return True


fake_user_repo_module.UserRepo = PlaceholderUserRepo
sys.modules["repositories.user_repo"] = fake_user_repo_module

fake_export_service_module = types.ModuleType("services.export_service")


class PlaceholderExportService:
    pass


fake_export_service_module.ExportService = PlaceholderExportService
sys.modules["services.export_service"] = fake_export_service_module

from api.deps import require_form_patient_access, require_patient_access
from api.routes.exports import router
from services.fhir_package_service import SchemaValidationError


def build_client() -> TestClient:
    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.dependency_overrides[require_patient_access] = lambda: (
        "http://example.org/fhir/custom#Usuario/test",
        "http://hl7.org/fhir/Patient/pac-1",
    )
    app.dependency_overrides[require_form_patient_access] = lambda: (
        "http://example.org/fhir/custom#Usuario/test",
        "http://hl7.org/fhir/Patient/pac-1",
    )
    return TestClient(app)


class ExportRouteHttpBehaviorTests(ReadableTestCase):
    suite_name = "Exportacion HTTP"

    @patch("api.routes.exports.ExportService")
    def test_export_selected_normalizes_comma_separated_ids_and_returns_a_zip(self, export_service_cls):
        """Exportacion correcta: limpia ids separados por comas y devuelve un ZIP."""
        export_service = export_service_cls.return_value
        export_service.export_selected_zip.return_value = (
            b"zip-content",
            "export_procedimientos_pac-1_solo_items.zip",
        )
        client = build_client()

        response = client.post(
            "/api/export_seleccionados",
            data={
                "patient_id": "pac-1",
                "tipo": "procedimientos",
                "ids": " proc-1, ,proc-2 ",
                "incluir_paciente": "false",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"zip-content")
        self.assertEqual(response.headers["content-type"], "application/zip")
        self.assertIn(
            "attachment; filename=export_procedimientos_pac-1_solo_items.zip",
            response.headers["content-disposition"],
        )
        export_service.export_selected_zip.assert_called_once_with(
            patient_id="pac-1",
            tipo="procedimientos",
            ids=["proc-1", "proc-2"],
            incluir_paciente=False,
        )

    @patch("api.routes.exports.ExportService")
    def test_export_selected_accepts_procedures_and_allergies_in_one_request(self, export_service_cls):
        """Exportacion mixta: permite procedimientos y alergias en el mismo ZIP."""
        export_service = export_service_cls.return_value
        export_service.export_mixed_zip.return_value = (
            b"zip-content",
            "export_seleccion_pac-1_con_paciente.zip",
        )
        client = build_client()

        response = client.post(
            "/api/export_seleccionados",
            data={
                "patient_id": "pac-1",
                "procedure_ids": " proc-1,proc-2 ",
                "allergy_ids": " al-1, ,al-2 ",
                "incluir_paciente": "true",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"zip-content")
        self.assertIn(
            "attachment; filename=export_seleccion_pac-1_con_paciente.zip",
            response.headers["content-disposition"],
        )
        export_service.export_mixed_zip.assert_called_once_with(
            patient_id="pac-1",
            procedure_ids=["proc-1", "proc-2"],
            allergy_ids=["al-1", "al-2"],
            incluir_paciente=True,
        )

    @patch("api.routes.exports.ExportService")
    def test_export_selected_returns_404_when_the_selection_has_no_exportable_items(self, export_service_cls):
        """Exportacion vacia: responde 404 cuando no hay elementos exportables."""
        export_service_cls.return_value.export_selected_zip.side_effect = ValueError(
            "No se encontraron elementos para exportar."
        )
        client = build_client()

        response = client.post(
            "/api/export_seleccionados",
            data={
                "patient_id": "pac-1",
                "tipo": "procedimientos",
                "ids": "proc-1",
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "No se encontraron elementos para exportar.")

    @patch("api.routes.exports.ExportService")
    def test_export_selected_returns_400_when_the_requested_type_is_invalid(self, export_service_cls):
        """Exportacion invalida: responde 400 si el tipo solicitado no es valido."""
        export_service_cls.return_value.export_selected_zip.side_effect = ValueError("Tipo no valido.")
        client = build_client()

        response = client.post(
            "/api/export_seleccionados",
            data={
                "patient_id": "pac-1",
                "tipo": "otro",
                "ids": "proc-1",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Tipo no valido.")

    @patch("api.routes.exports.ExportService")
    def test_export_selected_returns_422_when_schema_validation_fails(self, export_service_cls):
        """Exportacion invalida: responde 422 si falla la validacion ShEx."""
        export_service_cls.return_value.export_selected_zip.side_effect = SchemaValidationError(
            "Schema invalido",
            errors=[{"focus": "Patient/pac-1", "shape": "PatientShape", "reason": "Falta un campo"}],
        )
        client = build_client()

        response = client.post(
            "/api/export_seleccionados",
            data={
                "patient_id": "pac-1",
                "tipo": "procedimientos",
                "ids": "proc-1",
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"]["message"], "Schema invalido")
        self.assertEqual(len(response.json()["detail"]["validation_errors"]), 1)


if __name__ == "__main__":
    unittest.main()
