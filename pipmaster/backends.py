# -*- coding: utf-8 -*-
"""
Alternative package manager backends.

Provides UvPackageManager and CondaPackageManager for
managing packages through 'uv' and 'conda' respectively.

Author: ParisNeo
Created: 01/04/2024
Last Updated: 13/02/2026
"""

import subprocess
import shutil
import platform
from typing import Optional, List, Tuple, Any

import ascii_colors as logging

logger = logging.getLogger(__name__)


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
        command = ["venv", f'"{path}"']
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
        Executes a tool in a temporary environment using `uv tool run`.
        """
        if not command:
            logger.error("run_with_uvx requires a command to execute.")
            return False

        uvx_command = ["tool", "run"] + command
        success, _ = self._run_command(
            uvx_command, verbose=verbose, capture_output=False
        )
        return success


class CondaPackageManager:
    def __init__(self, environment_name_or_path: Optional[str] = None):
        logger.warning("CondaPackageManager is not yet implemented.")
        raise NotImplementedError("Conda backend support is not yet implemented.")
