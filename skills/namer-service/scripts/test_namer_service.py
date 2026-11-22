import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
import urllib.error

spec = importlib.util.spec_from_file_location("service", Path(__file__).with_name("namer_service.py"))
service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(service)


class ServiceTests(unittest.TestCase):
    @patch.object(service.shutil, "which", return_value=None)
    def test_missing_install_only_suggests(self, which):
        with self.assertRaisesRegex(RuntimeError, "brew install ollama"):
            service.prepare()

    @patch.object(service.subprocess, "run")
    @patch.object(service, "models", return_value={service.MODEL})
    @patch.object(service.shutil, "which", return_value="/bin/ollama")
    def test_ready_service_does_not_restart_or_pull(self, which, models, run):
        service.prepare()
        run.assert_not_called()

    @patch.object(service.subprocess, "run")
    @patch.object(service, "models", side_effect=[set(), {service.MODEL}])
    @patch.object(service.shutil, "which", return_value="/bin/ollama")
    def test_missing_model_pulls_only(self, which, models, run):
        service.prepare()
        run.assert_called_once_with(["ollama", "pull", service.MODEL], check=True, timeout=1200)

    @patch.object(service.subprocess, "run")
    @patch.object(service, "models", side_effect=urllib.error.URLError(PermissionError("denied")))
    @patch.object(service.shutil, "which", return_value="/bin/ollama")
    def test_permission_failure_does_not_start_service(self, which, models, run):
        with self.assertRaisesRegex(RuntimeError, "Permission denied"):
            service.prepare()
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
