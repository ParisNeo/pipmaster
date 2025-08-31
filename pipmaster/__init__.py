# pipmaster/__init__.py

# -*- coding: utf-8 -*-
"""
pipmaster: A versatile Python package manager utility.

Author: ParisNeo
Created: 01/04/2024
Last Updated: 24/04/2025
"""

# Read version dynamically
__version__ = "1.0.4"

# --- Synchronous API ---
from .package_manager import (
    PackageManager,
    UvPackageManager,
    CondaPackageManager,
    get_pip_manager,
    get_uv_manager,
    get_conda_manager,
    install,
    install_if_missing,
    install_edit,
    install_requirements,
    install_multiple,
    install_multiple_if_not_installed,
    install_version,
    is_installed,
    get_installed_version,
    get_current_package_version,
    is_version_compatible,
    get_package_info,
    install_or_update,
    uninstall,
    uninstall_multiple,
    install_or_update_multiple,
    check_vulnerabilities,
    ensure_packages,
    ensure_requirements,
    is_version_higher, # Deprecated
    is_version_exact,  # Deprecated
)

# --- Asynchronous API ---
from .async_package_manager import (
    AsyncPackageManager,
    async_install,
    async_install_if_missing,
    async_ensure_packages,
    async_ensure_requirements,
    async_install_multiple,
    async_uninstall,
    async_uninstall_multiple,
    async_get_package_info,
    async_check_vulnerabilities,
)

# --- Public API Definition (`__all__`) ---
__all__ = [
    # Synchronous Classes & Factories
    "PackageManager",
    "UvPackageManager",
    "CondaPackageManager",
    "get_pip_manager",
    "get_uv_manager",
    "get_conda_manager",

    # Synchronous Core Functions
    "ensure_packages",
    "ensure_requirements",
    "install",
    "install_if_missing",
    "install_multiple",
    "uninstall",
    "uninstall_multiple",
    "is_installed",
    "get_installed_version",
    "get_current_package_version",
    "is_version_compatible",
    "check_vulnerabilities",
    "get_package_info",
    "install_edit",
    "install_requirements",
    "install_version",
    "install_or_update",
    "install_or_update_multiple",

    # Asynchronous Classes & Functions
    "AsyncPackageManager",
    "async_ensure_packages",
    "async_ensure_requirements",
    "async_install",
    "async_install_if_missing",
    "async_install_multiple",
    "async_uninstall",
    "async_uninstall_multiple",
    "async_check_vulnerabilities",
    "async_get_package_info",
    
    # Deprecated
    "is_version_higher",
    "is_version_exact",
    
    # Version
    "__version__",
]