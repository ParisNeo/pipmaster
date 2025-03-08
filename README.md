# pipmaster

[![GitHub stars](https://img.shields.io/github/stars/ParisNeo/pipmaster.svg?style=social&label=Stars)](https://github.com/ParisNeo/pipmaster)
[![PyPI version](https://badge.fury.io/py/pipmaster.svg)](https://badge.fury.io/py/pipmaster)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/ParisNeo/pipmaster/blob/main/LICENSE)

## PipMaster

PipMaster is a versatile Python package manager utility designed to simplify package installation, updating, uninstallation, and information retrieval. It provides a programmatic interface to manage Python packages with support for custom index URLs, version enforcement, editable installs, and more.

### Features

- Install packages with options for upgrades, forced reinstalls, and custom index URLs.
- Install specific package versions or enforce version requirements.
- Install packages in editable mode for development.
- Install multiple packages at once or from a requirements file.
- Check if packages are installed and retrieve their versions or metadata.
- Update or install packages conditionally.
- Uninstall single or multiple packages.
- Flexible and reusable `PackageManager` class with module-level convenience functions.

## Installation

Install PipMaster via pip:
pip install pipmaster

## Usage

Below are examples demonstrating the full range of PipMaster's functionality. Import it as `pipmaster` and use either the module-level functions or the `PackageManager` class directly.

### Basic Package Installation

```python
import pipmaster as pm

# Install a package (latest version by default)
pm.install("requests")

# Install with an upgrade if already installed
pm.install("numpy", upgrade=True)

# Force reinstall even if installed
pm.install("pandas", force_reinstall=True)

# Install from a custom index URL
pm.install("torch", index_url="https://download.pytorch.org/whl/cu121")
```
Installing Specific Versions
```python
# Install a specific version of a package
pm.install_version("numpy", "1.21.0")

# Force reinstall a specific version
pm.install_version("requests", "2.28.1", force_reinstall=True)
```
Conditional Installation
```python
# Install only if missing, with optional version enforcement
pm.install_if_missing("scipy")  # Install latest if not present
pm.install_if_missing("numpy", version="1.26.4", enforce_version=True)  # Ensure exact version
pm.install_if_missing("torch", always_update=True, index_url="https://download.pytorch.org/whl/cu121")  # Always update
```
Editable Mode Installation
```python
# Install a local package in editable mode (-e flag)
pm.install_edit("/path/to/local/package")
```
Installing Multiple Packages
```python
# Install multiple packages at once
packages = ["requests", "numpy", "pandas"]
pm.install_multiple(packages, force_reinstall=True)

# Install or update multiple packages
pm.install_or_update_multiple(packages, index_url="https://custom-index.com")
```
Installing from Requirements File
```python
# Install all packages listed in a requirements.txt file
pm.install_requirements("requirements.txt")
```
Checking Package Status
```python
# Check if a package is installed
if pm.is_installed("scipy"):
    print("SciPy is installed!")

# Get the installed version of a package
version = pm.get_installed_version("matplotlib")
print(f"Matplotlib version: {version}")

# Get detailed package info
pm.get_package_info("requests")  # Outputs pip show info
```
Installing or Updating Packages
```python
# Install a package if missing, or update it if installed
pm.install_or_update("pandas")

# Force reinstall during update
pm.install_or_update("torch", force_reinstall=True, index_url="https://download.pytorch.org/whl/cu121")
```
Uninstalling Packages
```python
# Uninstall a single package
pm.uninstall("requests")

# Uninstall multiple packages
pm.uninstall_multiple(["numpy", "pandas"])
```
Advanced Example: Managing Dependencies with Versions
```python
import pipmaster as pm
import pkg_resources

# List of required packages with minimum versions and optional index URLs
required_packages = [
    # [package, min_version, index_url]
    ["torch", "", "https://download.pytorch.org/whl/cu121"],
    ["diffusers", "0.30.1", None],
    ["transformers", "4.44.2", None],
    ["accelerate", "0.33.0", None],
    ["imageio-ffmpeg", "0.5.1", None]
]

for package, min_version, index_url in required_packages:
    if not pm.is_installed(package):
        pm.install_or_update(package, index_url=index_url)
    elif min_version:
        current_version = pm.get_installed_version(package)
        if pkg_resources.parse_version(current_version) < pkg_resources.parse_version(min_version):
            print(f"Upgrading {package} from {current_version} to at least {min_version}")
            pm.install_or_update(package, index_url=index_url)
```
Using the PackageManager Class Directly
For more control, instantiate PackageManager directly:
```python
from pipmaster import PackageManager

pm = PackageManager()

# Custom pip command (e.g., for virtual environments)
pm_custom = PackageManager(package_manager="/path/to/python -m pip")

# Use any method as shown above
pm.install("requests")
pm_custom.install_version("numpy", "1.21.0")
```

# License
This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

