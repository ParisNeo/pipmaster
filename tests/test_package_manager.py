import unittest
from unittest.mock import patch, MagicMock, call # Import call
import subprocess
import sys
import importlib # For mocking importlib.metadata
from packaging.version import parse as parse_version # For mocking packaging.version

# Adjust the import path based on your project structure
from pipmaster.package_manager import PackageManager

# Define constants for mocking
MOCK_EXECUTABLE = sys.executable

class TestPackageManager(unittest.TestCase):

    def setUp(self):
        # Instantiate PackageManager for each test
        self.pm = PackageManager(python_executable=MOCK_EXECUTABLE)

    # Helper to create mock subprocess result
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

        # Construct expected command string based on actual executable path
        # Use the _executable attribute stored during pm initialization
        executable_path = self.pm._executable # Get the path used by the instance
        # Apply the same quoting logic as in __init__ for comparison
        quoted_executable = (
            f'"{executable_path}"'
            if " " in executable_path and not executable_path.startswith('"')
            else executable_path
        )
        expected_cmd_list = [quoted_executable, "-m", "pip", "list"]
        expected_cmd_str = " ".join(expected_cmd_list) # This should now match the actual call

        # Compare against the string passed to subprocess.run
        mock_run.assert_called_once_with(
            expected_cmd_str, # Use the correctly constructed string
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
        self.assertIn("--- stderr ---\nError!", output) # Checks for the specific formattin

    @patch('subprocess.run')
    def test_install_success(self, mock_run):
        mock_run.return_value = self._create_mock_result(returncode=0)
        result = self.pm.install("requests")
        self.assertTrue(result)
        expected_cmd_part = f' install requests --upgrade' # Default is upgrade=True
        mock_run.assert_called_once()
        call_args, _ = mock_run.call_args
        self.assertIn(expected_cmd_part, call_args[0])


    @patch('subprocess.run')
    def test_install_failure(self, mock_run):
        mock_run.return_value = self._create_mock_result(returncode=1)
        result = self.pm.install("requests")
        self.assertFalse(result)

    @patch('importlib.metadata.distribution')
    def test_is_installed_true(self, mock_distribution):
        mock_distribution.return_value = MagicMock() # Just needs to not raise error
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
    def test_install_multiple_if_not_installed_all_missing(self, mock_run_pip, mock_is_installed):
        mock_is_installed.return_value = False # Simulate all packages are missing
        mock_run_pip.return_value = (True, "Success") # Simulate install succeeds
        packages = ["requests", "numpy"]

        result = self.pm.install_multiple_if_not_installed(packages, index_url="http://example.com")

        self.assertTrue(result)
        # Check is_installed was called for each package
        mock_is_installed.assert_has_calls([call("requests"), call("numpy")], any_order=True)
        # Check _run_pip_command was called with the correct install command
        expected_install_cmd = ["install", "requests", "numpy", "--index-url", "http://example.com"]
        mock_run_pip.assert_called_once_with(expected_install_cmd, dry_run=False)

    @patch('pipmaster.package_manager.PackageManager.is_installed')
    @patch('pipmaster.package_manager.PackageManager._run_command')
    def test_install_multiple_if_not_installed_some_missing(self, mock_run_pip, mock_is_installed):
        # Simulate 'requests' installed, 'numpy' missing
        mock_is_installed.side_effect = lambda pkg: True if pkg == "requests" else False
        mock_run_pip.return_value = (True, "Success")
        packages = ["requests", "numpy"]

        result = self.pm.install_multiple_if_not_installed(packages)

        self.assertTrue(result)
        mock_is_installed.assert_has_calls([call("requests"), call("numpy")], any_order=True)
        # Should only install numpy
        expected_install_cmd = ["install", "numpy"]
        mock_run_pip.assert_called_once_with(expected_install_cmd, dry_run=False)

    @patch('pipmaster.package_manager.PackageManager.is_installed')
    @patch('pipmaster.package_manager.PackageManager._run_command')
    def test_install_multiple_if_not_installed_none_missing(self, mock_run_pip, mock_is_installed):
        mock_is_installed.return_value = True # Simulate all are installed
        packages = ["requests", "numpy"]

        result = self.pm.install_multiple_if_not_installed(packages)

        self.assertTrue(result)
        mock_is_installed.assert_has_calls([call("requests"), call("numpy")], any_order=True)
        # Should not call install
        mock_run_pip.assert_not_called()

    @patch('pipmaster.package_manager.PackageManager.get_installed_version')
    def test_is_version_compatible_success(self, mock_get_version):
        mock_get_version.return_value = "1.2.3"
        self.assertTrue(self.pm.is_version_compatible("mypkg", ">=1.2.0"))
        self.assertTrue(self.pm.is_version_compatible("mypkg", "==1.2.3"))
        self.assertFalse(self.pm.is_version_compatible("mypkg", ">1.2.3"))
        self.assertFalse(self.pm.is_version_compatible("mypkg", "<=1.0.0"))
        mock_get_version.assert_called_with("mypkg") # Should be called multiple times


    @patch('pipmaster.package_manager.PackageManager.get_installed_version')
    def test_is_version_compatible_not_installed(self, mock_get_version):
        mock_get_version.return_value = None
        self.assertFalse(self.pm.is_version_compatible("mypkg", ">=1.0.0"))

    # Add more tests for other methods like uninstall, install_version, etc.
    # Remember to mock subprocess.run and importlib.metadata appropriately

if __name__ == '__main__':
    unittest.main()