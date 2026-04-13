# pipmaster/core.py

# -*- coding: utf-8 -*-
"""
Core Package Manager using pip with enhanced ASCIIColors visual feedback.

Author: ParisNeo
Created: 01/04/2024
Last Updated: 13/02/2026
"""

import subprocess
import sys
import os
import re
import shlex
import ascii_colors as logging
from ascii_colors import ASCIIColors
from typing import Optional, List, Tuple, Union, Dict, Any
from packaging import version as packaging_version
from packaging.specifiers import SpecifierSet

# Setup logger
logger = logging.getLogger(__name__)

# Emoji constants for visual feedback
EMOJI = {
    "package": "📦",
    "install": "⬇️",
    "update": "🔄",
    "remove": "🗑️",
    "check": "✅",
    "cross": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "search": "🔍",
    "gear": "⚙️",
    "sparkles": "✨",
    "rocket": "🚀",
    "clock": "⏱️",
    "star": "⭐",
}


class PackageManager:
    """
    Manages Python package installations and queries using pip.
    Enhanced with ASCIIColors visual feedback for pleasant UX.
    """
    def __init__(
        self,
        python_executable: Optional[str] = None,
        pip_command_base: Optional[List[str]] = None,
        venv_path: Optional[str] = None,
    ):
        self.venv_path = venv_path
        self.target_python_executable: str = python_executable or sys.executable
        self.pip_command_base: List[str] = pip_command_base or [sys.executable, "-m", "pip"]

        if self.venv_path:
            if os.name == 'nt':  # Windows
                self.target_python_executable = os.path.join(self.venv_path, 'Scripts', 'python.exe')
            else:  # Unix/Linux/MacOS
                self.target_python_executable = os.path.join(self.venv_path, 'bin', 'python')
            self.pip_command_base = [self.target_python_executable, "-m", "pip"]

        logger.debug(f"{EMOJI['info']}  PackageManager initialized for: {self.target_python_executable}")

    def _run_command(
        self, command: List[str], capture_output: bool = False, dry_run: bool = False, verbose: bool = False
    ) -> Tuple[bool, str]:
        """
        Runs a pip command using subprocess with optional visual feedback.
        """
        if dry_run:
            dry_run_msg = f"{EMOJI['info']} Dry run: Would execute: {' '.join(self.pip_command_base + command)}"
            logger.info(dry_run_msg)
            return True, f"Dry run: Command would be '{' '.join(command)}'"

        command_to_run = self.pip_command_base + command
        command_str = " ".join(command_to_run)
        
        if verbose:
            logger.info(f"{EMOJI['gear']} Executing: {command_str}")

        try:
            stderr_pipe = subprocess.PIPE if capture_output or verbose else subprocess.DEVNULL
            stdout_pipe = subprocess.PIPE if capture_output else (None if verbose else subprocess.DEVNULL)

            result = subprocess.run(
                command_to_run,
                stdout=stdout_pipe,
                stderr=stderr_pipe,
                text=True,
                check=False
            )

            if result.returncode == 0:
                msg = f"{EMOJI['check']} Command succeeded"
                if verbose:
                    msg += f": {command_str}"
                    logger.info(msg)
                else:
                    logger.debug(msg)
                output = result.stdout if result.stdout is not None else "Command executed successfully."
                return True, output
            else:
                error_message = f"{EMOJI['cross']} Command failed (exit {result.returncode}): {command_str}"
                stderr_content = result.stderr if result.stderr else "No stderr captured."
                if capture_output:
                    error_message += f"\n--- stderr ---\n{stderr_content}"
                logger.error(error_message)
                return False, error_message

        except FileNotFoundError:
            error_msg = f"{EMOJI['cross']} Error: '{self.pip_command_base[0]}' not found. Is it installed and in PATH?"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"{EMOJI['cross']} Unexpected error running command: {e}"
            logger.exception(error_msg)
            return False, error_msg

    def _check_if_install_is_needed(
        self, package: str, version_specifier: Optional[str], always_update: bool, verbose: bool = False
    ) -> Tuple[bool, str, bool]:
        """
        Determines if an install/update is needed with visual feedback logging.
        Returns: (is_needed: bool, install_target: str, force_reinstall: bool)
        """
        # Handle "latest" as a special version specifier meaning "get the latest version"
        if version_specifier == "latest":
            install_target = package
            ASCIIColors.cyan(f"{EMOJI['update']} Latest version requested for '{package}'. Scheduled for update.")
            return True, install_target, False

        # Handle VCS URLs (git+, hg+, svn+, etc.)
        # Extract package name from URLs like "git+https://github.com/user/repo.git"
        vcs_match = re.match(r'^(git\+|hg\+|svn\+|bzr\+)(.+)$', package)
        if vcs_match:
            # For VCS URLs, extract the repo name as the package name
            vcs_url = package
            # Extract package name from the end of the URL (e.g., "repo.git" -> "repo")
            url_path = vcs_match.group(2).rstrip('/')
            # Handle both .git suffix and bare repo names
            pkg_name_match = re.search(r'/([^/]+?)(?:\.git)?$', url_path)
            if pkg_name_match:
                package_name_from_vcs = pkg_name_match.group(1)
            else:
                # Fallback: use last path component
                package_name_from_vcs = url_path.split('/')[-1].replace('.git', '')
            
            # Check if package is installed (any version, since VCS URLs don't specify version easily)
            is_pkg_installed = self.is_installed(package_name_from_vcs)
            
            if is_pkg_installed and not always_update:
                if verbose:
                    ASCIIColors.green(f"{EMOJI['check']} Package '{package_name_from_vcs}' (from VCS) is already installed. Skipping.")
                else:
                    logger.debug(f"{EMOJI['check']} Package '{package_name_from_vcs}' (from VCS) already installed.")
                return False, package_name_from_vcs, False
            
            # Need to install/update
            action = "update" if is_pkg_installed else "installation"
            ASCIIColors.yellow(f"{EMOJI['search']} Package '{package_name_from_vcs}' (from VCS) scheduled for {action}.")
            return True, vcs_url, False

        # Handle case where package name contains specifiers (e.g., "foo>=1.0")
        # This prevents "Package 'foo>=1.0' not found" errors by splitting name and version
        if not version_specifier and any(c in package for c in "><=!~"):
            match = re.match(r"^([a-zA-Z0-9_.-]+)\s*(.*)$", package)
            if match and match.group(2):
                package = match.group(1)
                version_specifier = match.group(2).strip()

        logger.debug(f"{EMOJI['search']} Checking if install needed for: {package} (spec: {version_specifier}, always_update: {always_update})")
        
        is_pkg_installed = self.is_installed(package)

        if not is_pkg_installed:
            install_target = f"{package}{version_specifier}" if version_specifier else package
            # Always notify user why we are installing something
            ASCIIColors.yellow(f"{EMOJI['search']} Package '{package}' not found. Scheduled for installation.")
            return True, install_target, False

        if always_update:
            install_target = f"{package}{version_specifier}" if version_specifier else package
            # Always notify user about forced updates
            ASCIIColors.cyan(f"{EMOJI['update']} Always-update requested for '{package}'. Scheduled for update.")
            return True, install_target, False

        if version_specifier:
            if self.is_version_compatible(package, version_specifier):
                if verbose:
                    ASCIIColors.green(f"{EMOJI['check']} Package '{package}' is installed and meets specifier '{version_specifier}'. Skipping.")
                else:
                    logger.debug(f"{EMOJI['check']} Package '{package}' installed and meets specifier '{version_specifier}'. Skipping.")
                return False, package, False
            else:
                current_ver = self.get_installed_version(package)
                install_target = f"{package}{version_specifier}"
                # Always notify user about version mismatches
                ASCIIColors.red(f"{EMOJI['warning']} Version mismatch for '{package}': Installed v{current_ver} does not meet '{version_specifier}'. Scheduled for update.")
                return True, install_target, False
        else:
            if verbose:
                ASCIIColors.green(f"{EMOJI['check']} Package '{package}' is already installed. Skipping.")
            else:
                logger.debug(f"{EMOJI['check']} Package '{package}' already installed (no version check required).")
            return False, package, False

    def install(
        self,
        package: str,
        index_url: Optional[str] = None,
        force_reinstall: bool = False,
        upgrade: bool = True,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> bool:
        """Installs a package with pleasant visual feedback."""
        command = ["install"]
        if upgrade:
            command.append("--upgrade")
        if force_reinstall:
            command.append("--force-reinstall")
        if index_url:
            command.extend(["--index-url", index_url])
        if extra_args:
            command.extend(extra_args)
        command.append(package)

        action_emoji = EMOJI['update'] if upgrade else EMOJI['install']
        action_text = "Updating" if upgrade else "Installing"
        msg = f"{action_emoji} {action_text} package: {package}"
        
        if verbose or dry_run:
            logger.info(msg)
            success, _ = self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
            if success:
                logger.info(f"{EMOJI['sparkles']} Successfully handled package: {package}")
            else:
                logger.error(f"{EMOJI['cross']} Failed to handle package: {package}")
        else:
            with ASCIIColors.status(msg, spinner="dots", spinner_style="bold cyan") as status:
                success, _ = self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
                if success:
                    logger.debug(f"{EMOJI['sparkles']} Successfully handled package: {package}")
                else:
                    logger.error(f"{EMOJI['cross']} Failed to handle package: {package}")

        return success

    def install_if_missing(
        self,
        package: str,
        version_specifier: Optional[str] = None,
        always_update: bool = False,
        index_url: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> bool:
        """Conditionally installs a package with visual status feedback."""
        is_needed, install_target, force = self._check_if_install_is_needed(package, version_specifier, always_update, verbose=verbose)

        if not is_needed:
            return True

        return self.install(
            install_target,
            index_url=index_url,
            upgrade=True,
            force_reinstall=force,
            extra_args=extra_args,
            dry_run=dry_run,
            verbose=verbose,
        )

    def _get_packages_to_process(
        self,
        requirements: Union[str, Dict[str, Optional[str]], List[str]],
        always_update: bool = False,
        verbose: bool = False,
        progress_callback: Optional[callable] = None,
    ) -> List[str]:
        """Analyzes requirements and returns list of packages needing action."""
        if isinstance(requirements, str):
            requirements = {requirements: None}
        elif isinstance(requirements, list):
            temp_dict = {}
            for item in requirements:
                item = item.strip()
                if not item:
                    continue
                match = re.match(r"^([a-zA-Z0-9_.-]+)\s*(.*)$", item)
                if match:
                    pkg_name = match.group(1)
                    specifier = match.group(2).strip() if match.group(2) else None
                    temp_dict[pkg_name] = specifier
                else:
                    logger.warning(f"{EMOJI['warning']} Invalid requirement format: '{item}'")
            requirements = temp_dict
        elif not isinstance(requirements, dict):
            logger.error(f"{EMOJI['cross']} Invalid requirements type: {type(requirements)}")
            return []

        packages_to_process = []
        total = len(requirements)
        for idx, (pkg_name, specifier) in enumerate(requirements.items(), 1):
            is_needed, install_target, _ = self._check_if_install_is_needed(pkg_name, specifier, always_update, verbose=verbose)
            if is_needed:
                packages_to_process.append(install_target)
                if progress_callback:
                    progress_callback({
                        "status": "checking",
                        "message": f"Package '{pkg_name}' needs installation",
                        "package": pkg_name,
                        "install_target": install_target,
                        "progress": idx,
                        "total": total
                    })
            else:
                if progress_callback:
                    progress_callback({
                        "status": "checking",
                        "message": f"Package '{pkg_name}' already satisfied",
                        "package": pkg_name,
                        "progress": idx,
                        "total": total
                    })

        if not packages_to_process:
            logger.debug(f"{EMOJI['check']} All requirements already satisfied.")

        return packages_to_process

    def ensure_packages(
        self,
        requirements: Union[str, Dict[str, Optional[str]], List[str]],
        index_url: Optional[str] = None,
        always_update: bool = False,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False,
        progress_callback: Optional[callable] = None,
    ) -> bool:
        """
        Idempotently ensures packages meet requirements with pleasant progress feedback.
        """
        packages_to_process = self._get_packages_to_process(requirements, always_update, verbose, progress_callback)

        if not packages_to_process:
            msg = f"{EMOJI['check']} All package requirements satisfied. Nothing to do."
            logger.debug(msg)
            if progress_callback:
                progress_callback({"status": "complete", "message": msg, "packages": []})
            return True

        pkg_list_str = "', '".join(packages_to_process)
        if verbose:
            logger.info(f"{EMOJI['package']} Found {len(packages_to_process)} packages to process: '{pkg_list_str}'")
        else:
            logger.debug(f"{EMOJI['package']} Found {len(packages_to_process)} packages to process.")
        
        if progress_callback:
            progress_callback({
                "status": "processing",
                "message": f"Installing {len(packages_to_process)} package(s)",
                "packages": packages_to_process,
                "count": len(packages_to_process)
            })

        result = self.install_multiple(
            packages=packages_to_process,
            index_url=index_url,
            force_reinstall=False,
            upgrade=True,
            extra_args=extra_args,
            dry_run=dry_run,
            verbose=verbose,
        )
        
        if progress_callback:
            progress_callback({
                "status": "complete" if result else "failed",
                "message": "Installation complete" if result else "Installation failed",
                "packages": packages_to_process,
                "success": result
            })
        
        return result

    def ensure_requirements(
        self,
        requirements_file: str,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> bool:
        """Ensures packages from requirements.txt with visual feedback."""
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            logger.error(f"{EMOJI['cross']} Requirements file not found: {requirements_file}")
            return False

        requirements_list = []
        pip_options = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if line.startswith('-'):
                pip_options.extend(shlex.split(line))
            else:
                package_req = line.split('#')[0].strip()
                if package_req:
                    requirements_list.append(package_req)

        if not requirements_list and not pip_options:
            logger.debug(f"{EMOJI['info']} No requirements in {requirements_file}")
            return True
        
        if verbose:
            logger.info(f"{EMOJI['package']} Processing {len(requirements_list)} requirements from {requirements_file}")

        return self.ensure_packages(
            requirements=requirements_list,
            index_url=None,
            extra_args=pip_options,
            dry_run=dry_run,
            verbose=verbose
        )

    def install_multiple(
        self,
        packages: List[str],
        index_url: Optional[str] = None,
        force_reinstall: bool = False,
        upgrade: bool = True,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> bool:
        """Installs multiple packages with batch progress feedback."""
        if not packages:
            logger.debug(f"{EMOJI['check']} No packages to install.")
            return True

        batch_size = len(packages)
        msg = f"{EMOJI['rocket']} Installing batch of {batch_size} package(s)..."
        
        command = ["install"]
        if upgrade:
            command.append("--upgrade")
        if force_reinstall:
            command.append("--force-reinstall")
        if index_url:
            command.extend(["--index-url", index_url])
        if extra_args:
            command.extend(extra_args)
        command.extend(packages)

        if verbose or dry_run:
            logger.info(msg)
            success, _ = self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
            if success:
                logger.info(f"{EMOJI['sparkles']} Batch installation complete: {batch_size} package(s)")
            else:
                logger.error(f"{EMOJI['cross']} Batch installation failed for some packages")
        else:
            with ASCIIColors.status(msg, spinner="star", spinner_style="bold green") as status:
                success, _ = self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
                if success:
                    logger.debug(f"{EMOJI['sparkles']} Batch installation complete: {batch_size} package(s)")
                else:
                    logger.error(f"{EMOJI['cross']} Batch installation failed for some packages")
        
        return success

    def uninstall(
        self, package: str, extra_args: Optional[List[str]] = None, dry_run: bool = False, verbose: bool = False
    ) -> bool:
        """Uninstalls a package with visual feedback."""
        msg = f"{EMOJI['remove']} Removing package: {package}"
        
        command = ["uninstall", "-y", package]
        if extra_args:
            command.extend(extra_args)
        
        if verbose or dry_run:
            logger.info(msg)
            success, _ = self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
            if success:
                logger.info(f"{EMOJI['check']} Successfully removed: {package}")
            else:
                logger.error(f"{EMOJI['cross']} Failed to remove: {package}")
        else:
            with ASCIIColors.status(msg, spinner="pulse", spinner_style="bold red") as status:
                success, _ = self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
                if success:
                    logger.debug(f"{EMOJI['check']} Successfully removed: {package}")
                else:
                    logger.error(f"{EMOJI['cross']} Failed to remove: {package}")
        
        return success

    def uninstall_multiple(
        self, packages: List[str], extra_args: Optional[List[str]] = None, dry_run: bool = False, verbose: bool = False
    ) -> bool:
        """Uninstalls multiple packages with batch feedback."""
        if not packages:
            return True

        msg = f"{EMOJI['remove']} Removing {len(packages)} package(s)..."
        
        command = ["uninstall", "-y"] + packages
        if extra_args:
            command.extend(extra_args)
        
        if verbose or dry_run:
            logger.info(msg)
            success, _ = self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
            if success:
                logger.info(f"{EMOJI['check']} Batch removal complete")
            else:
                logger.error(f"{EMOJI['cross']} Some packages could not be removed")
        else:
            with ASCIIColors.status(msg, spinner="pulse", spinner_style="bold red") as status:
                success, _ = self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
                if success:
                    logger.debug(f"{EMOJI['check']} Batch removal complete")
                else:
                    logger.error(f"{EMOJI['cross']} Some packages could not be removed")
        
        return success

    def is_installed(self, package_name: str, version_specifier: Optional[str] = None) -> bool:
        """Checks if package is installed with optional version check."""
        try:
            import importlib.metadata
            dist = importlib.metadata.distribution(package_name)
            
            if version_specifier:
                installed_version_str = dist.version
                spec = SpecifierSet(version_specifier)
                is_compatible = installed_version_str in spec
                if not is_compatible and logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"{EMOJI['warning']} '{package_name}' v{installed_version_str} not compatible with '{version_specifier}'")
                return is_compatible
            
            return True
            
        except importlib.metadata.PackageNotFoundError:
            return False

    def get_installed_version(self, package_name: str) -> Optional[str]:
        """Gets installed package version."""
        try:
            import importlib.metadata
            return importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError:
            return None

    def is_version_compatible(self, package_name: str, version_specifier: str) -> bool:
        """Checks if installed version meets specifier."""
        installed_version = self.get_installed_version(package_name)
        if installed_version is None:
            return False
        
        try:
            spec = SpecifierSet(version_specifier)
            return installed_version in spec
        except Exception as e:
            logger.warning(f"{EMOJI['warning']} Invalid version specifier '{version_specifier}': {e}")
            return False

    def get_package_info(self, package_name: str) -> Optional[str]:
        """Retrieves package information."""
        success, output = self._run_command(
            ["show", package_name], capture_output=True
        )
        return output if success else None

    def check_vulnerabilities(
        self,
        package_name: Optional[str] = None,
        requirements_file: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
    ) -> Tuple[bool, str]:
        """Checks for security vulnerabilities with visual feedback."""
        import shutil
        
        pip_audit_exe = shutil.which("pip-audit")
        if not pip_audit_exe:
            logger.warning(f"{EMOJI['warning']} pip-audit not found. Install with: pip install pip-audit")
            return True, "pip-audit not installed"

        command_list = [pip_audit_exe]
        if requirements_file:
            command_list.extend(["-r", requirements_file])
        elif package_name:
            logger.warning(f"{EMOJI['warning']} Single package scan not supported, scanning all")
            
        if extra_args:
            command_list.extend(extra_args)
        
        command_str = " ".join(command_list)
        logger.info(f"{EMOJI['shield']} Running security scan: {command_str}")

        try:
            result = subprocess.run(
                command_list,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )

            if result.returncode == 0:
                logger.info(f"{EMOJI['check']} No vulnerabilities found")
                return False, result.stdout
            elif result.returncode == 1:
                logger.warning(f"{EMOJI['warning']} Vulnerabilities detected!")
                return True, f"Vulnerabilities found:\n{result.stdout}\n{result.stderr}"
            else:
                logger.error(f"{EMOJI['cross']} pip-audit failed (code {result.returncode})")
                return True, f"pip-audit error:\n{result.stderr}"
                
        except Exception as e:
            logger.exception(f"{EMOJI['cross']} Failed to run pip-audit: {e}")
            return True, f"Error: {e}"
