from pathlib import Path
import sys
import unittest


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT_DIR / "backend"
TESTS_DIR = BACKEND_DIR / "tests"
FIXTURES_DIR = TESTS_DIR / "fixtures"
DEFAULT_SCHEMA_PATH = BACKEND_DIR / "schemas" / "fhir_r4_clinical.shex"


def configure_paths() -> None:
    backend_path = str(BACKEND_DIR)
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)


def fixture_path(*parts: str) -> Path:
    return FIXTURES_DIR.joinpath(*parts)


def read_fixture_bytes(*parts: str) -> bytes:
    return fixture_path(*parts).read_bytes()


def load_default_schema_bytes() -> bytes:
    return DEFAULT_SCHEMA_PATH.read_bytes()


class ReadableTestCase(unittest.TestCase):
    suite_name = "Tests"

    def __str__(self) -> str:
        return f"{self.suite_name}: {self._test_label()}"

    def shortDescription(self):
        return None

    def _test_label(self) -> str:
        method = getattr(self, self._testMethodName)
        if method.__doc__:
            return " ".join(method.__doc__.strip().split())

        label = self._testMethodName.removeprefix("test_").replace("_", " ")
        return label[:1].upper() + label[1:]
