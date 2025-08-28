# pipmaster/async_package_manager.py

# -*- coding: utf-8 -*-
"""
Asynchronous Package Manager using pip.

Provides an async class and functions to interact with pip asynchronously.

Author: ParisNeo
Created: 23/04/2025
Last Updated: 24/04/2025
"""

import asyncio
import sys
import importlib.metadata
import ascii_colors as logging
import shutil
import shlex
from typing import Optional, List, Tuple, Union, Dict, Any

from .package_manager import PackageManager, Requirement

logger = logging.getLogger(__name__)


class AsyncPackageManager:
    """
    Manages Python package installations and queries using pip asynchronously.
    Mirrors the synchronous PackageManager interface but uses async methods.
    """
    def __init__(
        self,
        python_executable: Optional[str] = None,
        pip_command_base: Optional[List[str]] = None,
    ):
        """Initializes the AsyncPackageManager."""
        # Reuse sync init logic to determine command base
        sync_pm = PackageManager(python_executable, pip_command_base)
        self.pip_command_base = sync_pm.pip_command_base
        self.target_python_executable = sync_pm.target_python_executable
        self._sync_pm_instance = sync_pm  # Keep a sync instance for metadata checks
        logger.debug(f"[Async] Initialized for Python: {self.target_python_executable}")

    async def _run_command(
        self, command: List[str], capture_output: bool = False, dry_run: bool = False, verbose: bool = False
    ) -> Tuple[bool, str]:
        """
        Runs a command asynchronously using asyncio.create_subprocess_shell.
        """
        # Dry run logic is synchronous and quick, handle it first.
        if dry_run:
            # Re-use the synchronous dry-run logic which is well-tested
            # This is non-blocking and fast.
            success, output = self._sync_pm_instance._run_command(command, dry_run=True)
            return success, output

        command_str = " ".join(self.pip_command_base + command)
        logger.info(f"[Async] Executing: {command_str}")

        try:
            stdout_pipe = asyncio.subprocess.PIPE if capture_output or verbose else asyncio.subprocess.DEVNULL
            stderr_pipe = asyncio.subprocess.PIPE if capture_output or verbose else asyncio.subprocess.DEVNULL

            if verbose and not capture_output:
                # For verbose, we stream directly to console, which is complex to do
                # perfectly async. The simplest robust approach is to capture and print.
                stdout_pipe = asyncio.subprocess.PIPE
                stderr_pipe = asyncio.subprocess.STDOUT # Merge stderr into stdout

            process = await asyncio.create_subprocess_shell(
                command_str,
                stdout=stdout_pipe,
                stderr=stderr_pipe,
            )

            if verbose and not capture_output:
                # Stream output if verbose
                while True:
                    line = await process.stdout.readline()
                    if not line:
                        break
                    print(line.decode().strip())
                await process.wait()
                stdout_str, stderr_str = "", "" # Already printed
            else:
                # Standard capture
                stdout, stderr = await process.communicate()
                stdout_str = stdout.decode("utf-8", errors="ignore") if stdout else ""
                stderr_str = stderr.decode("utf-8", errors="ignore") if stderr else ""

            if process.returncode == 0:
                logger.info(f"[Async] Command succeeded: {command_str}")
                return True, stdout_str or "Command executed successfully."
            else:
                error_message = f"[Async] Command failed (code {process.returncode}): {command_str}"
                if stdout_str: error_message += f"\n--- stdout ---\n{stdout_str.strip()}"
                if stderr_str: error_message += f"\n--- stderr ---\n{stderr_str.strip()}"
                logger.error(error_message)
                return False, error_message
                
        except FileNotFoundError:
            error_message = f"[Async] Error: Command failed. Is '{self.pip_command_base[0]}' valid?"
            logger.exception(error_message)
            return False, error_message
        except Exception as e:
            error_message = f"[Async] Unexpected error running command '{command_str}': {e}"
            logger.exception(error_message)
            return False, error_message

    # --- Async Wrappers for Core Methods ---

    async def install(
        self,
        package: str,
        index_url: Optional[str] = None,
        force_reinstall: bool = False,
        upgrade: bool = True,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> bool:
        """Async version of install."""
        command = ["install"]
        if upgrade: command.append("--upgrade")
        if force_reinstall: command.append("--force-reinstall")
        if index_url: command.extend(["--index-url", index_url])
        if extra_args: command.extend(extra_args)
        command.append(package)
        success, _ = await self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
        return success

    async def install_if_missing(
        self,
        package: str,
        version_specifier: Optional[str] = None,
        always_update: bool = False,
        index_url: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> bool:
        """Async version of install_if_missing."""
        loop = asyncio.get_running_loop()
        # Use run_in_executor to call the sync logic without blocking
        # It's complex and better to not re-implement it here.
        is_needed, install_target, force = await loop.run_in_executor(
            None, self._sync_pm_instance._check_if_install_is_needed, package, version_specifier, always_update
        )

        if not is_needed:
            logger.info(f"[Async] Requirement for '{package}' already met. Skipping.")
            return True

        return await self.install(
            install_target,
            index_url=index_url,
            upgrade=True,
            force_reinstall=force,
            extra_args=extra_args,
            dry_run=dry_run,
            verbose=verbose,
        )

    async def ensure_packages(
        self,
        requirements: Union[str, Dict[str, Optional[str]], List[str]],
        index_url: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> bool:
        """Async version of ensure_packages."""
        loop = asyncio.get_running_loop()
        # The logic for checking packages is synchronous, so we run it in an executor
        packages_to_process = await loop.run_in_executor(
            None, self._sync_pm_instance._get_packages_to_process, requirements, verbose
        )

        if not packages_to_process:
            logger.debug("[Async]All specified package requirements are already met.")
            return True

        package_list_str = "', '".join(packages_to_process)
        logger.info(f"[Async] Found {len(packages_to_process)} packages requiring installation/update: '{package_list_str}'")
        
        return await self.install_multiple(
            packages=packages_to_process,
            index_url=index_url,
            force_reinstall=False,
            upgrade=True,
            extra_args=extra_args,
            dry_run=dry_run,
            verbose=verbose,
        )

    async def ensure_requirements(
        self,
        requirements_file: str,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> bool:
        """
        Asynchronously ensures that all packages from a requirements.txt file are installed.

        This method parses a requirements file, respecting comments and some pip
        options, and then uses the efficient `async_ensure_packages` method to
        install any missing or outdated packages.

        Note: File parsing is synchronous. The installation part is asynchronous.

        Args:
            requirements_file (str): Path to the requirements.txt file.
            dry_run (bool): If True, simulate installations without making changes.
            verbose (bool): If True, show detailed output during checks and installation.

        Returns:
            bool: True if all requirements were met or successfully installed, False otherwise.
        """
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            logger.error(f"[Async]Requirements file not found: {requirements_file}")
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
            logger.info(f"[Async] No valid requirements found in {requirements_file}. Nothing to do.")
            return True
        
        if verbose:
            logger.info(f"[Async] Found {len(requirements_list)} requirements and options {pip_options} in {requirements_file}.")

        return await self.ensure_packages(
            requirements=requirements_list,
            index_url=None, # Let options from file handle this via extra_args
            extra_args=pip_options,
            dry_run=dry_run,
            verbose=verbose
        )

    async def install_multiple(
        self,
        packages: List[str],
        index_url: Optional[str] = None,
        force_reinstall: bool = False,
        upgrade: bool = True,
        extra_args: Optional[List[str]] = None,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> bool:
        """Async version of install_multiple."""
        if not packages: return True
        command = ["install"]
        if upgrade: command.append("--upgrade")
        if force_reinstall: command.append("--force-reinstall")
        if index_url: command.extend(["--index-url", index_url])
        if extra_args: command.extend(extra_args)
        command.extend(packages)
        success, _ = await self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
        return success
    
    async def uninstall(
        self, package: str, extra_args: Optional[List[str]] = None, dry_run: bool = False, verbose: bool = False
    ) -> bool:
        """Async version of uninstall."""
        command = ["uninstall", "-y", package]
        if extra_args: command.extend(extra_args)
        success, _ = await self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
        return success

    async def uninstall_multiple(
        self, packages: List[str], extra_args: Optional[List[str]] = None, dry_run: bool = False, verbose: bool = False
    ) -> bool:
        """Async version of uninstall_multiple."""
        if not packages: return True
        command = ["uninstall", "-y"] + packages
        if extra_args: command.extend(extra_args)
        success, _ = await self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
        return success

    async def get_package_info(self, package_name: str) -> Optional[str]:
        """Async version of get_package_info."""
        success, output = await self._run_command(
            ["show", package_name], capture_output=True
        )
        return output if success else None

    async def check_vulnerabilities(
        self,
        package_name: Optional[str] = None,
        requirements_file: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
    ) -> Tuple[bool, str]:
        """Async vulnerability check using pip-audit."""
        # This one is a pure subprocess call, so it's a good candidate for a direct async implementation.
        loop = asyncio.get_running_loop()
        # `shutil.which` is sync but very fast, acceptable to call directly.
        pip_audit_exe = await loop.run_in_executor(None, shutil.which, "pip-audit")
        if not pip_audit_exe:
             logger.error("[Async] pip-audit not found.")
             return True, "pip-audit not found."

        command_list = [pip_audit_exe]
        if requirements_file:
            command_list.extend(["-r", requirements_file])
        elif package_name:
             logger.warning("[Async] Checking single package vuln via pip-audit not supported yet.")

        if extra_args: command_list.extend(extra_args)
        command_str = " ".join(command_list)
        logger.info(f"[Async] Running vulnerability check: {command_str}")

        try:
            process = await asyncio.create_subprocess_shell(
                command_str,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()
            stdout_str = stdout.decode("utf-8", errors="ignore")
            stderr_str = stderr.decode("utf-8", errors="ignore")

            if process.returncode == 0:
                 logger.info("[Async] pip-audit: No vulnerabilities found.")
                 return False, stdout_str
            elif process.returncode == 1:
                 logger.warning(f"[Async] pip-audit: Vulnerabilities found!\n{stdout_str}\n{stderr_str}")
                 return True, f"Vulnerabilities found:\n{stdout_str}\n{stderr_str}"
            else:
                 logger.error(f"[Async] pip-audit failed (code {process.returncode}): {command_str}\n{stderr_str}")
                 return True, f"pip-audit error:\n{stderr_str}"
        except Exception as e:
            logger.exception(f"[Async] Failed to run pip-audit: {e}")
            return True, f"Error running pip-audit: {e}"


# --- Module-level Async Functions ---
_default_async_pm = AsyncPackageManager()

async def async_install(package: str, **kwargs: Any) -> bool:
    """Installs a single package asynchronously."""
    return await _default_async_pm.install(package, **kwargs)

async def async_install_if_missing(package: str, **kwargs: Any) -> bool:
    """Conditionally installs a single package asynchronously."""
    return await _default_async_pm.install_if_missing(package, **kwargs)

async def async_ensure_packages(requirements: Union[str, Dict[str, Optional[str]], List[str]], **kwargs: Any) -> bool:
    """Ensures a set of requirements are met asynchronously."""
    return await _default_async_pm.ensure_packages(requirements, **kwargs)

async def async_ensure_requirements(requirements_file: str, **kwargs: Any) -> bool:
    """Ensures requirements from a file are met asynchronously."""
    return await _default_async_pm.ensure_requirements(requirements_file, **kwargs)

async def async_install_multiple(packages: List[str], **kwargs: Any) -> bool:
    """Installs multiple packages asynchronously."""
    return await _default_async_pm.install_multiple(packages, **kwargs)

async def async_uninstall(package: str, **kwargs: Any) -> bool:
    """Uninstalls a single package asynchronously."""
    return await _default_async_pm.uninstall(package, **kwargs)

async def async_uninstall_multiple(packages: List[str], **kwargs: Any) -> bool:
    """Uninstalls multiple packages asynchronously."""
    return await _default_async_pm.uninstall_multiple(packages, **kwargs)

async def async_get_package_info(package_name: str) -> Optional[str]:
    """Gets package details asynchronously."""
    return await _default_async_pm.get_package_info(package_name)

async def async_check_vulnerabilities(**kwargs: Any) -> Tuple[bool, str]:
    """Checks for vulnerabilities asynchronously."""
    return await _default_async_pm.check_vulnerabilities(**kwargs)