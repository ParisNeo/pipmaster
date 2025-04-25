# -*- coding: utf-8 -*-
"""
pipmaster: A versatile Python package manager utility.

Author: ParisNeo
Created: 01/04/2024
Last Updated: 23/04/2025
"""

# Read version dynamically - this must be present for pyproject.toml
__version__ = "0.7.0"

# Expose the main synchronous functions
from .package_manager import (
    install,
    install_if_missing,
    install_edit,
    install_requirements,
    install_multiple,
    install_multiple_if_not_installed,
    install_version,
    is_installed,
    get_installed_version,
    is_version_compatible,
    get_package_info,
    install_or_update,
    uninstall,
    uninstall_multiple,
    install_or_update_multiple,
    check_vulnerabilities, # Added
    get_pip_manager,        # Added factory function
    ensure_packages
)

# Expose the PackageManager class
from .package_manager import PackageManager

# Deprecated functions (kept for backward compatibility)
from .package_manager import is_version_higher, is_version_exact

# Define what `import *` imports (optional but good practice)
__all__ = [
    "PackageManager",
    "install",
    "install_if_missing",
    "install_edit",
    "install_requirements",
    "install_multiple",
    "install_multiple_if_not_installed",
    "install_version",
    "is_installed",
    "get_installed_version",
    "is_version_compatible",
    "get_package_info",
    "install_or_update",
    "uninstall",
    "uninstall_multiple",
    "install_or_update_multiple",
    "check_vulnerabilities",
    "get_pip_manager",
    "ensure_packages",
    # Async counterparts
    "AsyncPackageManager",
    "async_install",
    "async_install_if_missing",
    "async_check_vulnerabilities", # Add others as implemented
    # Deprecated
    "is_version_higher",
    "is_version_exact",
    # Version
    "__version__",
]