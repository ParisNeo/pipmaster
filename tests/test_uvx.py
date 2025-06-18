# -*- coding: utf-8 -*-
"""
Tests for newly added features in pipmaster, such as the UvPackageManager
and new utility functions.

Author: ParisNeo
Created: 24/04/2025
"""

import pytest
import sys
import os
import shutil
import subprocess

# Import the components to be tested
from pipmaster import (
    get_pip_manager,
    get_uv_manager,
    get_current_package_version,
    UvPackageManager,
)

# --- Tests for New Functions in the Standard Pip Manager ---

class TestNewPipFeatures:
    """Tests for new functions added to the existing PackageManager."""

    def test_get_current_package_version_alias(self):
        """
        Tests the get_current_package_version alias to ensure it behaves
        identically to get_installed_version.
        """
        pm = get_pip_manager()
        # Pytest itself should be installed in the test environment
        pytest_version = pm.get_installed_version("pytest")
        pytest_version_alias = pm.get_current_package_version("pytest")

        assert pytest_version is not None
        assert isinstance(pytest_version, str)
        assert pytest_version == pytest_version_alias

    def test_get_current_package_version_for_non_existent_package(self):
        """Tests the alias for a package that is not installed."""
        pm = get_pip_manager()
        version = pm.get_current_package_version("non-existent-package-for-pipmaster-testing-12345")
        assert version is None

    def test_module_level_get_current_package_version(self):
        """Tests the module-level wrapper for the new alias."""
        # This function uses the default (current env) manager
        pytest_version = get_current_package_version("pytest")
        assert pytest_version is not None
        assert isinstance(pytest_version, str)


# --- Tests for the new UvPackageManager ---

# Skip all tests in this class if 'uv' is not available in the system's PATH
uv_available = shutil.which("uv") is not None

@pytest.mark.skipif(not uv_available, reason="uv executable not found in PATH")
class TestUvPackageManager:
    """
    Tests for the UvPackageManager. These tests will create and destroy
    a temporary virtual environment.
    """

    @pytest.fixture
    def uv_test_env(self, tmp_path):
        """A pytest fixture to create and clean up a temporary directory for the uv env."""
        env_path = tmp_path / "uv_test_env"
        yield str(env_path)  # Provide the path to the test
        # Teardown: clean up the directory after the test is done
        if os.path.exists(env_path):
            shutil.rmtree(env_path)

    def test_uv_manager_init_and_factory(self):
        """Test the initialization of UvPackageManager and the factory function."""
        # Test factory function
        manager = get_uv_manager()
        assert isinstance(manager, UvPackageManager)
        assert manager.environment_path is None
        assert manager.python_executable is None
        
        # Test initialization with a path
        manager_with_path = get_uv_manager(environment_path="/fake/path")
        assert manager_with_path.environment_path == "/fake/path"
    
    def test_uv_init_raises_error_if_uv_missing(self, monkeypatch):
        """Test that UvPackageManager raises FileNotFoundError if uv is not found."""
        # Temporarily make shutil.which return None for 'uv'
        monkeypatch.setattr(shutil, 'which', lambda x: None)
        with pytest.raises(FileNotFoundError):
            UvPackageManager()

    def test_create_env_success(self, uv_test_env):
        """Test creating a new virtual environment with uv."""
        manager = get_uv_manager()
        success = manager.create_env(path=uv_test_env)
        
        assert success is True
        assert manager.environment_path == uv_test_env
        assert os.path.isdir(uv_test_env)
        
        # Verify the python executable exists
        assert manager.python_executable is not None
        assert os.path.isfile(manager.python_executable)

    def test_install_and_verify_single_package(self, uv_test_env):
        """Test installing a single package into a uv environment."""
        manager = get_uv_manager()
        assert manager.create_env(path=uv_test_env)
        
        # Install 'requests'
        install_success = manager.install("requests")
        assert install_success is True
        
        # Verify 'requests' can be imported using the new environment's python
        py_exe = manager.python_executable
        result = subprocess.run([py_exe, "-c", "import requests"], capture_output=True, text=True)
        assert result.returncode == 0, f"Verification failed: {result.stderr}"

    def test_install_multiple_packages(self, uv_test_env):
        """Test installing multiple packages into a uv environment."""
        manager = get_uv_manager()
        assert manager.create_env(path=uv_test_env)
        
        packages = ["six", "python-dateutil"]
        install_success = manager.install_multiple(packages)
        assert install_success is True
        
        # Verify both packages
        py_exe = manager.python_executable
        result_six = subprocess.run([py_exe, "-c", "import six"], capture_output=True)
        result_dateutil = subprocess.run([py_exe, "-c", "import dateutil"], capture_output=True)
        
        assert result_six.returncode == 0, "Verification for 'six' failed."
        assert result_dateutil.returncode == 0, "Verification for 'python-dateutil' failed."

    def test_uninstall_package(self, uv_test_env):
        """Test uninstalling a package from a uv environment."""
        manager = get_uv_manager(environment_path=uv_test_env)
        assert manager.create_env(path=uv_test_env)
        
        # Install a package first
        assert manager.install("click")
        py_exe = manager.python_executable
        result_install = subprocess.run([py_exe, "-c", "import click"], capture_output=True)
        assert result_install.returncode == 0, "Pre-test installation failed."
        
        # Now, uninstall it
        uninstall_success = manager.uninstall("click")
        assert uninstall_success is True
        
        # Verify it's gone
        result_uninstall = subprocess.run([py_exe, "-c", "import click"], capture_output=True)
        assert result_uninstall.returncode != 0, "'click' should have been uninstalled."
    
    def test_run_with_uvx(self):
        """
        Test the uvx functionality to run a command in an ephemeral environment.
        This test does not require a pre-existing environment.
        """
        manager = get_uv_manager()

        # ---- CHANGE IS HERE ----
        # Use 'black --version' instead of 'cowsay'. black is a highly standard
        # package and a more robust choice for this kind of test.
        command_to_run = ["black", "--version"]

        success = manager.run_with_uvx(command_to_run, verbose=True)
        # ---- END OF CHANGE ----

        # The primary assertion is that the command ran successfully (exit code 0).
        # We trust uvx to handle the temporary environment and package installation.
        assert success is True