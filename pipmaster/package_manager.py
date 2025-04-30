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
import importlib.metadata
from packaging.version import parse as parse_version
from packaging.requirements import Requirement
import ascii_colors as logging
import platform
import shutil
from typing import Optional, List, Tuple, Union, Dict, Any

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
    ):
        """
        Initializes the PackageManager.

        Args:
            python_executable (str, optional): Path to the Python executable
                of the target environment. Defaults to sys.executable (current env).
            pip_command_base (List[str], optional): Advanced: Override the base command
                list (e.g., ['/custom/python', '-m', 'pip']). Overrides python_executable.
                Use with caution.
        """
        if pip_command_base:
            self.pip_command_base = pip_command_base
            logger.info(f"Using custom pip command base: {' '.join(pip_command_base)}")
        else:
            self._executable = python_executable or sys.executable
            # Ensure executable path with spaces is quoted if detected,
            # although subprocess.run with shell=True often handles this.
            # Using a list for the command is generally safer if shell=False,
            # but shell=True is convenient here. Let's quote defensively.
            quoted_executable = (
                f'"{self._executable}"'
                if " " in self._executable and not self._executable.startswith('"')
                else self._executable
            )
            self.pip_command_base = [quoted_executable, "-m", "pip"]
            logger.info(
                f"Targeting pip associated with Python: {self._executable}"
                f" | Command base: {' '.join(self.pip_command_base)}"
            )
        self.target_python_executable = self._executable # Store for potential use

    def _run_command(
        self, command: List[str], capture_output: bool = False, dry_run: bool = False, verbose: bool = False # Added verbose
    ) -> Tuple[bool, str]:
        """
        Runs a command (typically pip) using subprocess.run.

        Args:
            command (list): The command arguments (e.g., ["install", "requests"]).
            capture_output (bool): Whether to capture stdout/stderr.
            dry_run (bool): If True, attempts to add the backend's dry-run flag.
            verbose (bool): If True and capture_output is False, shows command's
                            output directly on the console. Ignored if capture_output is True.

        Returns:
            tuple: (bool: success, str: output or error message)
        """
        full_command_list = self.pip_command_base + command
        log_command_list = [self.pip_command_base[0]] + self.pip_command_base[1:] + command
        command_str_for_log = " ".join(log_command_list)
        command_str_for_exec = " ".join(full_command_list)

        if dry_run:
            # Logic for dry run simulation (remains the same)
            # Add backend-specific dry-run flags (only pip known for now)
            if command[0] in ["install", "uninstall", "download"]:
                insert_pos = -1
                for i, arg in enumerate(command):
                     if i > 0 and not arg.startswith('-'):
                         insert_pos = i
                         break
                if insert_pos != -1:
                    dry_run_command_list = self.pip_command_base + command[:insert_pos] + ["--dry-run"] + command[insert_pos:]
                else:
                    dry_run_command_list = self.pip_command_base + command + ["--dry-run"]

                dry_run_cmd_str_for_log = " ".join([self.pip_command_base[0]] + dry_run_command_list[1:])
                logger.info(f"DRY RUN: Would execute: {dry_run_cmd_str_for_log}")
                return True, f"Dry run: Command would be '{dry_run_cmd_str_for_log}'"
            else:
                # For commands without a specific dry-run flag, just log the intended command
                logger.info(f"DRY RUN: Would execute: {command_str_for_log}")
                return True, f"Dry run: Command would be '{command_str_for_log}'"


        logger.info(f"Executing: {command_str_for_log}")
        try:
            # ---- CORRECTED SUBPROCESS CALL ----
            stdout_target = None
            stderr_target = None
            should_capture = False # Flag to know if we need to read result.stdout/stderr

            if capture_output:
                # Use capture_output=True, don't set stdout/stderr explicitly
                should_capture = True
                run_kwargs = {
                    "shell": True,
                    "check": False,
                    "capture_output": True, # Let subprocess handle PIPE creation
                    "text": True,
                    "encoding": "utf-8",
                }
            else:
                # Not capturing output, decide based on verbose flag
                if verbose:
                    stdout_target = None # Default: inherit handles (console)
                    stderr_target = None
                else: # Not capturing, not verbose -> discard
                    stdout_target = subprocess.DEVNULL
                    stderr_target = subprocess.DEVNULL

                run_kwargs = {
                    "shell": True,
                    "check": False,
                    "stdout": stdout_target,
                    "stderr": stderr_target,
                    "text": True, # Still useful even if discarding
                    "encoding": "utf-8",
                }

            result = subprocess.run(command_str_for_exec, **run_kwargs)
            # ---- END CORRECTED SUBPROCESS CALL ----


            # ---- CORRECTED OUTPUT HANDLING ----
            output = result.stdout if should_capture and result.stdout else ""
            error_out = result.stderr if should_capture and result.stderr else ""

            if result.returncode == 0:
                logger.info(f"Command succeeded: {command_str_for_log}")
                # Return captured output only if requested
                return True, output if should_capture else "Command executed successfully."
            else:
                # Error handling needs to read stdout/stderr *if they were captured*
                error_message = (
                    f"Command failed with exit code {result.returncode}: {command_str_for_log}"
                )
                # Get output/error ONLY if it was piped (i.e., should_capture was True)
                captured_stdout = result.stdout if should_capture and result.stdout else None
                captured_stderr = result.stderr if should_capture and result.stderr else None

                if captured_stdout: error_message += f"\n--- stdout ---\n{captured_stdout.strip()}"
                if captured_stderr: error_message += f"\n--- stderr ---\n{captured_stderr.strip()}"
                # If output wasn't captured but error occurred, suggest checking console
                if not should_capture: error_message += "\nCheck console output for details."

                logger.error(error_message)
                # Return the error message detail
                return False, error_message
            # ---- END CORRECTED OUTPUT HANDLING ----

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
        verbose: bool = False, # Added verbose
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
        command.append(package) # Append package last
        success, _ = self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=not verbose)
        return success

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
        verbose: bool = False, # Added verbose
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
             logger.warning("Using deprecated 'version' and 'enforce_version'. Prefer 'version_specifier=\"==%s\"'.", version)
             effective_specifier = f"=={version}"
        elif effective_specifier is None and version and not enforce_version:
             logger.warning("Using deprecated 'version' without 'enforce_version'. Interpreting as '>={%s}'. Prefer 'version_specifier=\">=%s\"'.", version, version)
             effective_specifier = f">={version}"

        is_installed_flag = self.is_installed(pkg_name)

        if is_installed_flag:
            installed_version_str = self.get_installed_version(pkg_name)
            logger.info(f"Package '{pkg_name}' is already installed (version {installed_version_str}).")
            needs_install = False
            if effective_specifier and not self.is_version_compatible(pkg_name, effective_specifier):
                logger.warning(f"Installed version {installed_version_str} of '{pkg_name}' does not meet specifier '{effective_specifier}'. Needs update/reinstall.")
                needs_install = True
            elif always_update:
                logger.info(f"Flag 'always_update=True' set. Checking for updates for '{pkg_name}'.")
                needs_install = True
            if not needs_install:
                 logger.info(f"'{pkg_name}' is installed and meets requirements. No action needed.")
                 return True
            install_target = package if req.specifier else f"{pkg_name}{effective_specifier or ''}"
            logger.info(f"Attempting to install/update '{pkg_name}' to satisfy '{install_target}'...")
            force = needs_install and effective_specifier is not None
            return self.install(
                    install_target, index_url=index_url, upgrade=True,
                    force_reinstall=force, extra_args=extra_args, dry_run=dry_run, verbose=verbose,
                )
        else:
            logger.info(f"Package '{pkg_name}' not found. Installing...")
            install_target = package if 'req' in locals() and req.specifier else f"{pkg_name}{effective_specifier or ''}" # Handle case where req parsing failed
            return self.install(
                install_target, index_url=index_url, upgrade=always_update,
                force_reinstall=False, extra_args=extra_args, dry_run=dry_run, verbose=verbose,
            )

    def install_multiple(
        self,
        packages: List[str],
        index_url: Optional[str] = None,
        force_reinstall: bool = False,
        upgrade: bool = True,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False, # Added verbose
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
        command.extend(list(packages)) # Add packages at the end
        success, _ = self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=not verbose)
        return success

    def install_multiple_if_not_installed(
        self,
        packages: List[str],
        index_url: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False, # Added verbose
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
                 pkg_name = pkg_input # Assume simple name if parsing fails

             if not self.is_installed(pkg_name):
                 logger.info(f"Package '{pkg_name}' (from '{pkg_input}') marked for installation.")
                 packages_to_install.append(pkg_input) # Use original string
             else:
                 if verbose: logger.info(f"Package '{pkg_name}' is already installed. Skipping.")

        if not packages_to_install:
            logger.info("All specified packages are already installed.")
            return True

        logger.info(f"Attempting to install missing packages: {', '.join(packages_to_install)}")
        return self.install_multiple(
            packages_to_install, index_url=index_url, upgrade=False,
            force_reinstall=False, extra_args=extra_args, dry_run=dry_run, verbose=verbose
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
                return self.is_version_compatible(package_name, version_specifier, _dist=dist)
            return True # Installed, no version check needed
        except importlib.metadata.PackageNotFoundError:
            return False

    def get_installed_version(self, package_name: str) -> Optional[str]:
        """Gets the installed version of a package using importlib.metadata."""
        try:
            return importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError:
            return None

    def is_version_compatible(
        self,
        package_name: str,
        version_specifier: str,
        _dist: Optional[importlib.metadata.Distribution] = None # Internal optimization
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
            installed_version_str = _dist.version if _dist else self.get_installed_version(package_name)
            if not installed_version_str:
                return False # Not installed

            # Use packaging.specifiers which is more direct than Requirement parsing trick
            spec = importlib.metadata.packages_distributions # Not quite right, use Requirement parser
            req = Requirement(f"dummy{version_specifier}") # Parse specifier
            return req.specifier.contains(installed_version_str, prereleases=True)

        except importlib.metadata.PackageNotFoundError:
            return False # Not installed
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
        )

    def uninstall(
        self, package: str, extra_args: Optional[List[str]] = None, dry_run: bool = False, verbose: bool = False
    ) -> bool:
        """Uninstalls a single package."""
        command = ["uninstall", "-y", package]
        if extra_args:
            command.extend(extra_args)
        success, _ = self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False) # Usually don't capture uninstall output unless error
        return success

    def uninstall_multiple(
        self, packages: List[str], extra_args: Optional[List[str]] = None, dry_run: bool = False, verbose: bool = False
    ) -> bool:
        """Uninstalls multiple packages."""
        if not packages:
            logger.info("No packages provided to uninstall_multiple.")
            return True
        command = ["uninstall", "-y"] + list(packages)
        if extra_args:
            command.extend(extra_args)
        success, _ = self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
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
        self, path: str, index_url: Optional[str] = None, extra_args: Optional[List[str]] = None, dry_run: bool = False
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
        self, requirements_file: str, index_url: Optional[str] = None, extra_args: Optional[List[str]] = None, dry_run: bool = False
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
            logger.error("pip-audit command not found. Please install it (`pip install pip-audit` or `pip install pipmaster[audit]`)")
            return True, "pip-audit not found." # Assume vulnerable if tool missing

        command = [pip_audit_exe]
        if package_name:
            # pip-audit doesn't directly check a single *installed* package easily.
            # A workaround is needed, e.g., creating a temp req file.
            # For now, let's support file or full env check primarily.
            logger.warning("Checking single package vulnerability via pip-audit is not directly supported yet. Checking full environment.")
            # To implement later: create temp file with "package_name==version", run audit -r tempfile
            pass # Fall through to check full environment
        elif requirements_file:
            command.extend(["-r", requirements_file])

        # Add arguments to target the correct python environment if needed
        # pip-audit uses the Python it runs under by default, but can be told:
        # command.extend(["--python", self.target_python_executable]) # This might work? Needs testing.
        # For now, assume pip-audit is run *from* the target env or can find it.

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
                return False, result.stdout # No vulns found = False
            elif result.returncode == 1:
                logger.warning(f"pip-audit: Vulnerabilities found!\n{result.stdout}\n{result.stderr}")
                return True, f"Vulnerabilities found:\n{result.stdout}\n{result.stderr}" # Vulns found = True
            else:
                logger.error(f"pip-audit command failed (exit code {result.returncode}): {audit_command_str}\n{result.stderr}")
                return True, f"pip-audit error:\n{result.stderr}" # Assume vulnerable on error
        except Exception as e:
            logger.exception(f"Failed to run pip-audit: {e}")
            return True, f"Error running pip-audit: {e}" # Assume vulnerable on error

    def ensure_packages(
        self,
        requirements: Union[Dict[str, Optional[str]], List[str]], # Updated type hint
        index_url: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False, # Added verbose parameter
    ) -> bool:
        """
        Ensures that required packages are installed and meet version requirements.

        Checks each requirement. If a package is missing or doesn't meet the
        specifier, it's added to a list. Finally, a single 'pip install' command
        is run to install/update all necessary packages efficiently.

        Args:
            requirements (Union[Dict[str, Optional[str]], List[str]]):
                Either a dictionary mapping package names to optional PEP 440 version
                specifiers (e.g., {"requests": ">=2.25", "numpy": None}) OR a list
                of package strings (e.g., ["requests>=2.25", "numpy"]). If a list
                item has no specifier, the latest version is assumed.
            index_url (str, optional): Custom index URL for installations.
            extra_args (List[str], optional): Additional arguments for the pip install command.
            dry_run (bool): If True, simulate installations without making changes.
            verbose (bool): If True, show pip's output directly during installation.

        Returns:
            bool: True if all requirements were met initially or successfully
                  resolved/installed/updated, False if any installation failed.
        """
        if not requirements:
            logger.info("ensure_packages called with empty requirements.")
            return True

        packages_to_process: List[str] = []
        processed_packages = set() # To avoid processing duplicates from list input

        if verbose: logger.info("--- Ensuring Package Requirements ---")

        # --- Normalize input or handle different types in the loop ---
        items_to_check = []
        if isinstance(requirements, dict):
            items_to_check = list(requirements.items()) # List of (package, specifier) tuples
            is_dict_input = True
        elif isinstance(requirements, list):
            items_to_check = requirements # List of package strings
            is_dict_input = False
        else:
            logger.error(f"Invalid requirements type: {type(requirements)}. Must be dict or list.")
            return False

        for item in items_to_check:
            package_name: str = ""
            effective_specifier: Optional[str] = None
            install_target_string: str = "" # The string to use if installation is needed

            try:
                if is_dict_input:
                    package_name, effective_specifier = item # item is (pkg, spec)
                    # Basic validation: package name shouldn't have specifiers here
                    req_check = Requirement(package_name)
                    if str(req_check.specifier):
                        logger.warning(f"Specifier found in dictionary key '{package_name}'. It should be in the value. Using specifier from value: '{effective_specifier}'.")
                    package_name = req_check.name # Use normalized name
                    install_target_string = f"{package_name}{effective_specifier or ''}"
                else:
                    # Input is a list item (string)
                    package_input_str = item
                    req = Requirement(package_input_str)
                    package_name = req.name
                    effective_specifier = str(req.specifier) or None
                    install_target_string = package_input_str # Use the original string for install

                # Avoid reprocessing duplicates if input was a list
                if not is_dict_input and package_name in processed_packages:
                    continue
                processed_packages.add(package_name)

                specifier_str = f" (requires '{effective_specifier}')" if effective_specifier else ""
                if verbose: logger.info(f"Checking requirement: '{package_name}'{specifier_str}")

                # Check if currently installed version meets the requirement
                if self.is_installed(package_name, version_specifier=effective_specifier):
                    if verbose: logger.info(f"Requirement met for '{package_name}'{specifier_str}.")
                else:
                    installed_version = self.get_installed_version(package_name)
                    if installed_version:
                        logger.warning(f"Requirement NOT met for '{package_name}'. Installed: {installed_version}, Required: '{effective_specifier or 'latest'}'. Adding to update list.")
                    else:
                        logger.warning(f"Requirement NOT met for '{package_name}'. Package not installed. Adding to install list.")
                    packages_to_process.append(install_target_string)

            except ValueError as e: # Handle invalid requirement strings in list input
                logger.error(f"Invalid package/requirement string '{item}': {e}")
                # Optionally decide whether to fail immediately or just skip this item
                # return False # Fail fast
                continue # Skip invalid item
            except Exception as e:
                 logger.error(f"Error checking requirement for '{package_name or item}': {e}")
                 # Optionally add to process list to attempt installation anyway
                 if install_target_string: packages_to_process.append(install_target_string)


        if not packages_to_process:
            logger.info("[success]All specified package requirements are already met.[/success]")
            return True

        # If we need to install/update packages
        package_list_str = "', '".join(packages_to_process)
        logger.info(f"Found {len(packages_to_process)} packages requiring installation/update: '[magenta]{package_list_str}[/magenta]'")
        if dry_run:
             logger.info("[info]Dry run enabled. Simulating installation...[/info]")
        else:
             logger.info("Running installation/update command...")

        # Use install_multiple to handle the batch installation efficiently
        success = self.install_multiple(
            packages=packages_to_process,
            index_url=index_url,
            force_reinstall=False,
            upgrade=True, # Important to handle version updates/latest install
            extra_args=extra_args,
            dry_run=dry_run,
            verbose=verbose, # Pass verbose flag
        )

        if dry_run and success:
            logger.info(f"[info]Dry run successful for processing requirements. No changes were made.[/info]")
        elif success:
            logger.info("[success]Successfully processed all required package installations/updates.[/success]")
        else:
            logger.error("[error]Failed to install/update one or more required packages.[/error]") # Changed log level
            return False

        return True

# --- Module-level Convenience Functions (using default PackageManager) ---

# NOTE: The following wrapper functions explicitly define their signatures
#       and copy docstrings from the PackageManager methods. This is done
#       to provide proper type hinting, parameter suggestions, and docstring
#       visibility for IDEs like VS Code, even though it's repetitive.
#       Using *args, **kwargs would lose this static information.

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
        verbose=verbose
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
        verbose=verbose
    )

