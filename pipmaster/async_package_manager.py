# -*- coding: utf-8 -*-
"""
Asynchronous Package Manager using pip.

Provides an async class and functions to interact with pip asynchronously.

Author: ParisNeo
Created: 23/04/2025
Last Updated: 23/04/2025
"""

import asyncio
import sys
import importlib.metadata
import ascii_colors as logging
import shutil
from typing import Optional, List, Tuple, Union, Dict, Any

# Assuming synchronous PackageManager provides necessary logic structure
from .package_manager import PackageManager # Reuse structure/logic where possible

logger = logging.getLogger(__name__) # Use the same logger hierarchy


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
        logger.info(f"[Async] Initialized for Python: {self.target_python_executable}")

    async def _run_command(
        self, command: List[str], capture_output: bool = False, dry_run: bool = False
    ) -> Tuple[bool, str]:
        """
        Runs a command asynchronously using asyncio.create_subprocess_shell.

        Args:
            command (list): Command arguments.
            capture_output (bool): Capture stdout/stderr.
            dry_run (bool): Simulate the command if applicable.

        Returns:
            tuple: (bool: success, str: output or error message)
        """
        full_command_list = self.pip_command_base + command
        command_str = " ".join(full_command_list)

        if dry_run:
             # Add backend-specific dry-run flags (only pip known for now)
             if command[0] in ["install", "uninstall", "download"]:
                insert_pos = -1
                for i, arg in enumerate(command):
                    if i > 0 and not arg.startswith('-'): insert_pos = i; break
                if insert_pos != -1:
                    dry_run_cmd_list = self.pip_command_base + command[:insert_pos] + ["--dry-run"] + command[insert_pos:]
                else:
                    dry_run_cmd_list = self.pip_command_base + command + ["--dry-run"]
                command_str = " ".join(dry_run_cmd_list)
                logger.info(f"[Async] DRY RUN execution: {command_str}")
                return True, f"Dry run: Command would be '{command_str}'"
             else:
                logger.warning(f"[Async] Dry run not applicable to command: {command[0]}. Executing normally.")
                # Fall through

        logger.info(f"[Async] Executing: {command_str}")
        try:
            process = await asyncio.create_subprocess_shell(
                command_str,
                stdout=asyncio.subprocess.PIPE if capture_output else None,
                stderr=asyncio.subprocess.PIPE if capture_output else None,
            )
            stdout, stderr = await process.communicate()
            stdout_str = stdout.decode("utf-8", errors="ignore") if stdout else ""
            stderr_str = stderr.decode("utf-8", errors="ignore") if stderr else ""

            if process.returncode == 0:
                logger.info(f"[Async] Command succeeded: {command_str}")
                return True, stdout_str or "Command executed successfully."
            else:
                error_message = f"[Async] Command failed (code {process.returncode}): {command_str}"
                if capture_output:
                    error_message += f"\n--- stdout ---\n{stdout_str}\n--- stderr ---\n{stderr_str}"
                else:
                    error_message += "\nCheck console output for stderr."
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
    # These mostly call _run_command with appropriate args, mirroring sync versions

    async def install(self, *args: Any, **kwargs: Any) -> bool:
        """Async version of install."""
        # Need to replicate the command building logic from sync version
        package = args[0] if args else kwargs.get("package")
        command = ["install", package]
        if kwargs.get("upgrade", True): command.append("--upgrade")
        if kwargs.get("force_reinstall", False): command.append("--force-reinstall")
        if index_url := kwargs.get("index_url"): command.extend(["--index-url", index_url])
        if extra_args := kwargs.get("extra_args"): command.extend(extra_args)
        success, _ = await self._run_command(command, dry_run=kwargs.get("dry_run", False))
        return success

    async def install_if_missing(self, *args: Any, **kwargs: Any) -> bool:
        """Async version of install_if_missing."""
        # This is more complex as it involves sync checks (is_installed)
        # Option 1: Make is_installed async (but it uses sync importlib.metadata)
        # Option 2: Run sync checks in executor
        # Option 3: Re-implement check logic here (simplest for now)

        # *** Simplified Implementation - Full logic needs careful porting ***
        logger.warning("[Async] install_if_missing async checks are simplified/not fully ported.")
        pkg_name = args[0] if args else kwargs.get("package") # Basic name extraction

        # Run sync check in executor for correctness without blocking event loop
        loop = asyncio.get_running_loop()
        sync_pm = PackageManager(self.target_python_executable) # Temp sync instance
        is_inst = await loop.run_in_executor(None, sync_pm.is_installed, pkg_name) # Crude check

        if is_inst and not kwargs.get("always_update") and not kwargs.get("version_specifier"):
             logger.info(f"[Async] {pkg_name} likely installed and no update forced. Skipping.")
             return True
        else:
            logger.info(f"[Async] {pkg_name} missing or update required. Proceeding with install.")
            # Call async install, passing relevant args through
            return await self.install(*args, **kwargs) # Reuse async install

    # ... Implement async versions for *all* other methods ...
    # (install_multiple, install_version, uninstall, get_package_info, etc.)
    # Remember to handle dry_run=kwargs.get("dry_run", False)

    # Example: async check_vulnerabilities
    async def check_vulnerabilities(
        self,
        package_name: Optional[str] = None,
        requirements_file: Optional[str] = None,
        extra_args: Optional[List[str]] = None,
    ) -> Tuple[bool, str]:
        """Async vulnerability check using pip-audit."""
        pip_audit_exe = shutil.which("pip-audit")
        if not pip_audit_exe:
             logger.error("[Async] pip-audit not found.")
             return True, "pip-audit not found."

        command = [pip_audit_exe]
        if requirements_file:
            command.extend(["-r", requirements_file])
        elif package_name:
             logger.warning("[Async] Checking single package vuln via pip-audit not supported yet.")

        if extra_args: command.extend(extra_args)
        audit_command_str = " ".join(command)
        logger.info(f"[Async] Running vulnerability check: {audit_command_str}")

        try:
            process = await asyncio.create_subprocess_shell(
                audit_command_str,
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
                 logger.error(f"[Async] pip-audit failed (code {process.returncode}): {audit_command_str}\n{stderr_str}")
                 return True, f"pip-audit error:\n{stderr_str}"
        except Exception as e:
            logger.exception(f"[Async] Failed to run pip-audit: {e}")
            return True, f"Error running pip-audit: {e}"

    # Note: is_installed, get_installed_version, is_version_compatible remain sync
    # as they use sync importlib.metadata. Run them via loop.run_in_executor if needed in async context.


# --- Module-level Async Functions ---
_default_async_pm = AsyncPackageManager()

async def async_install(*args: Any, **kwargs: Any) -> bool:
    return await _default_async_pm.install(*args, **kwargs)

async def async_install_if_missing(*args: Any, **kwargs: Any) -> bool:
    # Needs careful implementation as noted above
    return await _default_async_pm.install_if_missing(*args, **kwargs)

async def async_check_vulnerabilities(*args: Any, **kwargs: Any) -> Tuple[bool, str]:
    return await _default_async_pm.check_vulnerabilities(*args, **kwargs)

# ... Add wrappers for all other async methods ...