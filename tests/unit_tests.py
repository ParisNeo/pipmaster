import unittest
from unittest.mock import patch, MagicMock
from pipmaster import PackageManager  # Adjust the import based on your file structure
import subprocess

class TestPackageManager(unittest.TestCase):

    def setUp(self):
        self.pm = PackageManager()

    @patch('subprocess.run')
    def test_install_success(self, mock_run):
        mock_run.return_value = None  # Simulate successful installation
        result = self.pm.install("requests")
        self.assertTrue(result)

    @patch('subprocess.run')
    def test_install_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'pip install requests')  # Simulate failure
        result = self.pm.install("requests")
        self.assertFalse(result)

    @patch('subprocess.run')
    def test_install_multiple_success(self, mock_run):
        mock_run.return_value = None  # Simulate successful installation
        packages = ["requests", "numpy"]
        results = self.pm.install_multiple(packages)
        for package in packages:
            self.assertTrue(results[package])

    @patch('subprocess.run')
    def test_install_multiple_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'pip install requests')  # Simulate failure for the first package
        packages = ["requests", "numpy"]
        results = self.pm.install_multiple(packages)
        self.assertFalse(results["requests"])
        self.assertTrue(results["numpy"])  # Assuming numpy installs successfully

    @patch('subprocess.check_output')
    def test_get_installed_version_success(self, mock_check_output):
        mock_check_output.return_value = "Version: 2.25.1\n"
        version = self.pm.get_installed_version("requests")
        self.assertEqual(version, "2.25.1")

    @patch('subprocess.check_output')
    def test_get_installed_version_failure(self, mock_check_output):
        mock_check_output.side_effect = subprocess.CalledProcessError(1, 'pip show requests')
        version = self.pm.get_installed_version("requests")
        self.assertIsNone(version)

    @patch('subprocess.run')
    def test_is_installed_success(self, mock_run):
        mock_run.return_value = None  # Simulate package is installed
        result = self.pm.is_installed("requests")
        self.assertTrue(result)

    @patch('subprocess.run')
    def test_is_installed_failure(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, 'pip show requests')  # Simulate package is not installed
        result = self.pm.is_installed("requests")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