def install_edit(
    path: str,
    index_url: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False
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
    dry_run: bool = False
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
    )

def install_multiple_if_not_installed(
    packages: List[str],
    index_url: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
) -> bool:
    """
    Installs multiple packages only if they are not already installed, using the default PackageManager.
    Does *not* check version compatibility, only presence.

    Args:
        packages (List[str]): A list of package names/specifiers to check/install.
        index_url (str, optional): Custom index URL for installing missing packages.
        extra_args (List[str], optional): Additional arguments for pip install command.
        dry_run (bool): If True, simulate the command for missing packages.

    Returns:
        bool: True if all originally missing packages installed successfully or dry run ok, False otherwise.

    (Delegates to PackageManager.install_multiple_if_not_installed)
    """
    return _default_pm.install_multiple_if_not_installed(
        packages=packages, index_url=index_url, extra_args=extra_args, dry_run=dry_run
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
) -> bool:
    """
    Installs a package if missing, or updates it if installed, using the default PackageManager.

    Args:
        package (str): The package name, optionally with version specifier.
        index_url (str, optional): Custom index URL.
        force_reinstall (bool): If True, use --force-reinstall during update/install.
        extra_args (List[str], optional): Additional arguments for pip.
        dry_run (bool): If True, simulate the command.

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
    )

def uninstall(
    package: str, extra_args: Optional[List[str]] = None, dry_run: bool = False, verbose: bool = False
) -> bool:
    """
    Uninstalls a single package from the current environment.

    Args:
        package (str): The name of the package to uninstall.
        extra_args (List[str], optional): Additional arguments for pip uninstall.
        dry_run (bool): If True, simulate the command.

    Returns:
        bool: True on success or successful dry run, False otherwise.

    (Delegates to PackageManager.uninstall)
    """
    return _default_pm.uninstall(package=package, extra_args=extra_args, dry_run=dry_run, verbose=verbose)

def uninstall_multiple(
    packages: List[str], extra_args: Optional[List[str]] = None, dry_run: bool = False, verbose: bool = False
) -> bool:
    """
    Uninstalls multiple packages from the current environment.

    Args:
        packages (List[str]): A list of package names to uninstall.
        extra_args (List[str], optional): Additional arguments for pip uninstall.
        dry_run (bool): If True, simulate the command.

    Returns:
        bool: True on success or successful dry run, False otherwise.

    (Delegates to PackageManager.uninstall_multiple)
    """
    return _default_pm.uninstall_multiple(
        packages=packages, extra_args=extra_args, dry_run=dry_run, verbose = verbose
    )

def install_or_update_multiple(
    packages: List[str],
    index_url: Optional[str] = None,
    force_reinstall: bool = False,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
) -> bool:
    """
    Installs or updates multiple packages using the default PackageManager.

    Args:
        packages (List[str]): A list of package names/specifiers.
        index_url (str, optional): Custom index URL.
        force_reinstall (bool): If True, use --force-reinstall.
        extra_args (List[str], optional): Additional arguments for pip.
        dry_run (bool): If True, simulate the command.

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


