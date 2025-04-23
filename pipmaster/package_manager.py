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
import logging
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
        self, command: List[str], capture_output: bool = False, dry_run: bool = False
    ) -> Tuple[bool, str]:
        """
        Runs a command (typically pip) using subprocess.run.

        Args:
            command (list): The command arguments (e.g., ["install", "requests"]).
            capture_output (bool): Whether to capture stdout/stderr.
            dry_run (bool): If True, attempts to add the backend's dry-run flag.

        Returns:
            tuple: (bool: success, str: output or error message)
        """
        full_command_list = self.pip_command_base + command
        command_str = " ".join(full_command_list)

        if dry_run:
            # Add backend-specific dry-run flags (only pip known for now)
            # pip install/uninstall/download support --dry-run
            if command[0] in ["install", "uninstall", "download"]:
                # Find insert position (before package names/files)
                insert_pos = -1
                for i, arg in enumerate(command):
                     # Heuristic: stop before first non-flag argument after the action
                     if i > 0 and not arg.startswith('-'):
                         insert_pos = i
                         break
                if insert_pos != -1:
                    dry_run_command_list = self.pip_command_base + command[:insert_pos] + ["--dry-run"] + command[insert_pos:]
                else: # Append if only action and flags
                    dry_run_command_list = self.pip_command_base + command + ["--dry-run"]

                command_str = " ".join(dry_run_command_list)
                logger.info(f"DRY RUN execution: {command_str}")
                # For dry run, we often just simulate success if the command *could* be formed.
                # A more robust dry run might parse the dry run output if available.
                return True, f"Dry run: Command would be '{command_str}'"
            else:
                logger.warning(f"Dry run not applicable to command: {command[0]}. Executing normally.")
                # Fall through to normal execution if dry run not supported

        logger.info(f"Executing: {command_str}")
        try:
            # Using shell=True for convenience with quoted paths, but be mindful of security.
            # If shell=False was used, the command list needs careful handling of quotes.
            result = subprocess.run(
                command_str,
                shell=True,
                check=False, # Don't raise exception on non-zero exit
                capture_output=capture_output,
                text=True,
                encoding="utf-8",
            )
            output = result.stdout if capture_output and result.stdout else ""
            error_out = result.stderr if capture_output and result.stderr else ""

            if result.returncode == 0:
                logger.info(f"Command succeeded: {command_str}")
                return True, output or "Command executed successfully."
            else:
                error_message = (
                    f"Command failed with exit code {result.returncode}: {command_str}"
                )
                if capture_output:
                    error_message += f"\n--- stdout ---\n{output}\n--- stderr ---\n{error_out}"
                else:
                    error_message += "\nCheck console output for stderr."
                logger.error(error_message)
                return False, error_message
        except FileNotFoundError:
            error_message = f"Error: Command execution failed. Is '{self.pip_command_base[0]}' a valid executable path?"
            logger.exception(error_message)
            return False, error_message
        except Exception as e:
            error_message = f"An unexpected error occurred while running command '{command_str}': {e}"
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

        Returns:
            bool: True on success or successful dry run, False otherwise.
        """
        command = ["install", package]
        if upgrade:
            command.append("--upgrade")
        if force_reinstall:
            command.append("--force-reinstall")
        if index_url:
            command.extend(["--index-url", index_url])
        if extra_args:
            command.extend(extra_args)
        success, _ = self._run_command(command, dry_run=dry_run)
        return success

    def install_if_missing(
        self,
        package: str,
        version: Optional[str] = None,
        enforce_version: bool = False,
        always_update: bool = False,
        index_url: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
        version_specifier: Optional[str] = None, # NEW
        dry_run: bool = False, # NEW
    ) -> bool:
        """
        Installs a package conditionally based on presence and version requirements.

        Args:
            package (str): Name of the package (e.g., "numpy"). Can include specifier.
            version (str, optional): Specific version for enforce_version (e.g., "1.26.4").
                                     DEPRECATED in favor of version_specifier for >= checks.
            enforce_version (bool): If True and `version` is set, ensure *exact* version.
                                    DEPRECATED in favor of version_specifier="==x.y.z".
            always_update (bool): If True and package is installed, update to latest.
            index_url (str, optional): Custom index URL for pip.
            extra_args (List[str], optional): Additional arguments for pip.
            version_specifier (str, optional): A PEP 440 specifier (e.g., ">=1.2", "==1.3.4").
                                              Takes precedence over `version`/`enforce_version`.
            dry_run (bool): If True, simulate the command.

        Returns:
            bool: True if installation was successful, not needed, or dry run ok. False otherwise.
        """
        try:
            # Handle package name with potential embedded specifier
            req = Requirement(package)
            pkg_name = req.name
            # Use specifier from package string if none provided explicitly
            effective_specifier = version_specifier or str(req.specifier) or None
        except ValueError:
            pkg_name = package # Simple name
            effective_specifier = version_specifier

        # Handle deprecated arguments with warnings, prioritizing version_specifier
        if effective_specifier is None and enforce_version and version:
             logger.warning("Using deprecated 'version' and 'enforce_version'. Prefer 'version_specifier=\"==%s\"'.", version)
             effective_specifier = f"=={version}"
        elif effective_specifier is None and version and not enforce_version:
             logger.warning("Using deprecated 'version' without 'enforce_version'. Interpreting as '>={%s}'. Prefer 'version_specifier=\">=%s\"'.", version, version)
             effective_specifier = f">={version}"


        is_installed_flag = self.is_installed(pkg_name) # Check base name

        if is_installed_flag:
            installed_version_str = self.get_installed_version(pkg_name)
            logger.info(
                f"Package '{pkg_name}' is already installed (version {installed_version_str})."
            )

            # Check compatibility if a specifier is provided
            needs_install = False
            if effective_specifier and not self.is_version_compatible(pkg_name, effective_specifier):
                logger.warning(
                    f"Installed version {installed_version_str} of '{pkg_name}' "
                    f"does not meet specifier '{effective_specifier}'. Needs update/reinstall."
                )
                needs_install = True
            elif always_update:
                logger.info(f"Flag 'always_update=True' set. Checking for updates for '{pkg_name}'.")
                # We'll run install with --upgrade, pip will decide if update is needed
                needs_install = True

            if not needs_install:
                 logger.info(
                     f"'{pkg_name}' is installed and meets requirements. No action needed."
                 )
                 return True

            # If we reach here, installation/update is needed
            # Construct target: use original 'package' if it had specifier, else name + specifier
            install_target = package if req.specifier else f"{pkg_name}{effective_specifier or ''}"
            logger.info(f"Attempting to install/update '{pkg_name}' to satisfy '{install_target}'...")
            # Use install: upgrade=True handles updates, force_reinstall needed if version is exact? Pip usually handles it.
            # Let's add force_reinstall if we specifically failed a version check for robustness
            force = needs_install and effective_specifier is not None

            return self.install(
                    install_target,
                    index_url=index_url,
                    upgrade=True, # Always allow upgrade when action is needed
                    force_reinstall=force,
                    extra_args=extra_args,
                    dry_run=dry_run,
                )

        else:
            # Package is missing, install it
            logger.info(f"Package '{pkg_name}' not found. Installing...")
            # Construct target string: use original 'package' if it had specifier, else use name + specifier
            install_target = package if req.specifier else f"{pkg_name}{effective_specifier or ''}"
            # Don't force reinstall on first install, upgrade only if always_update requested
            return self.install(
                install_target,
                index_url=index_url,
                upgrade=always_update,
                force_reinstall=False,
                extra_args=extra_args,
                dry_run=dry_run,
            )


    def install_multiple(
        self,
        packages: List[str],
        index_url: Optional[str] = None,
        force_reinstall: bool = False,
        upgrade: bool = True,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> bool:
        """Installs or upgrades multiple packages."""
        if not packages:
            logger.info("No packages provided to install_multiple.")
            return True
        command = ["install"] + list(packages)
        if upgrade:
             command.append("--upgrade")
        if force_reinstall:
            command.append("--force-reinstall")
        if index_url:
            command.extend(["--index-url", index_url])
        if extra_args:
            command.extend(extra_args)
        success, _ = self._run_command(command, dry_run=dry_run)
        return success

    def install_multiple_if_not_installed(
        self,
        packages: List[str],
        index_url: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> bool:
        """
        Installs multiple packages only if they are not already installed.
        Does *not* check version compatibility, only presence. Use install_if_missing in a loop for that.
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
                 pkg_name = pkg_input

             # Use the is_installed check on the base name
             if not self.is_installed(pkg_name):
                 logger.info(f"Package '{pkg_name}' (from '{pkg_input}') marked for installation.")
                 # Install using the original input string (may contain specifier)
                 packages_to_install.append(pkg_input)
             else:
                 logger.info(f"Package '{pkg_name}' is already installed. Skipping.")

        if not packages_to_install:
            logger.info("All specified packages are already installed.")
            return True

        logger.info(f"Attempting to install missing packages: {', '.join(packages_to_install)}")
        # Use install_multiple logic, but without implicit upgrade/force reinstall by default
        # Pass dry_run flag down
        return self.install_multiple(
            packages_to_install,
            index_url=index_url,
            upgrade=False, # Don't upgrade existing dependencies implicitly
            force_reinstall=False,
            extra_args=extra_args,
            dry_run=dry_run
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
        self, package: str, extra_args: Optional[List[str]] = None, dry_run: bool = False
    ) -> bool:
        """Uninstalls a single package."""
        command = ["uninstall", "-y", package]
        if extra_args:
            command.extend(extra_args)
        success, _ = self._run_command(command, dry_run=dry_run)
        return success

    def uninstall_multiple(
        self, packages: List[str], extra_args: Optional[List[str]] = None, dry_run: bool = False
    ) -> bool:
        """Uninstalls multiple packages."""
        if not packages:
            logger.info("No packages provided to uninstall_multiple.")
            return True
        command = ["uninstall", "-y"] + list(packages)
        if extra_args:
            command.extend(extra_args)
        success, _ = self._run_command(command, dry_run=dry_run)
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
        requirements: Dict[str, Optional[str]],
        index_url: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
    ) -> bool:
        """
        Ensures that all specified packages are installed and meet version requirements.

        Checks each package and its optional version specifier. If a package
        is missing or doesn't meet the specifier, it's added to a list.
        Finally, a single 'pip install' command is run to install/update all
        necessary packages efficiently.

        Args:
            requirements (Dict[str, Optional[str]]): A dictionary where keys are
                package names and values are optional PEP 440 version specifiers
                (e.g., {"requests": ">=2.25", "numpy": None, "torch": "==1.10.0"}).
                Use None or "" if no specific version is required.
            index_url (str, optional): Custom index URL to use for installations.
            extra_args (List[str], optional): Additional arguments for the pip install command.
            dry_run (bool): If True, simulate the installation command without making changes.

        Returns:
            bool: True if all requirements were met initially or successfully
                  installed/updated, False if any installation failed.
        """
        if not requirements:
            logger.info("ensure_packages called with empty requirements dictionary.")
            return True

        packages_to_process: List[str] = []
        console.print("--- Ensuring Package Requirements ---")

        for package, specifier in requirements.items():
            specifier_str = f" (requires '{specifier}')" if specifier else ""
            logger.info(f"Checking requirement: '{package}'{specifier_str}")

            try:
                # Check if currently installed version meets the requirement
                if self.is_installed(package, version_specifier=specifier):
                    logger.info(f"Requirement met for '{package}'{specifier_str}.")
                else:
                    installed_version = self.get_installed_version(package)
                    if installed_version:
                         logger.warning(
                             f"Requirement NOT met for '{package}'. Installed: {installed_version}, Required: '{specifier}'. Adding to update list."
                         )
                    else:
                         logger.warning(
                             f"Requirement NOT met for '{package}'. Package not installed. Adding to install list."
                         )
                    # Add package string with specifier for the install command
                    # Pip handles "package>=x.y" format correctly
                    package_string = f"{package}{specifier or ''}"
                    packages_to_process.append(package_string)

            except Exception as e:
                 # Catch potential errors during checks, though is_installed should handle most
                 logger.error(f"Error checking requirement for '{package}': {e}")
                 # Treat check error as needing processing? Or return False?
                 # Let's try adding it to process list for install attempt.
                 package_string = f"{package}{specifier or ''}"
                 packages_to_process.append(package_string)


        if not packages_to_process:
            console.print("[success]All specified package requirements are already met.[/success]")
            return True

        # If we need to install/update packages
        package_list_str = "', '".join(packages_to_process)
        console.print(f"Found {len(packages_to_process)} packages requiring installation/update: '[magenta]{package_list_str}[/magenta]'")
        if dry_run:
             console.print("[info]Dry run enabled. Simulating installation...[/info]")
        else:
             console.print("Running installation/update command...")

        # Use install_multiple to handle the batch installation efficiently
        # Pass upgrade=True to ensure packages needing version change are handled
        success = self.install_multiple(
            packages=packages_to_process,
            index_url=index_url,
            force_reinstall=False, # Generally not needed unless specific issues arise
            upgrade=True, # Important to handle version updates
            extra_args=extra_args,
            dry_run=dry_run,
        )

        if dry_run and success:
            logger.info(f"[info]Dry run successful for processing requirements. No changes were made.[/info]")
        elif success:
            logger.info("[success]Successfully processed all required package installations/updates.[/success]")
             # Optional: Re-verify after install? Could add extra checks here if needed.
        else:
            logger.info("[error]Failed to install/update one or more required packages.[/error]")
            return False

        return True # Return True if install_multiple succeeded

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
    package: str, extra_args: Optional[List[str]] = None, dry_run: bool = False
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
    return _default_pm.uninstall(package=package, extra_args=extra_args, dry_run=dry_run)

def uninstall_multiple(
    packages: List[str], extra_args: Optional[List[str]] = None, dry_run: bool = False
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
        packages=packages, extra_args=extra_args, dry_run=dry_run
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
    requirements: Dict[str, Optional[str]],
    index_url: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
) -> bool:
    """
    Ensures packages meet requirements in the current environment using the default PackageManager.

    Checks each package and its optional version specifier from the requirements
    dictionary. Installs or updates packages efficiently in a single batch if needed.

    Args:
        requirements (Dict[str, Optional[str]]): Dictionary of package names to
            optional version specifiers (e.g., {"requests": ">=2.25", "numpy": None}).
        index_url (str, optional): Custom index URL for installations.
        extra_args (List[str], optional): Additional arguments for the pip install command.
        dry_run (bool): If True, simulate installations without making changes.

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