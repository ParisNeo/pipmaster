# -*- coding: utf-8 -*-
"""
Tests for the Asynchronous Package Manager.

Author: ParisNeo
Created: 23/04/2025
Last Updated: 23/04/2025
"""

import pytest
import pytest_asyncio # Implicitly used by @pytest.mark.asyncio
import asyncio
import sys
from unittest.mock import patch, AsyncMock, MagicMock, call
from typing import Tuple, Optional

# Adjust import path as necessary
from pipmaster.async_package_manager import AsyncPackageManager
import importlib # For mocking importlib.metadata
import shutil # For mocking shutil.which

# Define constants for mocking
MOCK_EXECUTABLE = sys.executable

# Helper to create a mock asyncio.subprocess.Process
def _create_mock_async_process(
    returncode: int = 0, stdout: str = "", stderr: str = ""
) -> AsyncMock:
    """Creates an AsyncMock representing an asyncio subprocess process."""
    mock_process = AsyncMock(spec=asyncio.subprocess.Process)
    mock_process.returncode = returncode
    # communicate returns bytes
    stdout_bytes = stdout.encode("utf-8")
    stderr_bytes = stderr.encode("utf-8")
    mock_process.communicate = AsyncMock(return_value=(stdout_bytes, stderr_bytes))
    return mock_process

@pytest.fixture
def apm() -> AsyncPackageManager:
    """Provides an instance of AsyncPackageManager for testing."""
    # Using the actual sys.executable for consistency unless specifically testing path handling
    return AsyncPackageManager(python_executable=MOCK_EXECUTABLE)

# Mark all tests in this module to be run by pytest-asyncio
pytestmark = pytest.mark.asyncio

# === Test _run_command ===