# --- Deprecated Functions ---
# (Keep these as they are, they correctly call the underlying method)
def is_version_higher(package_name: str, required_version: str) -> bool:
    """DEPRECATED: Use is_version_compatible(package, f'>={required_version}')"""
    logger.warning("is_version_higher is deprecated. Use is_version_compatible instead.")
    return _default_pm.is_version_compatible(package_name, f">={required_version}")

def is_version_exact(package_name: str, required_version: str) -> bool:
    """DEPRECATED: Use is_version_compatible(package, f'=={required_version}')"""
    logger.warning("is_version_exact is deprecated. Use is_version_compatible instead.")
    return _default_pm.is_version_compatible(package_name, f"=={required_version}")

def ensure_packages(
    requirements: Union[Dict[str, Optional[str]], List[str]], # Updated hint
    index_url: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
    verbose: bool = False, # Added verbose
) -> bool:
    """
    Ensures packages meet requirements in the current environment using the default PackageManager.

    Checks each requirement from the dictionary or list. Installs or updates
    packages efficiently in a single batch if needed.

    Args:
        requirements (Union[Dict[str, Optional[str]], List[str]]):
            Either a dictionary mapping package names to optional PEP 440 version
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
        verbose=verbose, # Pass verbose
    )

# --- UV / Conda Placeholders ---
# These would be implemented similarly to PackageManager but with different _run_command logic

class UvPackageManager: # Placeholder
     def __init__(self, environment_path: Optional[str] = None):
         logger.warning("UvPackageManager is not yet implemented.")
         # Logic to find UV and target environment
         pass
     # Implement methods using uv commands

class CondaPackageManager: # Placeholder
     def __init__(self, environment_name_or_path: Optional[str] = None):
         logger.warning("CondaPackageManager is not yet implemented.")
         # Logic to find conda and target environment
         pass
     # Implement methods using conda commands

def get_uv_manager(environment_path: Optional[str] = None) -> Any: # Return type Any for now
    """Gets a UV Package Manager instance (Not Implemented)."""
    logger.warning("get_uv_manager is not yet implemented.")
    # return UvPackageManager(environment_path=environment_path)
    raise NotImplementedError("UV backend support is not yet implemented.")

def get_conda_manager(environment_name_or_path: Optional[str] = None) -> Any: # Return type Any for now
    """Gets a Conda Package Manager instance (Not Implemented)."""
    logger.warning("get_conda_manager is not yet implemented.")
    # return CondaPackageManager(environment_name_or_path=environment_name_or_path)
    raise NotImplementedError("Conda backend support is not yet implemented.")