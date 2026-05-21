# -*- coding: utf-8 -*-
"""
Factory functions for creating package manager instances.

Provides convenient factory functions to get configured instances
of PackageManager, UvPackageManager, and other backends.

Author: ParisNeo
Created: 01/04/2024
Last Updated: 13/02/2026
"""

from pathlib import Path
from typing import Optional, Any

from .core import PackageManager, logger
from .portable_python import PythonVersionManager
from .backends import UvPackageManager, CondaPackageManager

# Cache for default package manager instance
_default_pm = None


def get_pip_manager(python_executable: Optional[str] = None, venv_path: Optional[str] = None, create_if_not_exist: bool = False) -> PackageManager:
    """
    Gets a PackageManager instance, potentially targeting a specific Python environment.

    Args:
        python_executable (str, optional): Path to the Python executable
            of the target environment. Defaults to sys.executable (current env).
        venv_path (str, optional): Path to a virtual environment to use.
        create_if_not_exist (bool, optional): If True and venv_path is provided,
            creates the virtual environment if it doesn't exist. Defaults to False.

    Returns:
        PackageManager: An instance configured for the target environment.
    """
    global _default_pm

    if python_executable or venv_path:
        return PackageManager(python_executable=python_executable, venv_path=venv_path, create_if_not_exist=create_if_not_exist)

    if _default_pm is None:
        _default_pm = PackageManager()

    return _default_pm


def get_pip_manager_for_version(target_python_version: str, venv_path: str, create_if_not_exist: bool = True) -> PackageManager:
    """
    Creates a PackageManager that targets a specific Python version.

    This function checks if the requested portable Python version is available 
    locally. If not, it downloads it using the built-in native downloader.

    It then creates or uses a virtual environment at 'venv_path' using that
    specific Python executable.

    Args:
        target_python_version (str): The Python version to use (e.g., "3.10", "3.12").
        venv_path (str): The path where the virtual environment should be created.
        create_if_not_exist (bool, optional): If True, creates the virtual environment
            if it doesn't exist. Defaults to True since this factory is typically
            used for environment creation.

    Returns:
        PackageManager: A manager instance for the requested Python environment.

    Raises:
        RuntimeError: If the Python version cannot be found or installed.
    """
    pvm = PythonVersionManager()

    python_exe = pvm.get_executable_path(target_python_version, auto_install=True)

    if not python_exe:
        raise RuntimeError(f"Could not find or install portable Python version {target_python_version}.")

    logger.info(f"Using portable Python {target_python_version} at: {python_exe}")

    return PackageManager(python_executable=python_exe, venv_path=venv_path, create_if_not_exist=create_if_not_exist)


def get_uv_manager(environment_path: Optional[str] = None) -> UvPackageManager:
    """
    Gets a UV Package Manager instance.

    Args:
        environment_path (str, optional): The path to the uv virtual environment
            to be managed.

    Returns:
        UvPackageManager: An instance configured for the specified environment.
    """
    return UvPackageManager(environment_path=environment_path)


def get_conda_manager(environment_name_or_path: Optional[str] = None) -> Any:
    """Gets a Conda Package Manager instance (Not Implemented)."""
    logger.warning("get_conda_manager is not yet implemented.")
    raise NotImplementedError("Conda backend support is not yet implemented.")


def remove_venv(venv_path: str) -> bool:
    """
    Safely removes a virtual environment directory.
    
    Checks for the existence of 'pyvenv.cfg' to ensure the target is likely
    a virtual environment before deletion.

    Args:
        venv_path (str): The path to the virtual environment directory.

    Returns:
        bool: True if removed successfully or didn't exist, False on failure or safety check.
    """
    import shutil
    path = Path(venv_path).resolve()
    
    if not path.exists():
        logger.info(f"Virtual environment not found at {path}, nothing to remove.")
        return True
    
    if not (path / "pyvenv.cfg").exists():
        logger.warning(
            f"Safety check failed: '{path}' does not contain 'pyvenv.cfg'. "
            "Aborting deletion to prevent accidental data loss."
        )
        return False

    try:
        shutil.rmtree(path)
        logger.info(f"Virtual environment at {path} successfully removed.")
        return True
    except Exception as e:
        logger.error(f"Failed to remove virtual environment at {path}: {e}")
        return False
