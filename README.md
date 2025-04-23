# pipmaster

[![GitHub stars](https://img.shields.io/github/stars/ParisNeo/pipmaster.svg?style=social&label=Stars)](https://github.com/ParisNeo/pipmaster)
[![PyPI version](https://badge.fury.io/py/pipmaster.svg)](https://badge.fury.io/py/pipmaster)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/ParisNeo/pipmaster/blob/main/LICENSE)
[![Python Versions](https://img.shields.io/pypi/pyversions/pipmaster.svg)](https://pypi.org/project/pipmaster/)


## PipMaster

PipMaster is a versatile Python package manager utility designed to simplify package installation, updating, uninstallation, and information retrieval programmatically. Built on top of `pip`, it leverages modern libraries like `importlib.metadata` and `packaging` for robust package checking.

### Features

- Install packages with options for upgrades, forced reinstalls, custom index URLs, and extra arguments.
- Install specific package versions.
- **Install multiple packages only if they are not already present.** (`install_multiple_if_not_installed`)
- Install packages in editable mode (`-e`).
- Install multiple packages at once or from a requirements file.
- **Check if packages are installed using `importlib.metadata`.**
- **Get installed versions using `importlib.metadata`.**
- **Check if an installed version meets a PEP 440 version specifier (e.g., `>=1.0`, `==2.3.4`) using `is_version_compatible`.**
- Retrieve package metadata using `pip show`.
- Update or install packages conditionally (`install_or_update`, `install_if_missing`).
- Uninstall single or multiple packages.
- Flexible and reusable `PackageManager` class with module-level convenience functions.
- Basic logging for executed commands and errors.

## Installation

Install PipMaster via pip:
```bash
pip install pipmaster
```
It requires Python 3.7+ and the `packaging` library.

## Usage

Import `pipmaster` and use either the module-level functions or instantiate the `PackageManager` class.

```python
import pipmaster as pm
from pipmaster import PackageManager

# Use module-level functions (default instance)
pm.install("requests")

# Or create your own instance (e.g., for different python env)
# custom_pm = PackageManager(python_executable="/path/to/venv/bin/python")
# custom_pm.install("numpy")
```

### Basic Installation
```python
# Install latest (or upgrade if installed)
pm.install("requests")

# Install without upgrade flag
pm.install("numpy", upgrade=False)

# Force reinstall
pm.install("pandas", force_reinstall=True)

# Install from custom index
pm.install("torch", index_url="https://download.pytorch.org/whl/cu121")

# Install with extra pip arguments
pm.install("scipy", extra_args=["--no-cache-dir"])
```

### Installing Specific Versions
```python
# Install exact version
pm.install_version("numpy", "1.21.5")

# Force reinstall specific version
pm.install_version("requests", "2.28.1", force_reinstall=True)
```

### Conditional Installation (`install_if_missing`)
```python
# Install latest if not present
pm.install_if_missing("scipy")

# Install specific version only if missing or wrong version installed
pm.install_if_missing("numpy", version="1.26.4", enforce_version=True)

# Install if missing, or update to latest if present
pm.install_if_missing("torch", always_update=True, index_url="https://download.pytorch.org/whl/cu121")
```

### **NEW: Install Multiple Only if Missing**
```python
# Define packages needed
packages = ["requests", "numpy", "pandas"]

# Install only those from the list that are not currently installed
pm.install_multiple_if_not_installed(packages)

# Can also use custom index for the batch
torch_packages = ["torch", "torchvision"]
pm.install_multiple_if_not_installed(torch_packages, index_url="https://download.pytorch.org/whl/cu121")
```

### Editable Mode Installation
```python
pm.install_edit("/path/to/local/package")
```

### Installing Multiple Packages (Install/Update)
```python
packages = ["requests", "numpy", "pandas"]
# Install or update all listed packages
pm.install_multiple(packages)

# Force reinstall all
pm.install_multiple(packages, force_reinstall=True)

# Install/update from custom index
pm.install_multiple(packages, index_url="https://custom-index.com")

# Ensure all are installed or updated (convenience wrapper)
pm.install_or_update_multiple(packages)
```

### Installing from Requirements File
```python
pm.install_requirements("requirements.txt")
pm.install_requirements("dev-requirements.txt", index_url="https://private-repo.com")
```

### Checking Package Status
```python
# Check if installed
if pm.is_installed("scipy"):
    print("SciPy is installed!")

# Get installed version (returns str or None)
version = pm.get_installed_version("matplotlib")
if version:
    print(f"Matplotlib version: {version}")
else:
    print("Matplotlib not installed.")

# Check if version meets specifier
if pm.is_version_compatible("requests", ">=2.25.0"):
     print("Requests version is compatible.")

if pm.is_version_compatible("numpy", "==1.21.5"):
     print("Numpy is exactly version 1.21.5.")

# Get detailed package info (runs 'pip show')
info = pm.get_package_info("requests")
if info:
    print(info)
```

### Installing or Updating
```python
# Install if missing, or update if installed
pm.install_or_update("pandas")

# Force reinstall during update
pm.install_or_update("torch", force_reinstall=True, index_url="https://download.pytorch.org/whl/cu121")
```

### Uninstalling Packages
```python
pm.uninstall("requests")
pm.uninstall_multiple(["numpy", "pandas"])
```

### Advanced Example: Managing Complex Dependencies

See `examples/advanced_usage.py` for a script demonstrating:
- Defining requirements with version specifiers and index URLs.
- Checking installed versions against specifiers using `is_version_compatible`.
- Grouping installations by index URL.
- Using `install_or_update_multiple` for targeted updates.

```python
# Snippet from examples/advanced_usage.py
required_packages_dict = {
    "torch": {"index_url": "...", "specifier": ">=2.0.0"},
    "transformers": {"specifier": ">=4.30.0"},
    # ... other packages
}
packages_to_install_or_update = {}
# ... logic to check is_installed and is_version_compatible ...
# ... populate packages_to_install_or_update dictionary {index_url: [list_of_packages]} ...

for index_url, pkgs_to_install in packages_to_install_or_update.items():
    pm.install_or_update_multiple(pkgs_to_install, index_url=index_url)

```

# License
This project is licensed under the Apache 2.0 License - see the LICENSE file for details.