import unittest
import sys
import types
from unittest.mock import patch

from _support import ReadableTestCase, configure_paths

configure_paths()

from fastapi import HTTPException

fake_user_repo_module = types.ModuleType("repositories.user_repo")


class PlaceholderUserRepo:
    pass


fake_user_repo_module.UserRepo = PlaceholderUserRepo
sys.modules["repositories.user_repo"] = fake_user_repo_module

from services.auth_service import AuthService


class RegisterAndLoginFlowTests(ReadableTestCase):
    suite_name = "Autenticacion"

    @patch("services.auth_service.crear_token", return_value="jwt-token")
    @patch("services.auth_service.hash_password", return_value="hashed-secret")
    @patch("services.auth_service.UserRepo")
    def test_register_creates_the_user_and_returns_a_bearer_token(self, user_repo_cls, hash_password, crear_token):
        """Registro correcto: crea el usuario y devuelve un bearer token."""
        user_repo = user_repo_cls.return_value
        user_repo.exists_by_email.return_value = False

        result = AuthService().register(
            email="ana@example.com",
            password="secret123",
            nombre="Ana",
        )

        user_repo.exists_by_email.assert_called_once_with("ana@example.com")
        hash_password.assert_called_once_with("secret123")
        user_repo.create_user.assert_called_once_with(
            "http://example.org/fhir/custom#Usuario/ana",
            "Ana",
            "ana@example.com",
            "hashed-secret",
        )
        crear_token.assert_called_once_with("http://example.org/fhir/custom#Usuario/ana")
        self.assertEqual(result, {"access_token": "jwt-token", "token_type": "bearer"})

    @patch("services.auth_service.UserRepo")
    def test_register_rejects_an_email_that_is_already_registered(self, user_repo_cls):
        """Registro duplicado: rechaza un email ya existente."""
        user_repo_cls.return_value.exists_by_email.return_value = True

        with self.assertRaises(HTTPException) as ctx:
            AuthService().register(email="ana@example.com", password="secret123", nombre="Ana")

        self.assertEqual(ctx.exception.status_code, 400)

    @patch("services.auth_service.UserRepo")
    def test_login_rejects_unknown_users(self, user_repo_cls):
        """Login invalido: rechaza usuarios que no existen."""
        user_repo_cls.return_value.get_by_email.return_value = None

        with self.assertRaises(HTTPException) as ctx:
            AuthService().login(email="ana@example.com", password="secret123")

        self.assertEqual(ctx.exception.status_code, 401)

    @patch("services.auth_service.verify_password", return_value=False)
    @patch("services.auth_service.UserRepo")
    def test_login_rejects_incorrect_passwords(self, user_repo_cls, verify_password):
        """Login invalido: rechaza una contrasena incorrecta."""
        user_repo_cls.return_value.get_by_email.return_value = (
            "http://example.org/fhir/custom#Usuario/ana",
            "hashed-secret",
        )

        with self.assertRaises(HTTPException) as ctx:
            AuthService().login(email="ana@example.com", password="incorrecta")

        verify_password.assert_called_once_with("incorrecta", "hashed-secret")
        self.assertEqual(ctx.exception.status_code, 401)

    @patch("services.auth_service.crear_token", return_value="jwt-token")
    @patch("services.auth_service.verify_password", return_value=True)
    @patch("services.auth_service.UserRepo")
    def test_login_returns_a_token_when_credentials_are_valid(self, user_repo_cls, verify_password, crear_token):
        """Login correcto: devuelve un token cuando las credenciales son validas."""
        user_repo_cls.return_value.get_by_email.return_value = (
            "http://example.org/fhir/custom#Usuario/ana",
            "hashed-secret",
        )

        result = AuthService().login(email="ana@example.com", password="secret123")

        verify_password.assert_called_once_with("secret123", "hashed-secret")
        crear_token.assert_called_once_with("http://example.org/fhir/custom#Usuario/ana")
        self.assertEqual(result, {"access_token": "jwt-token", "token_type": "bearer"})


if __name__ == "__main__":
    unittest.main()
