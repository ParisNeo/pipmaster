# pipmaster

[![GitHub stars](https://img.shields.io/github/stars/ParisNeo/pipmaster.svg?style=social&label=Stars)](https://github.com/ParisNeo/pipmaster)
[![PyPI version](https://badge.fury.io/py/pipmaster.svg)](https://badge.fury.io/py/pipmaster)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/ParisNeo/pipmaster/blob/main/LICENSE)


# PipMaster

PipMaster is a Python package manager utility that simplifies package installation, updating, and information retrieval.

## Installation

```
pip install pipmaster
```

## Usage

```python
import pipmaster as pm

# Install a package
pm.install("requests")

# Install a specific version
pm.install_version("numpy", "1.21.0")

# Check if a package is installed
if pm.is_installed("scipy"):
    print("SciPy is installed!")

# Get package info
info = pm.get_package_info("matplotlib")
if info:
    print(info)

# Install or update a package
pm.install_or_update("pandas")
```

## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

