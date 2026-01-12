import os
import sys
import shutil
import subprocess
import platform
import logging
from pathlib import Path

import pipmaster as pm

# ----------------------------------------------------------------------
# Configuration ---------------------------------------------------------
# ----------------------------------------------------------------------
TARGET_PYTHON_VERSION = "3.10"          # Desired portable Python version (e.g., "3.10", "3.12")
VENV_ROOT = Path("./my_special_venv")   # Where the virtual environment will live
SCRIPT_PATH = VENV_ROOT / "run_me.py"    # Script that will be executed inside the venv

# Packages we want to have inside the venv
PACKAGES = [
    "rich",                # pretty terminal output
    "requests>=2.28",      # example HTTP library
    "numpy==1.26.4",       # pinned version example
]

# ----------------------------------------------------------------------
# Helper functions ------------------------------------------------------
# ----------------------------------------------------------------------
def create_sample_script(path: Path):
    """Write a tiny Python script that prints its interpreter and a message."""
    script_content = """#!/usr/bin/env python
import sys
import platform
import rich

print(f"Running inside: {sys.executable}")
print(f"Python {platform.python_version()} on {platform.system()}")
rich.print("[bold green]Hello from the custom venv![/bold green]")
"""
    path.write_text(script_content, encoding="utf-8")
    # Make it executable on *nix
    if os.name != "nt":
        path.chmod(0o755)

def run_in_venv(python_exe: str, script: Path):
    """Execute a script using the given Python executable."""
    subprocess.run([python_exe, str(script)], check=False)

# ----------------------------------------------------------------------
# Main workflow ---------------------------------------------------------
# ----------------------------------------------------------------------
def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger(__name__)

    # 1️⃣ Ensure the target directory is clean (optional)
    if VENV_ROOT.exists():
        logger.info(f"Removing existing venv at {VENV_ROOT}")
        shutil.rmtree(VENV_ROOT)

    # 2️⃣ Build a PackageManager that targets the requested portable Python version
    # This will download the portable Python if not present and create a venv for us.
    try:
        pm_instance = pm.get_pip_manager_for_version(TARGET_PYTHON_VERSION, str(VENV_ROOT))
    except RuntimeError as e:
        logger.error(f"Failed to bootstrap portable Python {TARGET_PYTHON_VERSION}: {e}")
        sys.exit(1)

    logger.info(f"Portable Python {TARGET_PYTHON_VERSION} ready. "
                f"Using interpreter: {pm_instance.target_python_executable}")

    # 3️⃣ Install the desired libraries inside the freshly created venv
    logger.info(f"Installing packages {PACKAGES} into the venv...")
    if not pm_instance.install_multiple(PACKAGES, verbose=True):
        logger.error("Package installation failed.")
        sys.exit(1)

    # 4️⃣ Create a small script that will run inside the environment
    logger.info(f"Creating sample script at {SCRIPT_PATH}")
    create_sample_script(SCRIPT_PATH)

    # 5️⃣ Launch the script using the venv's python interpreter
    logger.info("Running the sample script inside the custom environment:")
    run_in_venv(pm_instance.target_python_executable, SCRIPT_PATH)

    logger.info("Example finished successfully.")

    logger.info("Cleaning.")
    pm.remove_venv(str(VENV_ROOT))


if __name__ == "__main__":
    main()
