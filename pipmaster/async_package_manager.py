# pipmaster/async_package_manager.py

# -*- coding: utf-8 -*-
"""
Asynchronous Package Manager using pip with enhanced visual feedback.

Provides async class and functions with ASCIIColors status indicators.

Author: ParisNeo
Created: 23/04/2025
Last Updated: 13/02/2026
"""

import asyncio
import sys
import importlib.metadata
import ascii_colors as logging
from ascii_colors import ASCIIColors
import shutil
import shlex
from typing import Optional, List, Tuple, Union, Dict, Any

from .core import PackageManager, EMOJI
from .factories import get_pip_manager_for_version

logger = logging.getLogger(__name__)


class AsyncPackageManager:
    """
    Manages Python package installations and queries using pip asynchronously.
    Enhanced with ASCIIColors visual feedback.
    """
    def __init__(
        self,
        python_executable: Optional[str] = None,
        pip_command_base: Optional[List[str]] = None,
        venv_path: Optional[str] = None,
    ):
        sync_pm = PackageManager(python_executable, pip_command_base, venv_path=venv_path)
        self.pip_command_base = sync_pm.pip_command_base
        self.target_python_executable = sync_pm.target_python_executable
        self._sync_pm_instance = sync_pm
        logger.debug(f"{EMOJI['info']} [Async] Initialized for: {self.target_python_executable}")

    async def _run_command(
        self, command: List[str], capture_output: bool = False, dry_run: bool = False, verbose: bool = False
    ) -> Tuple[bool, str]:
        """Runs a command asynchronously with optional visual feedback."""
        if dry_run:
            success, output = self._sync_pm_instance._run_command(command, dry_run=True)
            return success, output

        command_str = " ".join(self.pip_command_base + command)
        logger.info(f"{EMOJI['gear']} [Async] Executing: {command_str}")

        try:
            stdout_pipe = asyncio.subprocess.PIPE if capture_output or verbose else asyncio.subprocess.DEVNULL
            stderr_pipe = asyncio.subprocess.PIPE if capture_output or verbose else asyncio.subprocess.DEVNULL

            if verbose and not capture_output:
                stdout_pipe = asyncio.subprocess.PIPE
                stderr_pipe = asyncio.subprocess.STDOUT

            process = await asyncio.create_subprocess_shell(
                command_str,
                stdout=stdout_pipe,
                stderr=stderr_pipe,
            )

            if verbose and not capture_output:
                while True:
                    line = await process.stdout.readline()
                    if not line:
                        break
                    print(line.decode().strip())
                await process.wait()
                stdout_str, stderr_str = "", ""
            else:
                stdout, stderr = await process.communicate()
                stdout_str = stdout.decode("utf-8", errors="ignore") if stdout else ""
                stderr_str = stderr.decode("utf-8", errors="ignore") if stderr else ""

            if process.returncode == 0:
                if verbose:
                    logger.info(f"{EMOJI['check']} [Async] Command succeeded")
                else:
                    logger.debug(f"{EMOJI['check']} [Async] Command succeeded")
                return True, stdout_str or "Command executed successfully."
            else:
                error_message = f"{EMOJI['cross']} [Async] Command failed (code {process.returncode})"
                if stdout_str: error_message += f"\n--- stdout ---\n{stdout_str.strip()}"
                if stderr_str: error_message += f"\n--- stderr ---\n{stderr_str.strip()}"
                logger.error(error_message)
                return False, error_message
                
        except FileNotFoundError:
            error_message = f"{EMOJI['cross']} [Async] Error: Command failed. Is '{self.pip_command_base[0]}' valid?"
            logger.exception(error_message)
            return False, error_message
        except Exception as e:
            error_message = f"{EMOJI['cross']} [Async] Unexpected error: {e}"
            logger.exception(error_message)
            return False, error_message

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
        """Async install with visual feedback."""
        command = ["install"]
        if upgrade: command.append("--upgrade")
        if force_reinstall: command.append("--force-reinstall")
        if index_url: command.extend(["--index-url", index_url])
        if extra_args: command.extend(extra_args)
        command.append(package)

        action_emoji = EMOJI['update'] if upgrade else EMOJI['install']
        action_text = "Updating" if upgrade else "Installing"
        msg = f"{action_emoji} [Async] {action_text}: {package}"

        if verbose or dry_run:
            logger.info(msg)
            success, _ = await self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
            if success:
                logger.info(f"{EMOJI['sparkles']} [Async] Successfully handled: {package}")
            else:
                logger.error(f"{EMOJI['cross']} [Async] Failed to handle: {package}")
        else:
            with ASCIIColors.status(msg, spinner="dots", spinner_style="bold cyan") as status:
                success, _ = await self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
                if success:
                    logger.debug(f"{EMOJI['sparkles']} [Async] Successfully handled: {package}")
                else:
                    logger.error(f"{EMOJI['cross']} [Async] Failed to handle: {package}")

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
        """Async conditional install with visual feedback."""
        loop = asyncio.get_running_loop()
        # We must pass the verbose argument as a keyword argument because run_in_executor
        # only takes *args. We use functools.partial or lambda, but here we can just
        # construct the call carefully.
        # Since _check_if_install_is_needed signature is (package, version_specifier, always_update, verbose)
        # We can pass them positionally.
        is_needed, install_target, force = await loop.run_in_executor(
            None, 
            self._sync_pm_instance._check_if_install_is_needed, 
            package, 
            version_specifier, 
            always_update, 
            verbose
        )

        if not is_needed:
            logger.debug(f"{EMOJI['check']} [Async] '{package}' already satisfied. Skipping.")
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
        progress_callback: Optional[callable] = None,
    ) -> bool:
        """Async ensure with pleasant batch feedback."""
        loop = asyncio.get_running_loop()
        
        # Define a wrapper to call async callback from sync context
        def sync_progress_wrapper(data):
            if progress_callback and asyncio.iscoroutinefunction(progress_callback):
                # Schedule the async callback on the event loop
                try:
                    loop.call_soon_threadsafe(lambda: asyncio.create_task(progress_callback(data)))
                except Exception:
                    pass
            elif progress_callback:
                progress_callback(data)
        
        packages_to_process = await loop.run_in_executor(
            None, self._sync_pm_instance._get_packages_to_process, requirements, False, verbose, sync_progress_wrapper
        )

        if not packages_to_process:
            msg = f"{EMOJI['check']} [Async] All requirements satisfied."
            logger.debug(msg)
            if progress_callback:
                if asyncio.iscoroutinefunction(progress_callback):
                    await progress_callback({"status": "complete", "message": msg, "packages": []})
                else:
                    progress_callback({"status": "complete", "message": msg, "packages": []})
            return True

        pkg_list_str = "', '".join(packages_to_process)
        if verbose:
            logger.info(f"{EMOJI['package']} [Async] Processing {len(packages_to_process)} packages: '{pkg_list_str}'")
        else:
            logger.debug(f"{EMOJI['package']} [Async] Processing {len(packages_to_process)} packages.")
        
        if progress_callback:
            data = {
                "status": "processing",
                "message": f"Installing {len(packages_to_process)} package(s)",
                "packages": packages_to_process,
                "count": len(packages_to_process)
            }
            if asyncio.iscoroutinefunction(progress_callback):
                await progress_callback(data)
            else:
                progress_callback(data)

        result = await self.install_multiple(
            packages=packages_to_process,
            index_url=index_url,
            force_reinstall=False,
            upgrade=True,
            extra_args=extra_args,
            dry_run=dry_run,
            verbose=verbose,
        )
        
        if progress_callback:
            data = {
                "status": "complete" if result else "failed",
                "message": "Installation complete" if result else "Installation failed",
                "packages": packages_to_process,
                "success": result
            }
            if asyncio.iscoroutinefunction(progress_callback):
                await progress_callback(data)
            else:
                progress_callback(data)
        
        return result

    async def ensure_requirements(
        self,
        requirements_file: str,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> bool:
        """Async requirements.txt processing."""
        try:
            with open(requirements_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            logger.error(f"{EMOJI['cross']} [Async] Requirements file not found: {requirements_file}")
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
            logger.debug(f"{EMOJI['info']} [Async] No requirements in {requirements_file}")
            return True
        
        if verbose:
            logger.info(f"{EMOJI['package']} [Async] Processing {len(requirements_list)} requirements from {requirements_file}")

        return await self.ensure_packages(
            requirements=requirements_list,
            index_url=None,
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
        """Async batch install with progress feedback."""
        if not packages: 
            return True

        msg = f"{EMOJI['rocket']} [Async] Installing batch of {len(packages)} package(s)..."

        command = ["install"]
        if upgrade: command.append("--upgrade")
        if force_reinstall: command.append("--force-reinstall")
        if index_url: command.extend(["--index-url", index_url])
        if extra_args: command.extend(extra_args)
        command.extend(packages)
        
        if verbose or dry_run:
            logger.info(msg)
            success, _ = await self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
            if success:
                logger.info(f"{EMOJI['sparkles']} [Async] Batch complete: {len(packages)} package(s)")
            else:
                logger.error(f"{EMOJI['cross']} [Async] Batch failed")
        else:
            with ASCIIColors.status(msg, spinner="star", spinner_style="bold green") as status:
                success, _ = await self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
                if success:
                    logger.debug(f"{EMOJI['sparkles']} [Async] Batch complete: {len(packages)} package(s)")
                else:
                    logger.error(f"{EMOJI['cross']} [Async] Batch failed")

        return success
    
    async def uninstall(
        self, package: str, extra_args: Optional[List[str]] = None, dry_run: bool = False, verbose: bool = False
    ) -> bool:
        """Async uninstall with visual feedback."""
        msg = f"{EMOJI['remove']} [Async] Removing: {package}"
        
        command = ["uninstall", "-y", package]
        if extra_args: command.extend(extra_args)
        
        if verbose or dry_run:
            logger.info(msg)
            success, _ = await self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
            if success:
                logger.info(f"{EMOJI['check']} [Async] Successfully removed: {package}")
            else:
                logger.error(f"{EMOJI['cross']} [Async] Failed to remove: {package}")
        else:
            with ASCIIColors.status(msg, spinner="pulse", spinner_style="bold red") as status:
                success, _ = await self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
                if success:
                    logger.debug(f"{EMOJI['check']} [Async] Successfully removed: {package}")
                else:
                    logger.error(f"{EMOJI['cross']} [Async] Failed to remove: {package}")

        return success

    async def uninstall_multiple(
        self, packages: List[str], extra_args: Optional[List[str]] = None, dry_run: bool = False, verbose: bool = False
    ) -> bool:
        """Async batch uninstall."""
        if not packages: return True

        msg = f"{EMOJI['remove']} [Async] Removing {len(packages)} package(s)..."
        
        command = ["uninstall", "-y"] + packages
        if extra_args: command.extend(extra_args)
        
        if verbose or dry_run:
            logger.info(msg)
            success, _ = await self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
            if success:
                logger.info(f"{EMOJI['check']} [Async] Batch removal complete")
            else:
                logger.error(f"{EMOJI['cross']} [Async] Some packages could not be removed")
        else:
            with ASCIIColors.status(msg, spinner="pulse", spinner_style="bold red") as status:
                success, _ = await self._run_command(command, dry_run=dry_run, verbose=verbose, capture_output=False)
                if success:
                    logger.debug(f"{EMOJI['check']} [Async] Batch removal complete")
                else:
                    logger.error(f"{EMOJI['cross']} [Async] Some packages could not be removed")

        return success

    async def get_package_info(self, package_name: str) -> Optional[str]:
        """Async package info retrieval."""
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
        """Async vulnerability check with visual feedback."""
        loop = asyncio.get_running_loop()
        pip_audit_exe = await loop.run_in_executor(None, shutil.which, "pip-audit")
        
        if not pip_audit_exe:
            logger.warning(f"{EMOJI['warning']} [Async] pip-audit not found")
            return True, "pip-audit not found"

        command_list = [pip_audit_exe]
        if requirements_file:
            command_list.extend(["-r", requirements_file])
        elif package_name:
            logger.warning(f"{EMOJI['warning']} [Async] Single package check not supported")

        if extra_args: command_list.extend(extra_args)
        command_str = " ".join(command_list)
        logger.info(f"{EMOJI['shield']} [Async] Running security scan")

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
                logger.info(f"{EMOJI['check']} [Async] No vulnerabilities found")
                return False, stdout_str
            elif process.returncode == 1:
                logger.warning(f"{EMOJI['warning']} [Async] Vulnerabilities detected!")
                return True, f"Vulnerabilities:\n{stdout_str}\n{stderr_str}"
            else:
                logger.error(f"{EMOJI['cross']} [Async] pip-audit failed")
                return True, f"Error:\n{stderr_str}"
                
        except Exception as e:
            logger.exception(f"{EMOJI['cross']} [Async] Failed to run pip-audit: {e}")
            return True, f"Error: {e}"


# --- Module-level Async Functions ---
_default_async_pm = AsyncPackageManager()

async def async_install(package: str, **kwargs: Any) -> bool:
    """Installs a single package asynchronously."""
    return await _default_async_pm.install(package, **kwargs)

async def async_install_if_missing(package: str, **kwargs: Any) -> bool:
    """Conditionally installs a single package asynchronously."""
    return await _default_async_pm.install_if_missing(package, **kwargs)

async def async_ensure_packages(
    requirements: Union[str, Dict[str, Optional[str]], List[str]],
    index_url: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
    dry_run: bool = False,
    verbose: bool = False,
    progress_callback: Optional[callable] = None,
) -> bool:
    """Ensures a set of requirements are met asynchronously."""
    return await _default_async_pm.ensure_packages(
        requirements=requirements,
        index_url=index_url,
        extra_args=extra_args,
        dry_run=dry_run,
        verbose=verbose,
        progress_callback=progress_callback,
    )

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

def get_async_pip_manager_for_version(target_python_version: str, venv_path: str) -> AsyncPackageManager:
    """Creates an AsyncPackageManager targeting a specific portable Python version."""
    try:
        sync_pm = get_pip_manager_for_version(target_python_version, venv_path)
    except RuntimeError as e:
        logger.error(f"{EMOJI['cross']} Failed to initialize async manager: {e}")
        raise
        
    return AsyncPackageManager(
        python_executable=sync_pm.target_python_executable,
        venv_path=venv_path
    )
