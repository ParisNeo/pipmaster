# -*- coding: utf-8 -*-
"""
Portable Python version management.

Provides PythonVersionManager for downloading and managing
portable Python versions from python-build-standalone releases.

Author: ParisNeo
Created: 01/04/2024
Last Updated: 13/02/2026
"""

import os
import shutil
import platform
import tempfile
import urllib.request
import urllib.error
import tarfile
import zipfile
from pathlib import Path
from typing import Optional, Tuple

import ascii_colors as logging

logger = logging.getLogger(__name__)


def clear_portable_python_cache() -> bool:
    """
    Clears the entire cache of downloaded portable Python versions.
    Deletes the contents of ~/.pipmaster/python_versions.

    Returns:
        bool: True if successful, False on failure.
    """
    return PythonVersionManager().clear_cache()


class PythonVersionManager:
    """
    Manages portable Python versions natively by downloading and extracting
    pre-compiled standalone builds (via indygreg/python-build-standalone).
    Does NOT require 'uv' or other external tools.
    """
    
    # Base URL for a stable release of python-build-standalone. 
    # Using 20251217 release tag.
    BASE_URL_TEMPLATE = "https://github.com/astral-sh/python-build-standalone/releases/download/20251217/cpython-{version}+20251217-{arch}-{os}-install_only.tar.gz"
    
    # Mapping for the 20251217 release
    VERSION_MAP = {
        "3.10": "3.10.19",
        "3.11": "3.11.14",
        "3.12": "3.12.12",
        "3.13": "3.13.10",
        "3.14": "3.14.1",
        "3.9": "3.9.24"
    }

    def __init__(self):
        self.base_dir = Path.home() / ".pipmaster" / "python_versions"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_platform_info(self) -> Tuple[str, str]:
        """Returns (arch, os) strings suitable for the build URL."""
        machine = platform.machine().lower()
        system = platform.system().lower()

        # Architecture mapping
        if machine in ["x86_64", "amd64"]:
            arch = "x86_64"
        elif machine in ["aarch64", "arm64"]:
            arch = "aarch64"
        elif machine in ["i386", "i686", "x86"]:
            arch = "i686"
        else:
            raise RuntimeError(f"Unsupported architecture: {machine}")

        # OS mapping and suffix
        if system == "linux":
            os_str = "unknown-linux-gnu"
        elif system == "darwin":
            os_str = "apple-darwin"
        elif system == "windows":
            os_str = "pc-windows-msvc"
        else:
            raise RuntimeError(f"Unsupported OS: {system}")

        return arch, os_str

    def _get_download_url(self, version: str) -> str:
        """Constructs the download URL for the requested version and current platform."""
        arch, os_str = self._get_platform_info()
        return self.BASE_URL_TEMPLATE.format(version=version, arch=arch, os=os_str)
    
    def _resolve_version(self, version: str) -> str:
        """Resolves a short version string (e.g. '3.10') to the full version in the map."""
        return self.VERSION_MAP.get(version, version)

    def install_version(self, version: str) -> bool:
        """
        Downloads and installs a specific Python version (e.g., '3.12.9').
        
        Args:
            version (str): The specific Python version to install.
            
        Returns:
            bool: True if successful or already installed.
        """
        target_version = self._resolve_version(version)
        install_dir = self.base_dir / target_version
        
        if install_dir.exists():
            if self._find_python_in_dir(install_dir):
                logger.info(f"Python {target_version} is already installed at {install_dir}")
                return True
            else:
                logger.warning(f"Found directory for {target_version} but it seems corrupt. Re-installing.")
                shutil.rmtree(install_dir)

        url = self._get_download_url(target_version)
        logger.info(f"Downloading Python {target_version} from {url}...")
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".tar.gz") as tmp_file:
                req = urllib.request.Request(
                    url, 
                    headers={'User-Agent': 'pipmaster-installer/1.0'}
                )
                try:
                    with urllib.request.urlopen(req) as response:
                        shutil.copyfileobj(response, tmp_file)
                except urllib.error.HTTPError as e:
                    logger.error(f"HTTP Error downloading Python: {e.code} {e.reason}")
                    logger.error(f"URL Attempted: {url}")
                    return False
                except Exception as e:
                    logger.error(f"Failed to download from {url}: {e}")
                    return False
                tmp_path = Path(tmp_file.name)

            logger.info("Extracting...")
            try:
                with tempfile.TemporaryDirectory() as extract_tmp:
                    if url.endswith(".zip"):
                         with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                            zip_ref.extractall(extract_tmp)
                    else:
                        with tarfile.open(tmp_path, "r:*") as tar:
                            tar.extractall(extract_tmp)
                    
                    extracted_root = Path(extract_tmp)
                    content_dir = extracted_root / "python"
                    if not content_dir.exists():
                        content_dir = extracted_root
                    
                    install_dir.parent.mkdir(parents=True, exist_ok=True)
                    
                    if install_dir.exists():
                         shutil.rmtree(install_dir, ignore_errors=True)

                    shutil.move(str(content_dir), str(install_dir))
                    
            finally:
                if tmp_path.exists():
                    try:
                        tmp_path.unlink()
                    except Exception:
                        pass
            
            logger.info(f"Python {target_version} installed successfully.")
            return True

        except Exception as e:
            logger.error(f"Installation failed for {target_version}: {e}")
            if install_dir.exists():
                shutil.rmtree(install_dir, ignore_errors=True)
            return False

    def remove_version(self, version: str) -> bool:
        """
        Removes a specific portable Python version from the cache.

        Args:
            version (str): The version to remove (e.g., "3.12" or "3.12.12").
        
        Returns:
            bool: True if removed or didn't exist, False on error.
        """
        target_version = self._resolve_version(version)
        install_dir = self.base_dir / target_version

        if not install_dir.exists():
            logger.info(f"Portable Python {target_version} not found in cache.")
            return True

        try:
            shutil.rmtree(install_dir)
            logger.info(f"Portable Python {target_version} removed from cache.")
            return True
        except Exception as e:
            logger.error(f"Failed to remove Python {target_version}: {e}")
            return False

    def clear_cache(self) -> bool:
        """
        Clears the entire cache of downloaded portable Python versions.
        
        Returns:
            bool: True if successful, False on failure.
        """
        if not self.base_dir.exists():
            return True
            
        try:
            shutil.rmtree(self.base_dir)
            self.base_dir.mkdir(parents=True, exist_ok=True)
            logger.info("Portable Python cache cleared successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to clear portable Python cache: {e}")
            return False

    def _find_python_in_dir(self, directory: Path) -> Optional[str]:
        """Finds the python executable inside a directory."""
        if platform.system() == "Windows":
            candidates = [directory / "python.exe", directory / "Scripts" / "python.exe"]
        else:
            candidates = [directory / "bin" / "python3", directory / "bin" / "python"]
            
        for cand in candidates:
            if cand.exists():
                if platform.system() != "Windows" and not os.access(cand, os.X_OK):
                     continue
                return str(cand)
        
        return None

    def get_executable_path(self, version: str, auto_install: bool = True) -> Optional[str]:
        """
        Finds the executable path for a specific Python version.
        
        Args:
            version (str): The Python version (e.g., "3.12" or "3.12.9").
            auto_install (bool): If True, attempts to download if missing.
        """
        target_version = self._resolve_version(version)
        install_dir = self.base_dir / target_version
        
        exe = self._find_python_in_dir(install_dir)
        if exe:
            return exe
            
        if auto_install:
            logger.info(f"Portable Python {target_version} not found locally. Installing...")
            if self.install_version(version):
                return self._find_python_in_dir(install_dir)
        
        return None
