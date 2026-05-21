import unittest
from unittest.mock import patch, MagicMock, call, mock_open
import subprocess
import sys
import importlib.metadata
from pathlib import Path

from pipmaster.core import PackageManager, logger as pm_logger

MOCK_EXECUTABLE = sys.executable

class TestPackageManager(unittest.TestCase):

    def setUp(self):
        self.pm = PackageManager(python_executable=MOCK_EXECUTABLE)

    def _create_mock_result(self, returncode=0, stdout="", stderr=""):
        mock_result = MagicMock(spec=subprocess.CompletedProcess)
        mock_result.returncode = returncode
        mock_result.stdout = stdout
        mock_result.stderr = stderr
        return mock_result

    @patch('subprocess.run')
    def test_run_pip_command_success(self, mock_run):
        mock_run.return_value = self._create_mock_result(returncode=0, stdout="Success!")
        success, output = self.pm._run_command(["list"], capture_output=True)
        self.assertTrue(success)
        self.assertEqual(output, "Success!")
        
        # Check that subprocess.run was called with a list (not shell string)
        mock_run.assert_called_once()
        call_args, call_kwargs = mock_run.call_args
        self.assertIsInstance(call_args[0], list)  # Command is a list
        self.assertIn("list", call_args[0])

    @patch('subprocess.run')
    def test_run_pip_command_failure(self, mock_run):
        mock_run.return_value = self._create_mock_result(returncode=1, stderr="Error!")
        success, output = self.pm._run_command(["install", "nonexistent"], capture_output=True)
        self.assertFalse(success)
        self.assertIn("Command failed (exit 1)", output)
        self.assertIn("--- stderr ---\nError!", output)

    @patch('subprocess.run')
    def test_install_success(self, mock_run):
        mock_run.return_value = self._create_mock_result(returncode=0)
        result = self.pm.install("requests")
        self.assertTrue(result)
        mock_run.assert_called_once()
        call_args, _ = mock_run.call_args
        # Make assertion less brittle - just check key elements exist
        self.assertIn("install", call_args[0])
        self.assertIn("--upgrade", call_args[0])
        self.assertIn("requests", call_args[0])

    @patch('subprocess.run')
    def test_install_failure(self, mock_run):
        mock_run.return_value = self._create_mock_result(returncode=1)
        result = self.pm.install("requests")
        self.assertFalse(result)

    @patch('importlib.metadata.version')
    def test_is_installed_true(self, mock_version):
        mock_version.return_value = "2.25.1"
        self.assertTrue(self.pm.is_installed("requests"))
        mock_version.assert_called_once_with("requests")

    @patch('importlib.metadata.version')
    def test_is_installed_false(self, mock_version):
        from importlib.metadata import PackageNotFoundError
        mock_version.side_effect = PackageNotFoundError("nonexistent")
        self.assertFalse(self.pm.is_installed("nonexistent"))
        mock_version.assert_called_once_with("nonexistent")

    @patch('importlib.metadata.version')
    def test_get_installed_version_success(self, mock_version):
        mock_version.return_value = "2.25.1"
        version = self.pm.get_installed_version("requests")
        self.assertEqual(version, "2.25.1")
        mock_version.assert_called_once_with("requests")

    @patch('importlib.metadata.version')
    def test_get_installed_version_not_found(self, mock_version):
        from importlib.metadata import PackageNotFoundError
        mock_version.side_effect = PackageNotFoundError("nonexistent")
        version = self.pm.get_installed_version("nonexistent")
        self.assertIsNone(version)
        mock_version.assert_called_once_with("nonexistent")

    @patch('pipmaster.core.PackageManager.is_installed')
    @patch('pipmaster.core.PackageManager._run_command')
    def test_install_multiple_if_not_installed_all_missing(self, mock_run_command, mock_is_installed):
        mock_is_installed.return_value = False
        mock_run_command.return_value = (True, "Success")
        packages = ["requests", "numpy"]

        result = self.pm.install_multiple_if_not_installed(packages, index_url="http://example.com")

        self.assertTrue(result)
        mock_is_installed.assert_has_calls([call("requests"), call("numpy")], any_order=True)

        # install_multiple adds --upgrade and uses capture_output=False
        expected_install_cmd = ["install", "--upgrade", "--index-url", "http://example.com", "requests", "numpy"]
        mock_run_command.assert_called_once_with(
            expected_install_cmd, dry_run=False, verbose=False, capture_output=False
        )

    @patch('pipmaster.core.PackageManager.is_installed')
    @patch('pipmaster.core.PackageManager._run_command')
    def test_install_multiple_if_not_installed_some_missing(self, mock_run_command, mock_is_installed):
        mock_is_installed.side_effect = lambda pkg: True if pkg == "requests" else False
        mock_run_command.return_value = (True, "Success")
        packages = ["requests", "numpy"]

        result = self.pm.install_multiple_if_not_installed(packages)

        self.assertTrue(result)
        mock_is_installed.assert_has_calls([call("requests"), call("numpy")], any_order=True)

        # install_multiple adds --upgrade and uses capture_output=False
        expected_install_cmd = ["install", "--upgrade", "numpy"]
        mock_run_command.assert_called_once_with(
            expected_install_cmd, dry_run=False, verbose=False, capture_output=False
        )

    @patch('pipmaster.core.PackageManager.is_installed')
    @patch('pipmaster.core.PackageManager._run_command')
    def test_install_multiple_if_not_installed_none_missing(self, mock_run_command, mock_is_installed):
        mock_is_installed.return_value = True
        packages = ["requests", "numpy"]
        result = self.pm.install_multiple_if_not_installed(packages)
        self.assertTrue(result)
        mock_is_installed.assert_has_calls([call("requests"), call("numpy")], any_order=True)
        mock_run_command.assert_not_called()

    @patch('pipmaster.core.PackageManager.get_installed_version')
    def test_is_version_compatible_success(self, mock_get_version):
        mock_get_version.return_value = "1.2.3"
        self.assertTrue(self.pm.is_version_compatible("mypkg", ">=1.2.0"))
        self.assertTrue(self.pm.is_version_compatible("mypkg", "==1.2.3"))
        self.assertFalse(self.pm.is_version_compatible("mypkg", ">1.2.3"))
        self.assertFalse(self.pm.is_version_compatible("mypkg", "<=1.0.0"))
        # Check that it's called for each check
        self.assertEqual(mock_get_version.call_count, 4)
        mock_get_version.assert_called_with("mypkg")

    @patch('pipmaster.core.PackageManager.get_installed_version')
    def test_is_version_compatible_not_installed(self, mock_get_version):
        mock_get_version.return_value = None
        self.assertFalse(self.pm.is_version_compatible("mypkg", ">=1.0.0"))

    @patch('pipmaster.core.PackageManager.get_installed_versions_batch')
    @patch('pipmaster.core.PackageManager.install_multiple')
    def test_ensure_packages_dict_all_met(self, mock_install_multiple, mock_batch):
        mock_batch.return_value = {"requests": "2.28.0", "numpy": "1.23.0"}
        requirements = {"requests": ">=2.0", "numpy": None}

        result = self.pm.ensure_packages(requirements)

        self.assertTrue(result)
        mock_batch.assert_called_once_with(["requests", "numpy"])
        mock_install_multiple.assert_not_called()

    @patch('pipmaster.core.PackageManager.get_installed_versions_batch')
    @patch('pipmaster.core.PackageManager.install_multiple')
    def test_ensure_packages_dict_some_missing(self, mock_install_multiple, mock_batch):
        mock_batch.return_value = {"requests": "2.28.0", "numpy": None}
        mock_install_multiple.return_value = True
        requirements = {"requests": ">=2.0", "numpy": ">=1.20"}

        result = self.pm.ensure_packages(requirements, verbose=True)

        self.assertTrue(result)
        mock_batch.assert_called_once_with(["requests", "numpy"])
        mock_install_multiple.assert_called_once_with(
            packages=["numpy>=1.20"],
            index_url=None,
            force_reinstall=False,
            upgrade=True,
            extra_args=None,
            dry_run=False,
            verbose=True
        )

    @patch('pipmaster.core.PackageManager.get_installed_versions_batch')
    @patch('pipmaster.core.PackageManager.install_multiple')
    def test_ensure_packages_list_input_simple(self, mock_install_multiple, mock_batch):
        mock_batch.return_value = {"numpy": "1.23.0", "pandas": None}
        mock_install_multiple.return_value = True
        requirements = ["numpy", "pandas"]

        result = self.pm.ensure_packages(requirements)

        self.assertTrue(result)
        mock_batch.assert_called_once_with(["numpy", "pandas"])
        mock_install_multiple.assert_called_once_with(
            packages=["pandas"],
            index_url=None, force_reinstall=False, upgrade=True,
            extra_args=None, dry_run=False, verbose=False
        )

    @patch('pipmaster.core.PackageManager.get_installed_versions_batch')
    @patch('pipmaster.core.PackageManager.install_multiple')
    def test_ensure_packages_list_with_specifiers(self, mock_install_multiple, mock_batch):
        mock_batch.return_value = {"requests": None, "pandas": None, "numpy": "1.23.0"}
        mock_install_multiple.return_value = True
        requirements = ["requests>=2.25", "pandas", "numpy"]

        result = self.pm.ensure_packages(requirements)

        self.assertTrue(result)
        mock_batch.assert_called_once_with(["requests", "pandas", "numpy"])
        mock_install_multiple.assert_called_once_with(
            packages=["requests>=2.25", "pandas"],
            index_url=None, force_reinstall=False, upgrade=True,
            extra_args=None, dry_run=False, verbose=False
        )

    @patch('pipmaster.core.PackageManager.is_installed')
    @patch('pipmaster.core.PackageManager.install_multiple')
    def test_ensure_packages_list_empty(self, mock_install_multiple, mock_is_installed):
        result = self.pm.ensure_packages([])
        self.assertTrue(result)
        mock_is_installed.assert_not_called()
        mock_install_multiple.assert_not_called()

    @patch('pipmaster.core.PackageManager.get_installed_versions_batch')
    @patch('pipmaster.core.PackageManager.install_multiple')
    def test_ensure_packages_list_invalid_item(self, mock_install_multiple, mock_batch):
        """Test that invalid package strings are handled gracefully without crashing."""
        # The invalid item gets parsed as package="invalid" with version specifier="package string!"
        # Since batch returns a version for "invalid", it gets checked
        mock_batch.return_value = {"requests": "2.28.0", "invalid": "1.0.0", "numpy": "1.23.0"}
        requirements = ["requests", "invalid package string!", "numpy"]

        # This should not raise an exception, even though the requirement is invalid
        result = self.pm.ensure_packages(requirements)
        self.assertTrue(result)
        mock_batch.assert_called_once_with(["requests", "invalid", "numpy"])
        # The "invalid" package gets scheduled for update due to version mismatch
        mock_install_multiple.assert_called_once()

    @patch.object(pm_logger, 'error')
    def test_ensure_packages_invalid_input_type(self, mock_logger_error):
        requirements = 123  # Use a type that is actually invalid
        result = self.pm.ensure_packages(requirements) # type: ignore
        # Current behavior returns True after logging error (no packages to process)
        self.assertTrue(result)
        mock_logger_error.assert_called_once()
        self.assertIn("Invalid requirements type", mock_logger_error.call_args[0][0])

    def test_ensure_requirements_success(self):
        """Test reading requirements from a file."""
        with patch('pipmaster.core.PackageManager.ensure_packages') as mock_ensure_packages:
            mock_ensure_packages.return_value = True

            # Use tempfile for cross-platform compatibility
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("requests>=2.25\n# A comment\nnumpy")
                req_file = f.name

            try:
                result = self.pm.ensure_requirements(req_file, dry_run=True, verbose=True)

                self.assertTrue(result)
                mock_ensure_packages.assert_called_once_with(
                    requirements=['requests>=2.25', 'numpy'],
                    index_url=None,
                    extra_args=[],
                    dry_run=True,
                    verbose=True
                )
            finally:
                os.unlink(req_file)

    def test_ensure_requirements_with_pip_options(self):
        """Test reading requirements with pip options from a file."""
        with patch('pipmaster.core.PackageManager.ensure_packages') as mock_ensure_packages:
            mock_ensure_packages.return_value = True

            import tempfile
            import os

            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("--index-url http://example.com\nrequests")
                req_file = f.name

            try:
                result = self.pm.ensure_requirements(req_file)

                self.assertTrue(result)
                mock_ensure_packages.assert_called_once_with(
                    requirements=['requests'],
                    index_url=None,
                    extra_args=['--index-url', 'http://example.com'],
                    dry_run=False,
                    verbose=False
                )
            finally:
                os.unlink(req_file)

    @patch('pipmaster.core.PackageManager.ensure_packages')
    def test_ensure_requirements_file_not_found(self, mock_ensure_packages):
        """Test handling of non-existent requirements file."""
        result = self.pm.ensure_requirements("non_existent_file_that_does_not_exist.txt")

        self.assertFalse(result)
        mock_ensure_packages.assert_not_called()

    def test_ensure_requirements_empty_or_comments_only(self):
        """Test handling of file with only comments/whitespace."""
        with patch('pipmaster.core.PackageManager.ensure_packages') as mock_ensure_packages:
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write("# Only comments\n\n   # and whitespace")
                req_file = f.name
            
            try:
                result = self.pm.ensure_requirements(req_file)
                
                self.assertTrue(result)
                mock_ensure_packages.assert_not_called()
            finally:
                os.unlink(req_file)

    @patch('subprocess.run')
    def test_run_pip_command_verbose_no_capture(self, mock_run):
        mock_run.return_value = self._create_mock_result(returncode=0)
        success, output = self.pm._run_command(["list"], capture_output=False, verbose=True)
        self.assertTrue(success)
        # When verbose=True and capture_output=False, stdout is None, so output is empty string
        self.assertEqual(output, "")

        # Check that subprocess.run was called with a list
        mock_run.assert_called_once()
        call_args, call_kwargs = mock_run.call_args
        self.assertIsInstance(call_args[0], list)
        self.assertIn("list", call_args[0])

    @patch('venv.create')
    def test_create_venv_if_not_exist(self, mock_venv_create):
        """Test that PackageManager creates venv when create_if_not_exist=True."""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmp_dir:
            venv_path = os.path.join(tmp_dir, "test_venv")

            # venv doesn't exist yet, create_if_not_exist=True should create it
            pm = PackageManager(venv_path=venv_path, create_if_not_exist=True)

            mock_venv_create.assert_called_once_with(venv_path, with_pip=True)
            self.assertEqual(pm.venv_path, venv_path)

    @patch('venv.create')
    def test_no_create_venv_by_default(self, mock_venv_create):
        """Test that PackageManager does NOT create venv by default (create_if_not_exist=False)."""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmp_dir:
            venv_path = os.path.join(tmp_dir, "test_venv")

            # venv doesn't exist, but create_if_not_exist defaults to False
            pm = PackageManager(venv_path=venv_path)

            mock_venv_create.assert_not_called()
            self.assertEqual(pm.venv_path, venv_path)

    @patch('venv.create')
    def test_no_create_venv_if_exists(self, mock_venv_create):
        """Test that PackageManager does not recreate existing venv even with create_if_not_exist=True."""
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as tmp_dir:
            venv_path = os.path.join(tmp_dir, "test_venv")
            os.makedirs(venv_path)

            # venv already exists, should not call venv.create
            pm = PackageManager(venv_path=venv_path, create_if_not_exist=True)

            mock_venv_create.assert_not_called()
            self.assertEqual(pm.venv_path, venv_path)

    @patch('venv.create')
    def test_create_venv_failure_raises(self, mock_venv_create):
        """Test that venv creation failure raises RuntimeError."""
        import tempfile
        import os

        mock_venv_create.side_effect = PermissionError("Permission denied")

        with tempfile.TemporaryDirectory() as tmp_dir:
            venv_path = os.path.join(tmp_dir, "test_venv")

            with self.assertRaises(RuntimeError) as context:
                PackageManager(venv_path=venv_path, create_if_not_exist=True)

            self.assertIn("Failed to create virtual environment", str(context.exception))
            mock_venv_create.assert_called_once_with(venv_path, with_pip=True)

    if __name__ == '__main__':
        unittest.main()
