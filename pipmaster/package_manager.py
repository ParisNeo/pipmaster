# -*- coding: utf-8 -*-
"""
Synchronous Package Manager using pip.

Provides a class and functions to interact with pip for package management
within the current environment or a specified Python environment.

Author: ParisNeo
Created: 01/04/2024
Last Updated: 23/04/2025
"""

import subprocess
import sys
from pathlib import Path
import importlib.metadata
from packaging.version import parse as parse_version
from packaging.requirements import Requirement
import ascii_colors as logging
import platform
import shutil
import shlex
from typing import Optional, List, Tuple, Union, Dict, Any

import os
import locale


# Setup basic logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PackageManager:
    """
    Manages Python package installations and queries using pip.

    Allows targeting different Python environments via the `python_executable` parameter.
    """

    def __init__(
        self,
        python_executable: Optional[str] = None,
        pip_command_base: Optional[List[str]] = None,
        venv_path: Optional[str] = None,
    ):
        """
        Initializes the PackageManager.

        Args:
            python_executable (str, optional): Path to the Python executable
                to use (default: sys.executable).
            pip_command_base (List[str], optional): Override the base command
                list (e.g., ['/custom/python', '-m', 'pip']). Overrides python_executable.
            venv_path (str, optional): Path to a virtual environment. If provided,
                will use its Python executable. If missing, creates the venv
                using python_executable (if provided) or sys.executable.
        """
        self._executable = None

        # 1. priorité à pip_command_base
        if pip_command_base:
            self.pip_command_base = pip_command_base
            logger.info(f"Using custom pip command base: {' '.join(pip_command_base)}")
            self._executable = pip_command_base[0]

        # 2. sinon priorité au venv_path
        elif venv_path:
            venv_path = Path(venv_path).resolve()
            if os.name == "nt":
                venv_python = venv_path / "Scripts" / "python.exe"
            else:
                venv_python = venv_path / "bin" / "python"

            # créer si manquant
            if not venv_python.exists():
                base_python = python_executable or sys.executable
                logger.info(
                    f"Virtual environment not found at {venv_path}, creating it with {base_python}..."
                )
                venv_path.parent.mkdir(parents=True, exist_ok=True)
                subprocess.run([base_python, "-m", "venv", str(venv_path)], check=True)
                logger.info(f"Virtual environment created at {venv_path}")

            if not venv_python.exists():
                raise RuntimeError(f"Failed to create or locate virtual environment at {venv_path}")

            self._executable = str(venv_python)
            self.pip_command_base = [self._executable, "-m", "pip"]
            logger.info(f"Using virtual environment Python: {self._executable}")

        # 3. fallback ancien comportement
        else:
            self._executable = python_executable or sys.executable
            quoted_executable = (
                f'"{self._executable}"'
                if " " in self._executable and not self._executable.startswith('"')
                else self._executable
            )
            self.pip_command_base = [quoted_executable, "-m", "pip"]
            logger.debug(
                f"Targeting pip associated with Python: {self._executable} "
                f"| Command base: {' '.join(self.pip_command_base)}"
            )

        self.target_python_executable = self._executable


    def _run_command(
        self,
        command: List[str],
        capture_output: bool = False,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> Tuple[bool, str]:
        full_command_list = self.pip_command_base + command
        log_command_list = [self.pip_command_base[0]] + self.pip_command_base[1:] + command
        command_str_for_log = " ".join(log_command_list)

        if dry_run:
            if command[0] in ["install", "uninstall", "download"]:
                insert_pos = next((i for i, arg in enumerate(command) if i > 0 and not arg.startswith("-")), -1)
                dry_run_command_list = (
                    self.pip_command_base + command[:insert_pos] + ["--dry-run"] + command[insert_pos:]
                    if insert_pos != -1 else self.pip_command_base + command + ["--dry-run"]
                )
                dry_run_cmd_str_for_log = " ".join([self.pip_command_base[0]] + dry_run_command_list[1:])
                logger.info(f"DRY RUN: Would execute: {dry_run_cmd_str_for_log}")
                return True, f"Dry run: Command would be '{dry_run_cmd_str_for_log}'"
            else:
                logger.info(f"DRY RUN: Would execute: {command_str_for_log}")
                return True, f"Dry run: Command would be '{command_str_for_log}'"

        logger.info(f"Executing: {command_str_for_log}")

        try:
            # Détection automatique de l’encodage système
            encoding = locale.getpreferredencoding(False)

            # Forcer UTF-8 si possible (Python >=3.7)
            env = os.environ.copy()
            env["PYTHONUTF8"] = "1"

            if capture_output:
                result = subprocess.run(
                    full_command_list,
                    check=False,
                    capture_output=True,
                    text=True,
                    encoding=encoding,
                    errors="replace",
                    env=env,
                )
            else:
                if verbose:
                    result = subprocess.run(
                        full_command_list,
                        check=False,
                        text=True,
                        encoding=encoding,
                        errors="replace",
                        env=env,
                    )
                else:
                    result = subprocess.run(
                        full_command_list,
                        check=False,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        text=True,
                        encoding=encoding,
                        errors="replace",
                        env=env,
                    )

            output = result.stdout or ""
            error_out = result.stderr or ""

            if result.returncode == 0:
                logger.info(f"Command succeeded: {command_str_for_log}")
                return True, output if capture_output else "Command executed successfully."
            else:
                error_message = f"Command failed with exit code {result.returncode}: {command_str_for_log}"
                if capture_output:
                    if output.strip():
                        error_message += f"\n--- stdout ---\n{output.strip()}"
                    if error_out.strip():
                        error_message += f"\n--- stderr ---\n{error_out.strip()}"
                else:
                    error_message += "\nCheck console output for details."
                logger.error(error_message)
                return False, error_message

        except FileNotFoundError:
            error_message = f"Error: Command execution failed. Is '{self.pip_command_base[0]}' a valid executable path?"
            logger.exception(error_message)
            return False, error_message
        except Exception as e:
            error_message = f"An unexpected error occurred while running command '{command_str_for_log}': {e}"
            logger.exception(error_message)
            return False, error_message


    # --- Core Package Methods ---

    def install(
        self,
        package: str,
        index_url: Optional[str] = None,
        force_reinstall: bool = False,
        upgrade: bool = True,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False,  # Added verbose
    ) -> bool:
        """
        Installs or upgrades a single package.

        Args:
            package (str): The package name, optionally with version specifier.
            index_url (str, optional): Custom index URL.
            force_reinstall (bool): If True, use --force-reinstall.
            upgrade (bool): If True, use --upgrade (pip default behavior).
            extra_args (List[str], optional): Additional arguments for pip.
            dry_run (bool): If True, simulate the command.
            verbose (bool): If True, show pip's output directly (if not capturing).

        Returns:
            bool: True on success or successful dry run, False otherwise.
        """
        command = ["install"]
        if upgrade:
            command.append("--upgrade")
        if force_reinstall:
            command.append("--force-reinstall")
        if index_url:
            command.extend(["--index-url", index_url])
        if extra_args:
            command.extend(extra_args)
        command.append(package)  # Append package last
        success, _ = self._run_command(
            command, dry_run=dry_run, verbose=verbose, capture_output=False
        )
        return success

    def _check_if_install_is_needed(
        self, package: str, version_specifier: Optional[str], always_update: bool
    ) -> Tuple[bool, str, bool]:
        """
        Internal helper to determine if a package needs to be installed or updated.
        Returns: (needs_install, install_target, force_reinstall)
        """
        try:
            req = Requirement(package)
            pkg_name = req.name
            effective_specifier = version_specifier or str(req.specifier) or None
        except ValueError:
            pkg_name = package
            effective_specifier = version_specifier

        is_installed_flag = self.is_installed(pkg_name)
        install_target = package if 'req' in locals() and req.specifier else f"{pkg_name}{effective_specifier or ''}"
        force_reinstall = False

        if not is_installed_flag:
            logger.info(f"Package '{pkg_name}' not found. Installing...")
            return True, install_target, force_reinstall

        installed_version_str = self.get_installed_version(pkg_name)
        logger.info(f"Package '{pkg_name}' is already installed (version {installed_version_str}).")

        if effective_specifier and not self.is_version_compatible(pkg_name, effective_specifier):
            logger.warning(
                f"Installed version {installed_version_str} of '{pkg_name}' does not meet specifier "
                f"'{effective_specifier}'. Needs update/reinstall."
            )
            force_reinstall = True
            return True, install_target, force_reinstall

        if always_update:
            logger.info(f"Flag 'always_update=True' set. Checking for updates for '{pkg_name}'.")
            return True, install_target, force_reinstall

        logger.info(f"'{pkg_name}' is installed and meets requirements. No action needed.")
        return False, install_target, force_reinstall

    def install_if_missing(
        self,
        package: str,
        version: Optional[str] = None,
        enforce_version: bool = False,
        always_update: bool = False,
        index_url: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
        version_specifier: Optional[str] = None,
        dry_run: bool = False,
        verbose: bool = False,  # Added verbose
    ) -> bool:
        """
        Installs a package conditionally based on presence and version requirements.

        Args:
            package (str): Name of the package (e.g., "numpy"). Can include specifier.
            version (str, optional): DEPRECATED. Use version_specifier.
            enforce_version (bool): DEPRECATED. Use version_specifier="==x.y.z".
            always_update (bool): If True and package is installed, update to latest.
            index_url (str, optional): Custom index URL for pip.
            extra_args (List[str], optional): Additional arguments for pip.
            version_specifier (str, optional): A PEP 440 specifier (e.g., ">=1.2", "==1.3.4").
                                              Takes precedence over `version`/`enforce_version`.
            dry_run (bool): If True, simulate the command.
            verbose (bool): If True, show pip's output directly (if not capturing).

        Returns:
            bool: True if installation was successful, not needed, or dry run ok. False otherwise.
        """
        try:
            req = Requirement(package)
            pkg_name = req.name
            effective_specifier = version_specifier or str(req.specifier) or None
        except ValueError:
            pkg_name = package
            effective_specifier = version_specifier

        if effective_specifier is None and enforce_version and version:
            logger.warning(
                "Using deprecated 'version' and 'enforce_version'. Prefer 'version_specifier=\"==%s\"'.",
                version,
            )
            effective_specifier = f"=={version}"
        elif effective_specifier is None and version and not enforce_version:
            logger.warning(
                "Using deprecated 'version' without 'enforce_version'. Interpreting as '>={%s}'. Prefer 'version_specifier=\">=%s\"'.",
                version,
                version,
            )
            effective_specifier = f">={version}"

        is_installed_flag = self.is_installed(pkg_name)

        if is_installed_flag:
            installed_version_str = self.get_installed_version(pkg_name)
            logger.info(
                f"Package '{pkg_name}' is already installed (version {installed_version_str})."
            )
            needs_install = False
            if effective_specifier and not self.is_version_compatible(
                pkg_name, effective_specifier
            ):
                logger.warning(
                    f"Installed version {installed_version_str} of '{pkg_name}' does not meet specifier '{effective_specifier}'. Needs update/reinstall."
                )
                needs_install = True
            elif always_update:
                logger.info(
                    f"Flag 'always_update=True' set. Checking for updates for '{pkg_name}'."
                )
                needs_install = True
            if not needs_install:
                logger.info(
                    f"'{pkg_name}' is installed and meets requirements. No action needed."
                )
                return True
            install_target = (
                package if req.specifier else f"{pkg_name}{effective_specifier or ''}"
            )
            logger.info(
                f"Attempting to install/update '{pkg_name}' to satisfy '{install_target}'..."
            )
            force = needs_install and effective_specifier is not None
            return self.install(
                install_target,
                index_url=index_url,
                upgrade=True,
                force_reinstall=force,
                extra_args=extra_args,
                dry_run=dry_run,
                verbose=verbose,
            )
        else:
            logger.info(f"Package '{pkg_name}' not found. Installing...")
            install_target = (
                package
                if "req" in locals() and req.specifier
                else f"{pkg_name}{effective_specifier or ''}"
            )  # Handle case where req parsing failed
            return self.install(
                install_target,
                index_url=index_url,
                upgrade=always_update,
                force_reinstall=False,
                extra_args=extra_args,
                dry_run=dry_run,
                verbose=verbose,
            )

    def install_multiple(
        self,
        packages: List[str],
        index_url: Optional[str] = None,
        force_reinstall: bool = False,
        upgrade: bool = True,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False,  # Added verbose
    ) -> bool:
        """Installs or upgrades multiple packages."""
        if not packages:
            logger.info("No packages provided to install_multiple.")
            return True
        command = ["install"]
        if upgrade:
            command.append("--upgrade")
        if force_reinstall:
            command.append("--force-reinstall")
        if index_url:
            command.extend(["--index-url", index_url])
        if extra_args:
            command.extend(extra_args)
        command.extend(list(packages))  # Add packages at the end
        success, _ = self._run_command(
            command, dry_run=dry_run, verbose=verbose, capture_output=not verbose
        )
        return success

    def install_multiple_if_not_installed(
        self,
        packages: List[str],
        index_url: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False,  # Added verbose
    ) -> bool:
        """
        Installs multiple packages only if they are not already installed.
        Does *not* check version compatibility, only presence. Use ensure_packages for that.
        """
        if not packages:
            logger.info("No packages provided to install_multiple_if_not_installed.")
            return True

        packages_to_install = []
        for pkg_input in packages:
            try:
                req = Requirement(pkg_input)
                pkg_name = req.name
            except ValueError:
                pkg_name = pkg_input  # Assume simple name if parsing fails

            if not self.is_installed(pkg_name):
                logger.info(
                    f"Package '{pkg_name}' (from '{pkg_input}') marked for installation."
                )
                packages_to_install.append(pkg_input)  # Use original string
            else:
                if verbose:
                    logger.info(f"Package '{pkg_name}' is already installed. Skipping.")

        if not packages_to_install:
            logger.info("All specified packages are already installed.")
            return True

        logger.info(
            f"Attempting to install missing packages: {', '.join(packages_to_install)}"
        )
        return self.install_multiple(
            packages_to_install,
            index_url=index_url,
            upgrade=False,
            force_reinstall=False,
            extra_args=extra_args,
            dry_run=dry_run,
            verbose=verbose,
        )

    def install_version(
        self,
        package: str,
        version: str,
        index_url: Optional[str] = None,
        force_reinstall: bool = False,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> bool:
        """Installs a specific version of a package."""
        install_target = f"{package}=={version}"
        command = ["install", install_target]
        if force_reinstall:
            command.append("--force-reinstall")
        if index_url:
            command.extend(["--index-url", index_url])
        if extra_args:
            command.extend(extra_args)
        success, _ = self._run_command(command, dry_run=dry_run)
        return success

    # --- Verification Methods ---

    def is_installed(
        self, package_name: str, version_specifier: Optional[str] = None
    ) -> bool:
        """
        Checks if a package is installed, optionally checking version compatibility.

        Args:
            package_name (str): The name of the package (without specifier).
            version_specifier (str, optional): A PEP 440 specifier (e.g., ">=1.2").
                                              If provided, checks version compatibility.

        Returns:
            bool: True if installed (and meets specifier if provided), False otherwise.
        """
        try:
            dist = importlib.metadata.distribution(package_name)
            if version_specifier:
                return self.is_version_compatible(
                    package_name, version_specifier, _dist=dist
                )
            return True  # Installed, no version check needed
        except importlib.metadata.PackageNotFoundError:
            return False

    def get_installed_version(self, package_name: str) -> Optional[str]:
        """Gets the installed version of a package using importlib.metadata."""
        try:
            return importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError:
            return None

    def get_current_package_version(self, package_name: str) -> Optional[str]:
        """
        Gets the installed version of a package. Alias for get_installed_version.

        This method provides a more explicit name for querying the version of a package
        that is currently installed in the target environment.

        Args:
            package_name (str): The name of the package.

        Returns:
            Optional[str]: The installed version string or None if the package is not found.
        """
        return self.get_installed_version(package_name)

    def is_version_compatible(
        self,
        package_name: str,
        version_specifier: str,
        _dist: Optional[importlib.metadata.Distribution] = None,  # Internal optimization
    ) -> bool:
        """
        Checks if the installed version of a package meets a version specifier.

        Args:
            package_name (str): The name of the package.
            version_specifier (str): A PEP 440 version specifier string (e.g., ">=1.0").
            _dist (Distribution, optional): Pre-fetched distribution object.

        Returns:
            bool: True if installed and meets specifier, False otherwise.
        """
        try:
            # Avoid redundant lookup if Distribution object is passed
            installed_version_str = (
                _dist.version if _dist else self.get_installed_version(package_name)
            )
            if not installed_version_str:
                return False  # Not installed

            # Use packaging.specifiers which is more direct than Requirement parsing trick
            req = Requirement(
                f"dummy{version_specifier}"
            )  # Parse specifier
            return req.specifier.contains(installed_version_str, prereleases=True)

        except importlib.metadata.PackageNotFoundError:
            return False  # Not installed
        except ValueError as e:
            logger.error(
                f"Error parsing version or specifier for package {package_name} ('{version_specifier}'): {e}"
            )
            return False

    def get_package_info(self, package_name: str) -> Optional[str]:
        """Runs `pip show` to get package details."""
        success, output = self._run_command(
            ["show", package_name], capture_output=True
        )
        return output if success else None

    # --- Update / Uninstall Methods ---

    def install_or_update(
        self,
        package: str,
        index_url: Optional[str] = None,
        force_reinstall: bool = False,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose = False,  # Added verbose
    ) -> bool:
        """Installs a package if missing, or updates it if installed."""
        logger.info(f"Ensuring package '{package}' is installed and up-to-date.")
        # install handles the upgrade logic correctly
        return self.install(
            package,
            index_url=index_url,
            force_reinstall=force_reinstall,
            upgrade=True,
            extra_args=extra_args,
            dry_run=dry_run,
            verbose=verbose,
        )

    def uninstall(
        self,
        package: str,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> bool:
        """Uninstalls a single package."""
        command = ["uninstall", "-y", package]
        if extra_args:
            command.extend(extra_args)
        success, _ = self._run_command(
            command, dry_run=dry_run, verbose=verbose, capture_output=False
        )  # Usually don't capture uninstall output unless error
        return success

    def uninstall_multiple(
        self,
        packages: List[str],
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> bool:
        """Uninstalls multiple packages."""
        if not packages:
            logger.info("No packages provided to uninstall_multiple.")
            return True
        command = ["uninstall", "-y"] + list(packages)
        if extra_args:
            command.extend(extra_args)
        success, _ = self._run_command(
            command, dry_run=dry_run, verbose=verbose, capture_output=False
        )
        return success

    def install_or_update_multiple(
        self,
        packages: List[str],
        index_url: Optional[str] = None,
        force_reinstall: bool = False,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> bool:
        """Installs or updates multiple packages."""
        logger.info(
            f"Ensuring packages are installed and up-to-date: {', '.join(packages)}"
        )
        # install_multiple handles the upgrade logic
        return self.install_multiple(
            packages,
            index_url=index_url,
            force_reinstall=force_reinstall,
            upgrade=True,
            extra_args=extra_args,
            dry_run=dry_run,
        )

    # --- Other Utilities ---
    def install_edit(
        self,
        path: str,
        index_url: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> bool:
        """Installs a package in editable mode."""
        command = ["install", "-e", path]
        if index_url:
            command.extend(["--index-url", index_url])
        if extra_args:
            command.extend(extra_args)
        success, _ = self._run_command(command, dry_run=dry_run)
        return success

    def install_requirements(
        self,
        requirements_file: str,
        index_url: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> bool:
        """Installs packages from a requirements file."""
        command = ["install", "-r", requirements_file]
        if index_url:
            command.extend(["--index-url", index_url])
        if extra_args:
            command.extend(extra_args)
        success, _ = self._run_command(command, dry_run=dry_run)
        return success

    def check_vulnerabilities(
        self,
        package_name: Optional[str] = None,
        requirements_file: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
    ) -> Tuple[bool, str]:
        """
        Checks for vulnerabilities using pip-audit. Requires 'pip-audit' to be installed.

        Checks the current environment targeted by this PackageManager instance.
        Provide EITHER package_name OR requirements_file to check specific targets,
        otherwise the whole environment is checked.

        Args:
            package_name (str, optional): Check a specific package.
            requirements_file (str, optional): Check dependencies in a requirements file.
            extra_args (List[str], optional): Additional arguments for pip-audit.

        Returns:
            Tuple[bool, str]: (vulnerabilities_found, audit_output_or_error)
                              Note: vulnerabilities_found is True if pip-audit finds issues.
        """
        pip_audit_exe = shutil.which("pip-audit")
        if not pip_audit_exe:
            logger.error(
                "pip-audit command not found. Please install it (`pip install pip-audit` or `pip install pipmaster[audit]`)"
            )
            return True, "pip-audit not found."  # Assume vulnerable if tool missing

        command = [pip_audit_exe]
        if package_name:
            # pip-audit doesn't directly check a single *installed* package easily.
            # A workaround is needed, e.g., creating a temp req file.
            # For now, let's support file or full env check primarily.
            logger.warning(
                "Checking single package vulnerability via pip-audit is not directly supported yet. Checking full environment."
            )
            # To implement later: create temp file with "package_name==version", run audit -r tempfile
            pass  # Fall through to check full environment
        elif requirements_file:
            command.extend(["-r", requirements_file])

        if extra_args:
            command.extend(extra_args)

        # Construct the command using the *system* pip-audit, not the target python's pip module
        audit_command_str = " ".join(command)
        logger.info(f"Running vulnerability check: {audit_command_str}")

        try:
            result = subprocess.run(
                audit_command_str,
                shell=True,
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            # pip-audit exit codes: 0 = no vulns, 1 = vulns found, >1 = error
            if result.returncode == 0:
                logger.info("pip-audit: No vulnerabilities found.")
                return False, result.stdout  # No vulns found = False
            elif result.returncode == 1:
                logger.warning(
                    f"pip-audit: Vulnerabilities found!\n{result.stdout}\n{result.stderr}"
                )
                return (
                    True,
                    f"Vulnerabilities found:\n{result.stdout}\n{result.stderr}",
                )  # Vulns found = True
            else:
                logger.error(
                    f"pip-audit command failed (exit code {result.returncode}): {audit_command_str}\n{result.stderr}"
                )
                return True, f"pip-audit error:\n{result.stderr}"  # Assume vulnerable on error
        except Exception as e:
            logger.exception(f"Failed to run pip-audit: {e}")
            return True, f"Error running pip-audit: {e}"  # Assume vulnerable on error

    def _get_packages_to_process(self, requirements: Union[str, Dict[str, Optional[str]], List[str]], verbose: bool) -> List[str]:
        """
        Parses requirements and checks which packages need installation/update.
        Internal helper for ensure_packages and async_ensure_packages.
        """
        if not requirements:
            return []

        if isinstance(requirements, str):
            requirements = [requirements]

        packages_to_process: List[str] = []
        processed_packages = set()

        if verbose:
            logger.info("--- Checking Package Requirements ---")

        items_to_check = []
        is_dict_input = False
        if isinstance(requirements, dict):
            items_to_check = list(requirements.items())
            is_dict_input = True
        elif isinstance(requirements, list):
            items_to_check = requirements
        else:
            logger.error(
                f"Invalid requirements type: {type(requirements)}. Must be dict or list."
            )
            return []

        for item in items_to_check:
            package_name: str = ""
            effective_specifier: Optional[str] = None
            install_target_string: str = ""

            try:
                if is_dict_input:
                    package_name, effective_specifier = item
                    req_check = Requirement(package_name)
                    if str(req_check.specifier):
                        logger.warning(
                            f"Specifier found in dictionary key '{package_name}'. It should be in the value. Using specifier from value: '{effective_specifier}'."
                        )
                    package_name = req_check.name
                    install_target_string = f"{package_name}{effective_specifier or ''}"
                else:
                    package_input_str = item
                    req = Requirement(package_input_str)
                    package_name = req.name
                    effective_specifier = str(req.specifier) or None
                    install_target_string = package_input_str

                if not is_dict_input and package_name in processed_packages:
                    continue
                processed_packages.add(package_name)

                specifier_str = (
                    f" (requires '{effective_specifier}')" if effective_specifier else ""
                )
                if verbose:
                    logger.info(f"Checking requirement: '{package_name}'{specifier_str}")

                if self.is_installed(
                    package_name, version_specifier=effective_specifier
                ):
                    if verbose:
                        logger.info(f"Requirement met for '{package_name}'{specifier_str}.")
                else:
                    installed_version = self.get_installed_version(package_name)
                    if installed_version:
                        logger.warning(
                            f"Requirement NOT met for '{package_name}'. Installed: {installed_version}, Required: '{effective_specifier or 'latest'}'. Adding to update list."
                        )
                    else:
                        logger.warning(
                            f"Requirement NOT met for '{package_name}'. Package not installed. Adding to install list."
                        )
                    packages_to_process.append(install_target_string)

            except ValueError as e:
                logger.error(f"Invalid package/requirement string '{item}': {e}")
                continue
            except Exception as e:
                logger.error(f"Error checking requirement for '{package_name or item}': {e}")
                if install_target_string:
                    packages_to_process.append(install_target_string)
        
        return packages_to_process

    def ensure_packages(
        self,
        requirements: Union[str, Dict[str, Optional[str]], List[str]], # Updated hint
        index_url: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> bool:
        """
        Ensures that required packages are installed and meet version requirements.

        This is the most efficient method for managing a set of dependencies, as it
        checks all requirements first and then performs a single 'pip install'
        command for only those packages that need to be installed or updated.

        Args:
            requirements (Union[str, Dict[str, Optional[str]], List[str]]):
                - str: A single package requirement string (e.g., "requests>=2.25").
                - List[str]: A list of package requirement strings.
                - Dict[str, Optional[str]]: A dictionary mapping package names to
                  optional PEP 440 version specifiers.
            index_url (str, optional): Custom index URL for installations.
            extra_args (List[str], optional): Additional arguments for the pip install command.
            dry_run (bool): If True, simulate installations without making changes.
            verbose (bool): If True, show pip's output directly during installation.

        Returns:
            bool: True if all requirements were met initially or successfully
                  resolved/installed/updated, False if any installation failed.
        """
        if not isinstance(requirements, (str, dict, list)):
            logger.error(
                f"Invalid requirements type: {type(requirements)}. Must be str, dict, or list."
            )
            return False
            
        if not requirements:
            logger.info("ensure_packages called with empty requirements.")
            return True

        packages_to_process = self._get_packages_to_process(requirements, verbose)

        if not packages_to_process:
            logger.debug("[success]All specified package requirements are already met.[/success]")
            return True

        # If we need to install/update packages
        package_list_str = "', '".join(packages_to_process)
        logger.info(
            f"Found {len(packages_to_process)} packages requiring installation/update: '{package_list_str}'"
        )
        if dry_run:
            logger.info("Dry run enabled. Simulating installation...")
        else:
            logger.info("Running installation/update command...")

        # Use install_multiple to handle the batch installation efficiently
        success = self.install_multiple(
            packages=packages_to_process,
            index_url=index_url,
            force_reinstall=False,
            upgrade=True,  # Important to handle version updates/latest install
            extra_args=extra_args,
            dry_run=dry_run,
            verbose=verbose,  # Pass verbose flag
        )

        if dry_run and success:
            logger.info(
                f"Dry run successful for processing requirements. No changes were made."
            )
        elif success:
            logger.info(
                "Successfully processed all required package installations/updates."
            )
        else:
            logger.error(
                "Failed to install/update one or more required packages."
            )  # Changed log level
            return False

        return True

    def ensure_requirements(
        self,
        requirements_file: str,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> bool:
        """
        Installs all packages listed in a requirements.txt file using pip's native -r option.
        """
        if not Path(requirements_file).exists():
            logger.error(f"Requirements file not found: {requirements_file}")
            return False

        command = ["install", "-r", str(requirements_file)]

        success, _ = self._run_command(
            command, dry_run=dry_run, verbose=verbose, capture_output=not verbose
        )

        if dry_run and success:
            logger.info("Dry run successful. No changes were made.")
        elif success:
            logger.info(f"Successfully processed requirements from {requirements_file}.")
        else:
            logger.error(f"Failed to install requirements from {requirements_file}.")
            return False

        return True

# --- Module-level Convenience Functions (using default PackageManager) ---
_default_pm = PackageManager()


# --- Factory function ---
def get_pip_manager(python_executable: Optional[str] = None) -> PackageManager:
    """
    Gets a PackageManager instance, potentially targeting a specific Python environment.

    Args:
        python_executable (str, optional): Path to the Python executable
            of the target environment. Defaults to sys.executable (current env).

    Returns:
        PackageManager: An instance configured for the target environment.
    """
    if python_executable:
        # Create a new instance for the specific environment
        return PackageManager(python_executable=python_executable)
    # Return the cached default instance for the current environment
    return _default_pm


# --- Wrapped Methods ---


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

    Args:
        package (str): The package name, optionally with version specifier.
        index_url (str, optional): Custom index URL.
        force_reinstall (bool): If True, use --force-reinstall.
        upgrade (bool): If True, use --upgrade (pip default behavior).
        extra_args (List[str], optional): Additional arguments for pip.
        dry_run (bool): If True, simulate the command.
        verbose (bool): If True, shows pip's output directly (if not capturing).

    Returns:
        bool: True on success or successful dry run, False otherwise.

    (Delegates to PackageManager.install)
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
    version: Optional[str] = None,
    enforce_version: bool = False,
    always_update: bool = False,
    index_url: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    version_specifier: Optional[str] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> bool:
    """
    Installs a package conditionally using the default PackageManager.

    Args:
        package (str): Name of the package (e.g., "numpy"). Can include specifier.
        version (str, optional): DEPRECATED. Use version_specifier.
        enforce_version (bool): DEPRECATED. Use version_specifier="==x.y.z".
        always_update (bool): If True and package is installed, update to latest.
        index_url (str, optional): Custom index URL for pip.
        extra_args (List[str], optional): Additional arguments for pip.
        version_specifier (str, optional): A PEP 440 specifier (e.g., ">=1.2", "==1.3.4").
        dry_run (bool): If True, simulate the command.
        verbose (bool): If True, shows pip's output directly (if not capturing).

    Returns:
        bool: True if installation was successful, not needed, or dry run ok. False otherwise.

    (Delegates to PackageManager.install_if_missing)
    """
    return _default_pm.install_if_missing(
        package=package,
        version=version,
        enforce_version=enforce_version,
        always_update=always_update,
        index_url=index_url,
        extra_args=extra_args,
        version_specifier=version_specifier,
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

    Args:
        path (str): Path to the local package source directory.
        index_url (str, optional): Custom index URL.
        extra_args (List[str], optional): Additional arguments for pip.
        dry_run (bool): If True, simulate the command.

    Returns:
        bool: True on success or successful dry run, False otherwise.

    (Delegates to PackageManager.install_edit)
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

    Args:
        requirements_file (str): Path to the requirements file.
        index_url (str, optional): Custom index URL.
        extra_args (List[str], optional): Additional arguments for pip.
        dry_run (bool): If True, simulate the command.

    Returns:
        bool: True on success or successful dry run, False otherwise.

    (Delegates to PackageManager.install_requirements)
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

     Args:
        packages (List[str]): A list of package names/specifiers.
        index_url (str, optional): Custom index URL.
        force_reinstall (bool): If True, use --force-reinstall.
        upgrade (bool): If True, use --upgrade.
        extra_args (List[str], optional): Additional arguments for pip.
        dry_run (bool): If True, simulate the command.
        verbose (bool): If True, show pip's output.

    Returns:
        bool: True on success or successful dry run, False otherwise.

    (Delegates to PackageManager.install_multiple)
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
    Installs multiple packages only if they are not already installed, using the default PackageManager.
    Does *not* check version compatibility, only presence.

    Args:
        packages (List[str]): A list of package names/specifiers to check/install.
        index_url (str, optional): Custom index URL for installing missing packages.
        extra_args (List[str], optional): Additional arguments for pip install command.
        dry_run (bool): If True, simulate the command for missing packages.
        verbose (bool): If true, shows information about packages being skipped.

    Returns:
        bool: True if all originally missing packages installed successfully or dry run ok, False otherwise.

    (Delegates to PackageManager.install_multiple_if_not_installed)
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

    Args:
        package (str): The name of the package.
        version (str): The exact version string to install (e.g., "1.2.3").
        index_url (str, optional): Custom index URL.
        force_reinstall (bool): If True, use --force-reinstall.
        extra_args (List[str], optional): Additional arguments for pip.
        dry_run (bool): If True, simulate the command.

    Returns:
        bool: True on success or successful dry run, False otherwise.

    (Delegates to PackageManager.install_version)
    """
    return _default_pm.install_version(
        package=package,
        version=version,
        index_url=index_url,
        force_reinstall=force_reinstall,
        extra_args=extra_args,
        dry_run=dry_run,
    )


def is_installed(
    package_name: str, version_specifier: Optional[str] = None
) -> bool:
    """
    Checks if a package is installed in the current environment, optionally checking version.

    Args:
        package_name (str): The name of the package (without specifier).
        version_specifier (str, optional): A PEP 440 specifier (e.g., ">=1.2").

    Returns:
        bool: True if installed (and meets specifier if provided), False otherwise.

    (Delegates to PackageManager.is_installed)
    """
    return _default_pm.is_installed(
        package_name=package_name, version_specifier=version_specifier
    )


def get_installed_version(package_name: str) -> Optional[str]:
    """
    Gets the installed version of a package in the current environment.

    Args:
        package_name (str): The name of the package.

    Returns:
        Optional[str]: The installed version string or None if not found.

    (Delegates to PackageManager.get_installed_version)
    """
    return _default_pm.get_installed_version(package_name=package_name)


def get_current_package_version(package_name: str) -> Optional[str]:
    """
    Gets the installed version of a package in the current environment. Alias for get_installed_version.

    Args:
        package_name (str): The name of the package.

    Returns:
        Optional[str]: The installed version string or None if not found.

    (Delegates to PackageManager.get_current_package_version)
    """
    return _default_pm.get_current_package_version(package_name=package_name)


def is_version_compatible(
    package_name: str,
    version_specifier: str,
) -> bool:
    """
    Checks if the installed version in the current environment meets a version specifier.

    Args:
        package_name (str): The name of the package.
        version_specifier (str): A PEP 440 version specifier string (e.g., ">=1.0").

    Returns:
        bool: True if installed and meets specifier, False otherwise.

    (Delegates to PackageManager.is_version_compatible)
    """
    return _default_pm.is_version_compatible(
        package_name=package_name, version_specifier=version_specifier
    )


def get_package_info(package_name: str) -> Optional[str]:
    """
    Runs `pip show` for a package in the current environment.

    Args:
        package_name (str): The name of the package.

    Returns:
        Optional[str]: The output of `pip show` or None on error.

    (Delegates to PackageManager.get_package_info)
    """
    return _default_pm.get_package_info(package_name=package_name)


def install_or_update(
    package: str,
    index_url: Optional[str] = None,
    force_reinstall: bool = False,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
    verbose: bool = False,
) -> bool:
    """
    Installs a package if missing, or updates it if installed, using the default PackageManager.

    Args:
        package (str): The package name, optionally with version specifier.
        index_url (str, optional): Custom index URL.
        force_reinstall (bool): If True, use --force-reinstall during update/install.
        extra_args (List[str], optional): Additional arguments for pip.
        dry_run (bool): If True, simulate the command.
        verbose (bool): If True, shows pip's output.

    Returns:
        bool: True on success or successful dry run, False otherwise.

    (Delegates to PackageManager.install_or_update)
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

    Args:
        package (str): The name of the package to uninstall.
        extra_args (List[str], optional): Additional arguments for pip uninstall.
        dry_run (bool): If True, simulate the command.
        verbose (bool): If True, show pip's output.

    Returns:
        bool: True on success or successful dry run, False otherwise.

    (Delegates to PackageManager.uninstall)
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

    Args:
        packages (List[str]): A list of package names to uninstall.
        extra_args (List[str], optional): Additional arguments for pip uninstall.
        dry_run (bool): If True, simulate the command.
        verbose (bool): If True, show pip's output.

    Returns:
        bool: True on success or successful dry run, False otherwise.

    (Delegates to PackageManager.uninstall_multiple)
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

    Args:
        packages (List[str]): A list of package names/specifiers.
        index_url (str, optional): Custom index URL.
        force_reinstall (bool): If True, use --force-reinstall.
        extra_args (List[str], optional): Additional arguments for pip.
        dry_run (bool): If True, simulate the command.
        verbose (bool): If True, show pip's output.

    Returns:
        bool: True on success or successful dry run, False otherwise.

    (Delegates to PackageManager.install_or_update_multiple)
    """
    return _default_pm.install_or_update_multiple(
        packages=packages,
        index_url=index_url,
        force_reinstall=force_reinstall,
        extra_args=extra_args,
        dry_run=dry_run,
        verbose=verbose,
    )


def check_vulnerabilities(
    package_name: Optional[str] = None,
    requirements_file: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
) -> Tuple[bool, str]:
    """
    Checks for vulnerabilities in the current environment using pip-audit.

    Requires 'pip-audit' to be installed (e.g., `pip install pipmaster[audit]`).
    Provide EITHER package_name OR requirements_file for specific checks,
    otherwise the whole environment is checked.

    Args:
        package_name (str, optional): Check a specific package (support limited).
        requirements_file (str, optional): Check dependencies in a requirements file.
        extra_args (List[str], optional): Additional arguments for pip-audit.

    Returns:
        Tuple[bool, str]: (vulnerabilities_found, audit_output_or_error)

    (Delegates to PackageManager.check_vulnerabilities)
    """
    return _default_pm.check_vulnerabilities(
        package_name=package_name,
        requirements_file=requirements_file,
        extra_args=extra_args,
    )


def ensure_packages(
    requirements: Union[str, Dict[str, Optional[str]], List[str]],  # Updated hint
    index_url: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
    verbose: bool = False,  # Added verbose
) -> bool:
    """
    Ensures packages meet requirements in the current environment using the default PackageManager.

    Checks each requirement from the dictionary or list. Installs or updates
    packages efficiently in a single batch if needed.

    Args:
        requirements (Union[str, Dict[str, Optional[str]], List[str]]):
            Either a string (the package name), a dictionary mapping package names to optional PEP 440 version
            specifiers (e.g., {"requests": ">=2.25", "numpy": None}) OR a list
            of package strings (e.g., ["requests>=2.25", "numpy"]). If a list
            item has no specifier, the latest version is assumed.
        index_url (str, optional): Custom index URL for installations.
        extra_args (List[str], optional): Additional arguments for the pip install command.
        dry_run (bool): If True, simulate installations without making changes.
        verbose (bool): If True, show pip's output directly during installation.

    Returns:
        bool: True if all requirements were met initially or successfully resolved,
              False if any installation failed.

    (Delegates to PackageManager.ensure_packages)
    """
    return _default_pm.ensure_packages(
        requirements=requirements,
        index_url=index_url,
        extra_args=extra_args,
        dry_run=dry_run,
        verbose=verbose,  # Pass verbose
    )

def ensure_requirements(
    requirements_file: str,
    dry_run: bool = False,
    verbose: bool = False,
) -> bool:
    """
    Ensures that all packages from a requirements.txt file are installed.

    This method parses a requirements file, respecting comments and some pip
    options like --index-url or --extra-index-url, and then uses the efficient
    `ensure_packages` method to install any missing or outdated packages.

    Note: Does not support recursive '-r' includes or editable '-e' installs from
    within the file. For editable installs, use `install_edit()`.

    Args:
        requirements_file (str): Path to the requirements.txt file.
        dry_run (bool): If True, simulate installations without making changes.
        verbose (bool): If True, show detailed output during checks and installation.

    Returns:
        bool: True if all requirements were met or successfully installed, False otherwise.
    
    (Delegates to PackageManager.ensure_requirements)
    """
    return _default_pm.ensure_requirements(
        requirements_file=requirements_file,
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


# --- UV / Conda Backends ---
# In pipmaster/package_manager.py

class UvPackageManager:
    """
    Manages Python environments and packages using uv.
    Requires the 'uv' executable to be in the system's PATH.
    """

    def __init__(self, environment_path: Optional[str] = None):
        """
        Initializes the UvPackageManager.

        Args:
            environment_path (str, optional): The path to the uv virtual environment.
                If not provided, some methods like install/uninstall will fail until an
                environment is created and targeted.
        """
        self.uv_executable = shutil.which("uv")
        if not self.uv_executable:
            raise FileNotFoundError(
                "The 'uv' executable was not found in your system's PATH. Please install uv first."
            )

        self.environment_path: Optional[str] = environment_path
        self.python_executable: Optional[str] = None

        if self.environment_path:
            if platform.system() == "Windows":
                py_path = f"{self.environment_path}\\Scripts\\python.exe"
            else:
                py_path = f"{self.environment_path}/bin/python"
            self.python_executable = py_path
            logger.info(
                f"UvPackageManager targeting environment: {self.environment_path}"
            )
        else:
            logger.info("UvPackageManager initialized without a specific environment.")

    def _run_command(
        self, command: List[str], capture_output: bool = False, verbose: bool = False
    ) -> Tuple[bool, str]:
        """Runs a 'uv' command using subprocess."""
        command_str_for_exec = " ".join([f'"{self.uv_executable}"'] + command)
        logger.info(f"Executing: {command_str_for_exec}")

        try:
            run_kwargs = {
                "shell": True,
                "check": False,
                "text": True,
                "encoding": "utf-8",
            }

            if capture_output:
                run_kwargs["capture_output"] = True
            else:
                if not verbose:
                    run_kwargs["stdout"] = subprocess.DEVNULL
                    run_kwargs["stderr"] = subprocess.DEVNULL
            
            result = subprocess.run(command_str_for_exec, **run_kwargs)
            
            output = result.stdout if capture_output and result.stdout else ""

            if result.returncode == 0:
                logger.info(f"uv command succeeded: {command_str_for_exec}")
                return True, output if capture_output else "Command executed successfully."
            else:
                error_message = (
                    f"uv command failed with exit code {result.returncode}: {command_str_for_exec}"
                )
                if 'capture_output' in run_kwargs and run_kwargs.get('capture_output'):
                    if result.stdout:
                        error_message += f"\n--- stdout ---\n{result.stdout.strip()}"
                    if result.stderr:
                        error_message += f"\n--- stderr ---\n{result.stderr.strip()}"
                else:
                    error_message += "\nCheck console output for details."
                
                logger.error(error_message)
                return False, error_message

        except Exception as e:
            error_message = f"An unexpected error occurred while running uv command '{command_str_for_exec}': {e}"
            logger.exception(error_message)
            return False, error_message

    def create_env(self, path: str, python_version: Optional[str] = None) -> bool:
        """Creates a new virtual environment at the specified path."""
        command = ["venv", f'"{path}"'] # Quote path for safety
        if python_version:
            command.extend(["--python", python_version])
        success, _ = self._run_command(command, verbose=True)
        if success:
            self.environment_path = path
            if platform.system() == "Windows":
                self.python_executable = f"{path}\\Scripts\\python.exe"
            else:
                self.python_executable = f"{path}/bin/python"
            logger.info(
                f"UvPackageManager is now targeting the newly created environment at {path}"
            )
        return success

    def install(
        self,
        package: str,
        extra_args: Optional[List[str]] = None,
        verbose: bool = False,
    ) -> bool:
        """Installs a package into the configured environment."""
        if not self.python_executable:
            logger.error("Cannot install package: No target environment is configured.")
            return False
        command = ["pip", "install", f'--python="{self.python_executable}"', package]
        if extra_args:
            command.extend(extra_args)
        success, _ = self._run_command(
            command, verbose=verbose, capture_output=False
        )
        return success

    def install_multiple(
        self,
        packages: List[str],
        extra_args: Optional[List[str]] = None,
        verbose: bool = False,
    ) -> bool:
        """Installs multiple packages into the configured environment."""
        if not self.python_executable:
            logger.error(
                "Cannot install packages: No target environment is configured."
            )
            return False
        if not packages:
            return True
        command = ["pip", "install", f'--python="{self.python_executable}"'] + packages
        if extra_args:
            command.extend(extra_args)
        success, _ = self._run_command(
            command, verbose=verbose, capture_output=False
        )
        return success

    def uninstall(
        self, package: str, extra_args: Optional[List[str]] = None, verbose: bool = False
    ) -> bool:
        """Uninstalls a package from the configured environment."""
        if not self.python_executable:
            logger.error(
                "Cannot uninstall package: No target environment is configured."
            )
            return False
        command = ["pip", "uninstall", f'--python="{self.python_executable}"', package]
        if extra_args:
            command.extend(extra_args)
        success, _ = self._run_command(
            command, verbose=verbose, capture_output=False
        )
        return success

    def run_with_uvx(self, command: List[str], verbose: bool = False) -> bool:
        """
        Executes a tool in a temporary environment using `uv tool run` (the long
        form of `uvx`), which is the correct command for this purpose.

        Args:
            command (List[str]): The command and its arguments. The first element
                                 is assumed to be the tool/package name.
            verbose (bool): If True, show command's output on the console.
        """
        if not command:
            logger.error("run_with_uvx requires a command to execute.")
            return False

        # ---- THE CORRECT IMPLEMENTATION BASED ON DOCUMENTATION ----
        # The syntax is `uv tool run <tool> [args...]`.
        # `command` is already in the format `<tool> [args...]`.
        uvx_command = ["tool", "run"] + command
        # ---- END OF FIX ----

        success, _ = self._run_command(
            uvx_command, verbose=verbose, capture_output=False
        )
        return success
    
class CondaPackageManager:
    def __init__(self, environment_name_or_path: Optional[str] = None):
        logger.warning("CondaPackageManager is not yet implemented.")
        raise NotImplementedError("Conda backend support is not yet implemented.")


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