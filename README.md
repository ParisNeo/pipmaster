# `pipmaster`: The Python Package Management Toolkit

<!-- Badges -->
[![PyPI version](https://badge.fury.io/py/pipmaster.svg)](https://badge.fury.io/py/pipmaster)
[![Python Versions](https://img.shields.io/pypi/pyversions/pipmaster.svg)](https://pypi.org/project/pipmaster/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/ParisNeo/pipmaster/blob/main/LICENSE)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/ParisNeo/pipmaster/docs.yml?branch=main&label=docs)](https://github.com/ParisNeo/pipmaster/actions/workflows/docs.yml)
[![GitHub stars](https://img.shields.io/github/stars/ParisNeo/pipmaster.svg?style=social&label=Stars)](https://github.com/ParisNeo/pipmaster)
[![Documentation Status](https://readthedocs.org/projects/pipmaster/badge/?version=latest)](https://parisneo.github.io/pipmaster/) 

`pipmaster` is a comprehensive Python library for declarative and programmatic package management. It provides a robust, unified interface to multiple package management backends like **`pip`** and **`uv`**, allowing you to automate installations, updates, environment checks, and more, directly from your Python code with both **synchronous and asynchronous APIs**.

Think of it as the swiss army knife for your application's setup scripts, build automation, or any task that requires reliable dependency management.

**View the full documentation at [parisneo.github.io/pipmaster/](https://parisneo.github.io/pipmaster/).**

## Core Philosophy

*   **Declarative & Efficient:** Use the `ensure_packages` method to define the desired state of your environment. `pipmaster` handles the rest, performing a single, efficient installation for all missing or outdated packages.
*   **Programmatic Control:** Stop shelling out to `pip` with `os.system`. Manage your dependencies gracefully within your application logic, setup scripts, or automation tasks.
*   **Multi-Backend Ready:** Seamlessly use the standard `pip` or switch to the high-performance `uv` backend. `conda` support is planned for the future.
*   **Environment-Aware:** Target any Python virtual environment on your system simply by providing its path, making it perfect for managing complex projects or build servers.
*   **Asynchronous First:** A complete `async` API is available for modern, non-blocking applications.
*   **Safe and Informative:** A built-in `dry_run` mode lets you preview changes without modifying your system, and the `verbose` option provides detailed output for debugging.

## Feature Overview

| Feature                                      | `pip` Backend | `uv` Backend (Experimental) | `async` Support |
| -------------------------------------------- | :-----------: | :-------------------------: | :-------------: |
| **Ensure Package State (`ensure_packages`)** |      ✅       |             ❌              |       ✅        |
| Install / Upgrade Packages                   |      ✅       |             ✅              |       ✅        |
| Uninstall Packages                           |      ✅       |             ✅              |       ✅        |
| Check for Vulnerabilities (`pip-audit`)      |      ✅       |             N/A             |       ✅        |
| Check Installed Status (`is_installed`)      |      ✅       |             N/A             |      (Sync)     |
| Create Virtual Environments                  |      N/A      |             ✅              |       N/A       |
| Run Ephemeral Tools (`uvx`)                  |      N/A      |             ✅              |       N/A       |
| Dry Run Mode                                 |      ✅       |             ❌              |       ✅        |

## Installation

`pipmaster` requires Python 3.8 or higher.

```bash
pip install pipmaster
```

### Optional Features

`pipmaster` offers optional features that require extra dependencies. Install them as needed:

*   **Vulnerability Auditing:** Enables the `check_vulnerabilities` function using `pip-audit`.
    ```bash
    pip install pipmaster[audit]
    ```

*   **Development Environment:** For contributing to `pipmaster`, this includes all tools for testing, linting, and building documentation.
    ```bash
    git clone https://github.com/ParisNeo/pipmaster.git
    cd pipmaster
    pip install -e .[dev]
    ```
*   **All Extras:**
    ```bash
    pip install pipmaster[all]
    ```

## Getting Started: The `ensure_packages` Method

This is the most powerful and recommended way to use `pipmaster` with the `pip` backend. It efficiently checks if your requirements are met and only installs or updates what's necessary in a single batch operation. It's idempotent, meaning you can run it multiple times, and it will only act if the environment is not in the desired state.

It accepts a **string**, a **list**, or a **dictionary** for requirements.

```python
import pipmaster as pm

# 1. Ensure a SINGLE package is installed (using a string)
print("--- Ensuring 'rich' is installed ---")
pm.ensure_packages("rich", verbose=True)

# 2. Ensure a LIST of packages are installed
print("\n--- Ensuring a list of packages ---")
pm.ensure_packages(["pandas", "numpy>=1.20"], verbose=True)

# 3. Ensure a DICTIONARY of version-specific requirements are met
print("\n--- Ensuring a dictionary of requirements ---")
requirements = {
    "requests": ">=2.25.0",
    "tqdm": None  # We need it, but any installed version is fine
}
if pm.ensure_packages(requirements, verbose=True):
    print("\nAll requirements are successfully met!")
```

## Advanced Usage & Recipes

### Recipe 1: Synchronous vs. Asynchronous API

`pipmaster` provides a complete asynchronous API. Simply prefix function calls with `async_` and `await` them.

```python
import pipmaster as pm
import asyncio

# Synchronous call
pm.ensure_packages("httpx")

# Asynchronous equivalent
async def main():
    await pm.async_ensure_packages("httpx")

asyncio.run(main())
```

### Recipe 2: Using a Specific Backend (`pip` vs. `uv`)

While module-level functions default to the current environment's `pip`, you can get a dedicated manager to control a specific backend or environment.

#### `pip` Backend

```python
from pipmaster import get_pip_manager

# Target a specific Python environment
other_env_path = "/path/to/venv/bin/python" # Or "C:/path/to/venv/Scripts/python.exe"
# pip_manager = get_pip_manager(python_executable=other_env_path)
# pip_manager.install("requests")
```

#### `uv` Backend

This requires `uv` to be installed and available on your system's PATH.

```python
from pipmaster import get_uv_manager
import os
import shutil

temp_env_path = "./my_uv_test_env"

try:
    uv_manager = get_uv_manager()

    print(f"\n--- Creating new uv environment at {temp_env_path} ---")
    if uv_manager.create_env(path=temp_env_path):
        print("Environment created successfully.")
        uv_manager.install("numpy")
        print("Numpy installed in the new environment.")

    print("\n--- Running black --version with uv's tool runner ---")
    uv_manager.run_with_uvx(["black", "--version"], verbose=True)

except FileNotFoundError:
    print("Skipping uv examples: 'uv' executable not found in PATH.")
finally:
    if os.path.exists(temp_env_path):
        shutil.rmtree(temp_env_path)
```

### Recipe 3: Inspecting the Environment

Check the status of packages without changing anything. These functions are synchronous as they rely on the fast `importlib.metadata` library.

```python
import pipmaster as pm

if pm.is_installed("requests"):
    print("Requests is installed.")

if pm.is_installed("packaging", version_specifier=">=21.0"):
    print("A compatible version of 'packaging' is installed.")

numpy_version = pm.get_installed_version("numpy")
if numpy_version:
    print(f"Installed numpy version: {numpy_version}")

package_info = pm.get_package_info("pipmaster")
if package_info:
    print("\n--- pipmaster info ---\n" + package_info)
```

### Recipe 4: Safety Features (Dry Run & Auditing)

Preview changes and check for security vulnerabilities.

```python
import pipmaster as pm

print("\n--- Dry Run Examples ---")
pm.install("requests", dry_run=True, verbose=True)
pm.ensure_packages({"numpy": ">=1.20"}, dry_run=True, verbose=True)

print("\n--- Vulnerability Check ---")
try:
    vulnerabilities_found, report = pm.check_vulnerabilities()
    if vulnerabilities_found:
        print("WARNING: Vulnerabilities found in environment!")
    else:
        print("No known vulnerabilities found.")
except FileNotFoundError:
    print("Skipping check: pip-audit not found. Install with 'pip install pipmaster[audit]'")

```

## Contributing

Contributions are welcome! If you find a bug, have a feature request, or want to contribute code:

1.  **Search Issues:** Check the GitHub Issues page to see if a similar issue or request already exists.
2.  **Open an Issue:** If not, open a new issue describing the bug or feature.
3.  **Fork & Pull Request:** For code contributions, please fork the repository, create a new branch for your changes, and submit a pull request. Ensure your code includes tests and follows the project's style guidelines.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.