@patch("asyncio.create_subprocess_shell", new_callable=AsyncMock)
async def test_async_run_command_success(mock_create_subprocess, apm: AsyncPackageManager):
    """Test successful execution of _run_command."""
    mock_create_subprocess.return_value = _create_mock_async_process(
        returncode=0, stdout="Success!"
    )
    success, output = await apm._run_command(["list"], capture_output=True)

    assert success is True
    assert output == "Success!"
    # Construct expected command string like the method does
    expected_cmd_str = " ".join(apm.pip_command_base + ["list"])
    mock_create_subprocess.assert_awaited_once_with(
        expected_cmd_str,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

@patch("asyncio.create_subprocess_shell", new_callable=AsyncMock)
async def test_async_run_command_failure(mock_create_subprocess, apm: AsyncPackageManager):
    """Test failed execution of _run_command."""
    mock_create_subprocess.return_value = _create_mock_async_process(
        returncode=1, stderr="Error!"
    )
    success, output = await apm._run_command(
        ["install", "nonexistent"], capture_output=True
    )

    assert success is False
    assert "[Async] Command failed (code 1)" in output
    assert "--- stderr ---\nError!" in output # Check specific formatting
    expected_cmd_str = " ".join(apm.pip_command_base + ["install", "nonexistent"])
    mock_create_subprocess.assert_awaited_once_with(
        expected_cmd_str,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

@patch("asyncio.create_subprocess_shell", new_callable=AsyncMock)
async def test_async_run_command_dry_run(mock_create_subprocess, apm: AsyncPackageManager):
    """Test dry run functionality."""
    # Dry run shouldn't actually call subprocess if applicable
    success, output = await apm._run_command(["install", "requests"], dry_run=True)

    assert success is True
    assert "Dry run: Command would be" in output
    assert "--dry-run" in output
    assert " install " in output # Check it's an install command
    assert " requests" in output
    mock_create_subprocess.assert_not_awaited() # Should not be called for dry run


# === Test install ===

@patch("pipmaster.async_package_manager.AsyncPackageManager._run_command", new_callable=AsyncMock)
async def test_async_install_success(mock_run_command, apm: AsyncPackageManager):
    """Test successful async install call."""
    mock_run_command.return_value = (True, "Successfully installed requests")
    result = await apm.install("requests", extra_args=["--no-cache"])

    assert result is True
    expected_cmd = [
        "install", "requests", "--upgrade", "--no-cache" # Default upgrade=True
    ]
    mock_run_command.assert_awaited_once_with(expected_cmd, dry_run=False)

@patch("pipmaster.async_package_manager.AsyncPackageManager._run_command", new_callable=AsyncMock)
async def test_async_install_failure(mock_run_command, apm: AsyncPackageManager):
    """Test failed async install call."""
    mock_run_command.return_value = (False, "Installation failed")
    result = await apm.install("requests", upgrade=False) # Test without upgrade

    assert result is False
    expected_cmd = ["install", "requests"] # upgrade=False
    mock_run_command.assert_awaited_once_with(expected_cmd, dry_run=False)

# === Test install_if_missing ===
# Note: Testing this accurately is complex due to run_in_executor.
# We mock the *sync* is_installed that the executor eventually calls.

@patch("pipmaster.package_manager.PackageManager.is_installed") # Mock the sync method called via executor
@patch("pipmaster.async_package_manager.AsyncPackageManager.install", new_callable=AsyncMock) # Mock the async install method it calls
async def test_async_install_if_missing_package_missing(mock_async_install, mock_sync_is_installed, apm: AsyncPackageManager):
    """Test install_if_missing when package is not installed."""
    mock_sync_is_installed.return_value = False # Simulate package not found by sync check
    mock_async_install.return_value = True # Simulate install succeeds

    result = await apm.install_if_missing("requests", version_specifier=">=2.0", index_url="some_url")

    assert result is True
    mock_sync_is_installed.assert_called_once_with("requests") # Check sync is_installed was called
    # Check that async install was called with the *original* arguments
    mock_async_install.assert_awaited_once_with(
        "requests", version_specifier=">=2.0", index_url="some_url"
    )

@patch("pipmaster.package_manager.PackageManager.is_installed")
@patch("pipmaster.async_package_manager.AsyncPackageManager.install", new_callable=AsyncMock)
async def test_async_install_if_missing_package_present_no_update(mock_async_install, mock_sync_is_installed, apm: AsyncPackageManager):
    """Test install_if_missing when package is present and meets requirements."""
    mock_sync_is_installed.return_value = True # Simulate package is installed

    result = await apm.install_if_missing("requests", version_specifier=None, always_update=False)

    assert result is True
    mock_sync_is_installed.assert_called_once_with("requests")
    mock_async_install.assert_not_awaited() # Install should not be called

@patch("pipmaster.package_manager.PackageManager.is_installed")
@patch("pipmaster.async_package_manager.AsyncPackageManager.install", new_callable=AsyncMock)
async def test_async_install_if_missing_package_present_force_update(mock_async_install, mock_sync_is_installed, apm: AsyncPackageManager):
    """Test install_if_missing when package is present but always_update=True."""
    mock_sync_is_installed.return_value = True # Simulate package is installed
    mock_async_install.return_value = True

    result = await apm.install_if_missing("requests", always_update=True)

    assert result is True
    mock_sync_is_installed.assert_called_once_with("requests")
    # Check that async install was called, effectively triggering an update check
    mock_async_install.assert_awaited_once_with("requests", always_update=True)


# === Test Check Vulnerabilities ===

@patch("shutil.which")
@patch("asyncio.create_subprocess_shell", new_callable=AsyncMock)
async def test_async_check_vulnerabilities_no_vulns(mock_create_subprocess, mock_which, apm: AsyncPackageManager):
    """Test vulnerability check when no vulnerabilities are found."""
    mock_which.return_value = "/path/to/pip-audit" # Simulate pip-audit is found
    mock_create_subprocess.return_value = _create_mock_async_process(
        returncode=0, stdout="No vulnerabilities found"
    )
    found, output = await apm.check_vulnerabilities()

    assert found is False
    assert output == "No vulnerabilities found"
    mock_which.assert_called_once_with("pip-audit")
    mock_create_subprocess.assert_awaited_once()
    # Check the command string passed to shell
    call_args, _ = mock_create_subprocess.call_args
    assert call_args[0] == "/path/to/pip-audit"

@patch("shutil.which")
@patch("asyncio.create_subprocess_shell", new_callable=AsyncMock)
async def test_async_check_vulnerabilities_found_vulns(mock_create_subprocess, mock_which, apm: AsyncPackageManager):
    """Test vulnerability check when vulnerabilities are found."""
    mock_which.return_value = "/path/to/pip-audit"
    mock_create_subprocess.return_value = _create_mock_async_process(
        returncode=1, stdout="Found 1 vulnerability", stderr=""
    )
    found, output = await apm.check_vulnerabilities(requirements_file="reqs.txt", extra_args=["--fix"])

    assert found is True
    assert "Vulnerabilities found" in output
    assert "Found 1 vulnerability" in output
    mock_which.assert_called_once_with("pip-audit")
    mock_create_subprocess.assert_awaited_once()
    call_args, _ = mock_create_subprocess.call_args
    assert call_args[0] == "/path/to/pip-audit -r reqs.txt --fix"

@patch("shutil.which")
@patch("asyncio.create_subprocess_shell", new_callable=AsyncMock)
async def test_async_check_vulnerabilities_pip_audit_error(mock_create_subprocess, mock_which, apm: AsyncPackageManager):
    """Test vulnerability check when pip-audit itself fails."""
    mock_which.return_value = "/path/to/pip-audit"
    mock_create_subprocess.return_value = _create_mock_async_process(
        returncode=2, stderr="Pip audit internal error"
    )
    found, output = await apm.check_vulnerabilities()

    assert found is True # Assume vulnerable on error
    assert "pip-audit error" in output
    assert "Pip audit internal error" in output
    mock_which.assert_called_once_with("pip-audit")
    mock_create_subprocess.assert_awaited_once()

@patch("shutil.which")
@patch("asyncio.create_subprocess_shell", new_callable=AsyncMock)
async def test_async_check_vulnerabilities_not_found(mock_create_subprocess, mock_which, apm: AsyncPackageManager):
    """Test vulnerability check when pip-audit is not installed."""
    mock_which.return_value = None # Simulate pip-audit not found
    found, output = await apm.check_vulnerabilities()

    assert found is True # Assume vulnerable if tool missing
    assert "pip-audit not found" in output
    mock_which.assert_called_once_with("pip-audit")
    mock_create_subprocess.assert_not_awaited() # Should not be called if tool missing

# === Add more tests for other async methods ===
# Example: async_uninstall

@patch("pipmaster.async_package_manager.AsyncPackageManager._run_command", new_callable=AsyncMock)
async def test_async_uninstall_success(mock_run_command, apm: AsyncPackageManager):
    """Test successful async uninstall."""
    mock_run_command.return_value = (True, "Successfully uninstalled")
    # Dynamically get the uninstall method to call (if wrappers were used)
    # For now, assuming direct call if testing the class method
    uninstall_method = getattr(apm, 'uninstall', None) or getattr(apm, '_uninstall', None) # Placeholder if needed
    if uninstall_method is None: pytest.skip("Uninstall method not implemented/found for test")

    result = await uninstall_method("requests", dry_run=True) # Test with dry run

    assert result is True
    expected_cmd = ["uninstall", "-y", "requests"]
    # Check that _run_command was called correctly with dry_run
    mock_run_command.assert_awaited_once_with(expected_cmd, dry_run=True)


# === Test module level wrappers (Optional but good practice) ===
# Need to patch the default instance's methods

@patch("pipmaster.async_package_manager._default_async_pm.install", new_callable=AsyncMock)
async def test_module_async_install(mock_install):
    """Test the module-level async install wrapper."""
    from pipmaster.async_package_manager import async_install # Import the wrapper
    mock_install.return_value = True

    await async_install("requests", index_url="test_url")

    mock_install.assert_awaited_once_with("requests", index_url="test_url")

# Add more tests for other wrapped functions...