# -*- coding: utf-8 -*-
"""
Module-level convenience functions for pipmaster.

These functions provide a simple, functional API that wraps the default
PackageManager instance. They are the primary entry point for simple use cases.

Author: ParisNeo
Created: 01/04/2024
Last Updated: 13/02/2026
"""

from typing import Optional, List, Tuple, Union, Dict, Any

from .factories import get_pip_manager
from .core import logger


# Get the default package manager instance
_default_pm = get_pip_manager()


# --- Install Functions ---

def install(
    package: str,
    index_url: Optional[str] = None,
    force_reinstall: bool = False,
    upgrade: bool = True,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> bool:
    """
    Installs or upgrades a single package using the default PackageManager.
    """
    return _default_pm.install(
        package=package,
        index_url=index_url,
        force_reinstall=force_reinstall,
        upgrade=upgrade,
        extra_args=extra_args,
        dry_run=dry_run,
        verbose=verbose,
    )


def install_if_missing(
    package: str,
    version_specifier: Optional[str] = None,
    always_update: bool = False,
    index_url: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> bool:
    """
    Installs a package conditionally using the default PackageManager.
    """
    return _default_pm.install_if_missing(
        package=package,
        version_specifier=version_specifier,
        always_update=always_update,
        index_url=index_url,
        extra_args=extra_args,
        dry_run=dry_run,
        verbose=verbose,
    )


def install_edit(
    path: str,
    index_url: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
) -> bool:
    """
    Installs a package in editable mode using the default PackageManager.
    """
    return _default_pm.install_edit(
        path=path, index_url=index_url, extra_args=extra_args, dry_run=dry_run
    )


def install_requirements(
    requirements_file: str,
    index_url: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
) -> bool:
    """
    Installs packages from a requirements file using the default PackageManager.
    """
    return _default_pm.install_requirements(
        requirements_file=requirements_file,
        index_url=index_url,
        extra_args=extra_args,
        dry_run=dry_run,
    )


def install_multiple(
    packages: List[str],
    index_url: Optional[str] = None,
    force_reinstall: bool = False,
    upgrade: bool = True,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> bool:
    """
    Installs or upgrades multiple packages using the default PackageManager.
    """
    return _default_pm.install_multiple(
        packages=packages,
        index_url=index_url,
        force_reinstall=force_reinstall,
        upgrade=upgrade,
        extra_args=extra_args,
        dry_run=dry_run,
        verbose=verbose,
    )


def install_multiple_if_not_installed(
    packages: List[str],
    index_url: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> bool:
    """
    Installs multiple packages only if they are not already installed.
    """
    return _default_pm.install_multiple_if_not_installed(
        packages=packages,
        index_url=index_url,
        extra_args=extra_args,
        dry_run=dry_run,
        verbose=verbose,
    )


def install_version(
    package: str,
    version: str,
    index_url: Optional[str] = None,
    force_reinstall: bool = False,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
) -> bool:
    """
    Installs a specific version of a package using the default PackageManager.
    """
    return _default_pm.install_version(
        package=package,
        version=version,
        index_url=index_url,
        force_reinstall=force_reinstall,
        extra_args=extra_args,
        dry_run=dry_run,
    )


# --- Query Functions ---

def is_installed(
    package_name: str, version_specifier: Optional[str] = None
) -> bool:
    """
    Checks if a package is installed in the current environment.
    """
    return _default_pm.is_installed(
        package_name=package_name, version_specifier=version_specifier
    )


def get_installed_version(package_name: str) -> Optional[str]:
    """
    Gets the installed version of a package in the current environment.
    """
    return _default_pm.get_installed_version(package_name=package_name)


def get_current_package_version(package_name: str) -> Optional[str]:
    """
    Gets the installed version of a package. Alias for get_installed_version.
    """
    return _default_pm.get_current_package_version(package_name=package_name)


def is_version_compatible(
    package_name: str,
    version_specifier: str,
) -> bool:
    """
    Checks if the installed version meets a version specifier.
    """
    return _default_pm.is_version_compatible(
        package_name=package_name, version_specifier=version_specifier
    )


def get_package_info(package_name: str) -> Optional[str]:
    """
    Runs `pip show` for a package in the current environment.
    """
    return _default_pm.get_package_info(package_name=package_name)


# --- Update/Uninstall Functions ---

def install_or_update(
    package: str,
    index_url: Optional[str] = None,
    force_reinstall: bool = False,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> bool:
    """
    Installs a package if missing, or updates it if installed.
    """
    return _default_pm.install_or_update(
        package=package,
        index_url=index_url,
        force_reinstall=force_reinstall,
        extra_args=extra_args,
        dry_run=dry_run,
        verbose=verbose,
    )


def uninstall(
    package: str,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> bool:
    """
    Uninstalls a single package from the current environment.
    """
    return _default_pm.uninstall(
        package=package, extra_args=extra_args, dry_run=dry_run, verbose=verbose
    )


def uninstall_multiple(
    packages: List[str],
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> bool:
    """
    Uninstalls multiple packages from the current environment.
    """
    return _default_pm.uninstall_multiple(
        packages=packages, extra_args=extra_args, dry_run=dry_run, verbose=verbose
    )


def install_or_update_multiple(
    packages: List[str],
    index_url: Optional[str] = None,
    force_reinstall: bool = False,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> bool:
    """
    Installs or updates multiple packages using the default PackageManager.
    """
    return _default_pm.install_or_update_multiple(
        packages=packages,
        index_url=index_url,
        force_reinstall=force_reinstall,
        extra_args=extra_args,
        dry_run=dry_run,
        verbose=verbose,
    )


# --- Security Functions ---

def check_vulnerabilities(
    package_name: Optional[str] = None,
    requirements_file: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
) -> Tuple[bool, str]:
    """
    Checks for vulnerabilities in the current environment using pip-audit.
    """
    return _default_pm.check_vulnerabilities(
        package_name=package_name,
        requirements_file=requirements_file,
        extra_args=extra_args,
    )


# --- Ensure Functions ---

def ensure_packages(
    requirements: Union[str, Dict[str, Optional[str]], List[str]],
    always_update: bool = False,
    index_url: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
    verbose: bool = False,
    progress_callback: Optional[callable] = None,
) -> bool:
    """
    Ensures packages meet requirements in the current environment.
    """
    return _default_pm.ensure_packages(
        requirements=requirements,
        always_update=always_update,
        index_url=index_url,
        extra_args=extra_args,
        dry_run=dry_run,
        verbose=verbose,
        progress_callback=progress_callback,
    )


def ensure_requirements(
    requirements_file: str,
    always_update: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
) -> bool:
    """
    Ensures that all packages from a requirements.txt file are installed.
    """
    return _default_pm.ensure_requirements(
        requirements_file=requirements_file,
        always_update=always_update,
        dry_run=dry_run,
        verbose=verbose,
    )


# --- Deprecated Functions ---

def is_version_higher(package_name: str, required_version: str) -> bool:
    """DEPRECATED: Use is_version_compatible(package, f'>={required_version}')"""
    logger.warning("is_version_higher is deprecated. Use is_version_compatible instead.")
    return _default_pm.is_version_compatible(package_name, f">={required_version}")


def is_version_exact(package_name: str, required_version: str) -> bool:
    """DEPRECATED: Use is_version_compatible(package, f'=={required_version}')"""
    logger.warning("is_version_exact is deprecated. Use is_version_compatible instead.")
    return _default_pm.is_version_compatible(package_name, f"=={required_version}")
