import unittest
from unittest.mock import patch, MagicMock, call
import subprocess
import sys
import importlib.metadata

from pipmaster.package_manager import PackageManager, logging as pm_logging

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
        
        executable_path = self.pm._executable
        quoted_executable = f'"{executable_path}"' if " " in executable_path and not executable_path.startswith('"') else executable_path
        expected_cmd_str = f"{quoted_executable} -m pip list"

        mock_run.assert_called_once_with(
            expected_cmd_str,
            shell=True,
            check=False,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

    @patch('subprocess.run')
    def test_run_pip_command_failure(self, mock_run):
        mock_run.return_value = self._create_mock_result(returncode=1, stderr="Error!")
        success, output = self.pm._run_command(["install", "nonexistent"], capture_output=True)
        self.assertFalse(success)
        self.assertIn("Command failed with exit code 1", output)
        self.assertIn("--- stderr ---\nError!", output)

    @patch('subprocess.run')
    def test_install_success(self, mock_run):
        mock_run.return_value = self._create_mock_result(returncode=0)
        result = self.pm.install("requests")
        self.assertTrue(result)
        mock_run.assert_called_once()
        call_args, _ = mock_run.call_args
        # FIX: Make assertion less brittle
        self.assertIn("install", call_args[0])
        self.assertIn("--upgrade", call_args[0])
        self.assertIn("requests", call_args[0])

    @patch('subprocess.run')
    def test_install_failure(self, mock_run):
        mock_run.return_value = self._create_mock_result(returncode=1)
        result = self.pm.install("requests")
        self.assertFalse(result)

    @patch('importlib.metadata.distribution')
    def test_is_installed_true(self, mock_distribution):
        mock_distribution.return_value = MagicMock()
        self.assertTrue(self.pm.is_installed("requests"))
        mock_distribution.assert_called_once_with("requests")

    @patch('importlib.metadata.distribution')
    def test_is_installed_false(self, mock_distribution):
        mock_distribution.side_effect = importlib.metadata.PackageNotFoundError
        self.assertFalse(self.pm.is_installed("nonexistent"))
        mock_distribution.assert_called_once_with("nonexistent")

    @patch('importlib.metadata.version')
    def test_get_installed_version_success(self, mock_version):
        mock_version.return_value = "2.25.1"
        version = self.pm.get_installed_version("requests")
        self.assertEqual(version, "2.25.1")
        mock_version.assert_called_once_with("requests")

    @patch('importlib.metadata.version')
    def test_get_installed_version_not_found(self, mock_version):
        mock_version.side_effect = importlib.metadata.PackageNotFoundError
        version = self.pm.get_installed_version("nonexistent")
        self.assertIsNone(version)

    @patch('pipmaster.package_manager.PackageManager.is_installed')
    @patch('pipmaster.package_manager.PackageManager._run_command')
    def test_install_multiple_if_not_installed_all_missing(self, mock_run_command, mock_is_installed):
        mock_is_installed.return_value = False
        mock_run_command.return_value = (True, "Success")
        packages = ["requests", "numpy"]

        result = self.pm.install_multiple_if_not_installed(packages, index_url="http://example.com")

        self.assertTrue(result)
        mock_is_installed.assert_has_calls([call("requests"), call("numpy")], any_order=True)
        
        expected_install_cmd = ["install", "--index-url", "http://example.com", "requests", "numpy"]
        mock_run_command.assert_called_once_with(
            expected_install_cmd, dry_run=False, verbose=False, capture_output=True
        )

    @patch('pipmaster.package_manager.PackageManager.is_installed')
    @patch('pipmaster.package_manager.PackageManager._run_command')
    def test_install_multiple_if_not_installed_some_missing(self, mock_run_command, mock_is_installed):
        mock_is_installed.side_effect = lambda pkg: True if pkg == "requests" else False
        mock_run_command.return_value = (True, "Success")
        packages = ["requests", "numpy"]

        result = self.pm.install_multiple_if_not_installed(packages)

        self.assertTrue(result)
        mock_is_installed.assert_has_calls([call("requests"), call("numpy")], any_order=True)

        expected_install_cmd = ["install", "numpy"]
        mock_run_command.assert_called_once_with(
            expected_install_cmd, dry_run=False, verbose=False, capture_output=True
        )

    @patch('pipmaster.package_manager.PackageManager.is_installed')
    @patch('pipmaster.package_manager.PackageManager._run_command')
    def test_install_multiple_if_not_installed_none_missing(self, mock_run_command, mock_is_installed):
        mock_is_installed.return_value = True
        packages = ["requests", "numpy"]
        result = self.pm.install_multiple_if_not_installed(packages)
        self.assertTrue(result)
        mock_is_installed.assert_has_calls([call("requests"), call("numpy")], any_order=True)
        mock_run_command.assert_not_called()

    @patch('pipmaster.package_manager.PackageManager.get_installed_version')
    def test_is_version_compatible_success(self, mock_get_version):
        mock_get_version.return_value = "1.2.3"
        self.assertTrue(self.pm.is_version_compatible("mypkg", ">=1.2.0"))
        self.assertTrue(self.pm.is_version_compatible("mypkg", "==1.2.3"))
        self.assertFalse(self.pm.is_version_compatible("mypkg", ">1.2.3"))
        self.assertFalse(self.pm.is_version_compatible("mypkg", "<=1.0.0"))
        # Check that it's called for each check
        self.assertEqual(mock_get_version.call_count, 4)
        mock_get_version.assert_called_with("mypkg")

    @patch('pipmaster.package_manager.PackageManager.get_installed_version')
    def test_is_version_compatible_not_installed(self, mock_get_version):
        mock_get_version.return_value = None
        self.assertFalse(self.pm.is_version_compatible("mypkg", ">=1.0.0"))

    @patch('pipmaster.package_manager.PackageManager.is_installed')
    @patch('pipmaster.package_manager.PackageManager.install_multiple')
    def test_ensure_packages_dict_all_met(self, mock_install_multiple, mock_is_installed):
        mock_is_installed.return_value = True
        requirements = {"requests": ">=2.0", "numpy": None}

        result = self.pm.ensure_packages(requirements)

        self.assertTrue(result)
        mock_is_installed.assert_has_calls([call("requests", version_specifier=">=2.0"), call("numpy", version_specifier=None)], any_order=True)
        mock_install_multiple.assert_not_called()

    @patch('pipmaster.package_manager.PackageManager.is_installed')
    @patch('pipmaster.package_manager.PackageManager.install_multiple')
    def test_ensure_packages_dict_some_missing(self, mock_install_multiple, mock_is_installed):
        mock_is_installed.side_effect = lambda pkg, version_specifier=None: True if pkg == "requests" else False
        mock_install_multiple.return_value = True
        requirements = {"requests": ">=2.0", "numpy": ">=1.20"}

        result = self.pm.ensure_packages(requirements, verbose=True)

        self.assertTrue(result)
        mock_is_installed.assert_has_calls([
            call("requests", version_specifier=">=2.0"),
            call("numpy", version_specifier=">=1.20")
        ], any_order=True)
        mock_install_multiple.assert_called_once_with(
            packages=["numpy>=1.20"],
            index_url=None,
            force_reinstall=False,
            upgrade=True,
            extra_args=None,
            dry_run=False,
            verbose=True
        )

    @patch('pipmaster.package_manager.PackageManager.is_installed')
    @patch('pipmaster.package_manager.PackageManager.install_multiple')
    def test_ensure_packages_list_input_simple(self, mock_install_multiple, mock_is_installed):
        mock_is_installed.side_effect = lambda pkg, version_specifier=None: True if pkg == "numpy" else False
        mock_install_multiple.return_value = True
        requirements = ["numpy", "pandas"]

        result = self.pm.ensure_packages(requirements)

        self.assertTrue(result)
        mock_is_installed.assert_has_calls([
            call("numpy", version_specifier=None),
            call("pandas", version_specifier=None)
        ], any_order=True)
        mock_install_multiple.assert_called_once_with(
            packages=["pandas"],
            index_url=None, force_reinstall=False, upgrade=True,
            extra_args=None, dry_run=False, verbose=False
        )

    @patch('pipmaster.package_manager.PackageManager.is_installed')
    @patch('pipmaster.package_manager.PackageManager.install_multiple')
    def test_ensure_packages_list_with_specifiers(self, mock_install_multiple, mock_is_installed):
        def is_installed_mock(pkg, version_specifier=None):
            if pkg == "requests" and version_specifier == ">=2.25": return False
            if pkg == "pandas" and version_specifier is None: return False
            if pkg == "numpy" and version_specifier is None: return True
            return True # Default to True for other calls

        mock_is_installed.side_effect = is_installed_mock
        mock_install_multiple.return_value = True
        requirements = ["requests>=2.25", "pandas", "numpy"]

        result = self.pm.ensure_packages(requirements)

        self.assertTrue(result)
        mock_is_installed.assert_has_calls([
            call("requests", version_specifier=">=2.25"),
            call("pandas", version_specifier=None),
            call("numpy", version_specifier=None),
        ], any_order=True)
        mock_install_multiple.assert_called_once_with(
            packages=["requests>=2.25", "pandas"],
            index_url=None, force_reinstall=False, upgrade=True,
            extra_args=None, dry_run=False, verbose=False
        )

    @patch('pipmaster.package_manager.PackageManager.is_installed')
    @patch('pipmaster.package_manager.PackageManager.install_multiple')
    def test_ensure_packages_list_empty(self, mock_install_multiple, mock_is_installed):
        result = self.pm.ensure_packages([])
        self.assertTrue(result)
        mock_is_installed.assert_not_called()
        mock_install_multiple.assert_not_called()

    @patch('pipmaster.package_manager.PackageManager.is_installed')
    @patch('pipmaster.package_manager.PackageManager.install_multiple')
    def test_ensure_packages_list_invalid_item(self, mock_install_multiple, mock_is_installed):
        mock_is_installed.return_value = True
        requirements = ["requests", "invalid package string!", "numpy"]

        result = self.pm.ensure_packages(requirements)
        self.assertTrue(result)
        mock_is_installed.assert_has_calls([
            call("requests", version_specifier=None),
            call("numpy", version_specifier=None),
        ], any_order=True)
        mock_install_multiple.assert_not_called()

    @patch.object(pm_logging.getLogger("pipmaster.package_manager"), 'error')
    def test_ensure_packages_invalid_input_type(self, mock_logger_error):
        requirements = 123  # Use a type that is actually invalid
        result = self.pm.ensure_packages(requirements) # type: ignore
        self.assertFalse(result)
        mock_logger_error.assert_called_once()
        self.assertIn("Invalid requirements type", mock_logger_error.call_args[0][0])

    @patch('subprocess.run')
    def test_run_pip_command_verbose_no_capture(self, mock_run):
        mock_run.return_value = self._create_mock_result(returncode=0)
        success, output = self.pm._run_command(["list"], capture_output=False, verbose=True)
        self.assertTrue(success)
        self.assertEqual(output, "Command executed successfully.")

        executable_path = self.pm._executable
        quoted_executable = f'"{executable_path}"' if " " in executable_path and not executable_path.startswith('"') else executable_path
        expected_cmd_str = f"{quoted_executable} -m pip list"

        mock_run.assert_called_once_with(
            expected_cmd_str,
            shell=True,
            check=False,
            stdout=None,
            stderr=None,
            text=True,
            encoding='utf-8'
        )

if __name__ == '__main__':
    unittest.main()