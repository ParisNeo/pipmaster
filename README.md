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


for a more complete  example you can do this:

```python
import pipmaster as pm
import pkg_resources
# Check and install required packages
required_packages = [
    ["torch","","https://download.pytorch.org/whl/cu121"],
    ["diffusers","0.30.1",None],
    ["transformers","4.44.2",None],
    ["accelerate","0.33.0",None],
    ["imageio-ffmpeg","0.5.1",None]
]

for package, min_version, index_url in required_packages:
    if not pm.is_installed(package):
        pm.install_or_update(package, index_url)
    else:
        if min_version:
            if pkg_resources.parse_version(pm.get_installed_version(package))< pkg_resources.parse_version(min_version):
                pm.install_or_update(package, index_url)
```
## License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

