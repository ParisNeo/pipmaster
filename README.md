# pipmaster

<!-- Badges - Update URLs/paths as needed -->
[![PyPI version](https://badge.fury.io/py/pipmaster.svg)](https://badge.fury.io/py/pipmaster)
[![Python Versions](https://img.shields.io/pypi/pyversions/pipmaster.svg)](https://pypi.org/project/pipmaster/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/ParisNeo/pipmaster/blob/main/LICENSE)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/ParisNeo/pipmaster/docs.yml?branch=main&label=docs)](https://github.com/ParisNeo/pipmaster/actions/workflows/docs.yml)
[![GitHub stars](https://img.shields.io/github/stars/ParisNeo/pipmaster.svg?style=social&label=Stars)](https://github.com/ParisNeo/pipmaster)


`pipmaster` is a versatile Python library designed to simplify and automate Python package management tasks directly from your code. It provides a robust, programmatic interface to `pip`, allowing you to install, update, check, and uninstall packages, manage requirements, target different Python environments, perform vulnerability checks, and more, with both synchronous and asynchronous interfaces.

**View the full documentation at [parisneo.github.io/pipmaster/](https://parisneo.github.io/pipmaster/).**

## Why pipmaster?

*   **Programmatic Control:** Manage packages within your scripts, setup routines, or automation tasks.
*   **Environment Targeting:** Install and check packages in different virtual environments, not just the current one.
*   **Rich Feature Set:** Handles specific versions, custom indexes, editable installs, requirements files, conditional installs, dry runs, and vulnerability scanning.
*   **Modern & Robust:** Uses modern standard libraries like `importlib.metadata` and `packaging` for reliable checks.
*   **Async Support:** Provides asynchronous functions for integration into async applications.
*   **Extensible:** Designed with placeholders for future support of backends like UV or Conda.

## Key Features

*   Install/upgrade single or multiple packages (`install`, `install_multiple`).
*   Install specific package versions (`install_version`).
*   Install packages only if they are missing (`install_multiple_if_not_installed`).
*   Conditionally install/update based on version specifiers (`install_if_missing`).
*   Install packages in editable mode (`install_edit`).
*   Install packages from requirements files (`install_requirements`).
*   Check if packages are installed, optionally matching version specifiers (`is_installed`, `is_version_compatible`).
*   Get installed package versions (`get_installed_version`) and details (`get_package_info`).
*   Install or update packages (`install_or_update`, `install_or_update_multiple`).
*   Uninstall single or multiple packages (`uninstall`, `uninstall_multiple`).
*   **Target specific Python environments** by providing the path to the Python executable.
*   **Dry Run mode** (`dry_run=True`) to simulate commands without making changes.
*   **Asynchronous API** (e.g., `async_install`) for non-blocking operations.
*   **Vulnerability Checking** using `pip-audit` integration (`check_vulnerabilities`).
*   Convenient module-level functions for common tasks.
*   Instantiable `PackageManager` and `AsyncPackageManager` classes for more control.

## Installation

`pipmaster` requires Python 3.8 or higher.

```bash
pip install pipmaster
```

### Optional Features

`pipmaster` offers optional features that require extra dependencies. Install them as needed:

*   **Vulnerability Auditing:** Enables the `check_vulnerabilities` function.
    ```bash
    pip install pipmaster[audit]
    ```

*   **Development Tools:** Includes tools for testing, linting, and building documentation (pytest, ruff, sphinx, etc.).
    ```bash
    pip install pipmaster[dev]
    # Or for editable install during development:
    # pip install -e .[dev]
    ```

*   **All Extras:** Install all optional dependencies at once.
    ```bash
    pip install pipmaster[all]
    # Or for editable install:
    # pip install -e .[all]
    ```

## Basic Usage

Import the library and use the module-level functions for quick tasks targeting the current Python environment:

```python
import pipmaster as pm
import asyncio # For async examples

# Install the latest version of 'requests' (or upgrade if present)
print("Installing requests...")
if pm.install("requests"):
    print("Requests installed/updated.")
else:
    print("Failed to install requests.")

# Check if 'numpy' version 1.20 or higher is installed
print("\nChecking numpy version...")
if pm.is_installed("numpy", version_specifier=">=1.20.0"):
    version = pm.get_installed_version("numpy")
    print(f"Compatible numpy version ({version}) found.")
else:
    print("Compatible numpy not found. Installing...")
    pm.install("numpy>=1.20.0") # Install with the required specifier
```

## Detailed Usage & Examples

### 1. Installation Functions

```python
# Install latest (or upgrade)
pm.install("pandas")

# Install without implicit upgrade
pm.install("matplotlib", upgrade=False)

# Force reinstall
pm.install("scipy", force_reinstall=True)

# Install from a custom index URL
pm.install("torch", index_url="https://download.pytorch.org/whl/cu121")

# Install a specific version
pm.install_version("requests", "2.28.1")

# Install multiple packages (will upgrade by default)
pm.install_multiple(["seaborn", "plotly"])

# Install multiple from a specific index, forcing reinstall
pm.install_multiple(
    ["torchvision", "torchaudio"],
    index_url="https://download.pytorch.org/whl/cu121",
    force_reinstall=True
)

# Install only if missing (checks presence, not version)
pm.install_multiple_if_not_installed(["python-dotenv", "tqdm"])

# Install from requirements file
# Create a dummy requirements.txt:
# with open("reqs.txt", "w") as f: f.write("colorama\ntermcolor")
pm.install_requirements("reqs.txt")

# Install local package in editable mode
# Assume 'my_local_package' exists at './my_local_package' with a setup.py or pyproject.toml
# pm.install_edit("./my_local_package") # Uncomment if you have a local package

# Conditional installation with version checking
# Install numpy>=1.21 only if it's missing OR if installed version is < 1.21
pm.install_if_missing("numpy", version_specifier=">=1.21.0")

# Install exactly version 3.10.0 of protobuf if missing or different version installed
pm.install_if_missing("protobuf", version_specifier="==3.10.0")

# Install if missing, or ensure it's updated to latest if present
pm.install_if_missing("pip", always_update=True)
```

### 2. Checking Package Status

```python
# Check if installed
if pm.is_installed("requests"):
    print("Requests is installed.")

# Check if specific version specifier is met
if pm.is_installed("packaging", version_specifier=">=21.0"):
    print("Compatible 'packaging' version installed.")

# Get installed version (returns str or None)
numpy_ver = pm.get_installed_version("numpy")
if numpy_ver:
    print(f"Installed numpy version: {numpy_ver}")
else:
    print("Numpy is not installed.")

# Explicitly check version compatibility
if pm.is_version_compatible("pip", ">=23.0"):
    print("Pip version is >= 23.0")
else:
    print("Pip version is older than 23.0")

# Get detailed package info (output of 'pip show')
info = pm.get_package_info("pipmaster") # Get info about pipmaster itself
if info:
    print("\n--- pipmaster info ---")
    print(info)
    print("----------------------\n")
```

### 3. Uninstalling Packages

```python
# Uninstall a single package (assuming 'termcolor' was installed via reqs.txt)
# print("Uninstalling termcolor...")
# pm.uninstall("termcolor")

# Uninstall multiple packages
# print("Uninstalling colorama and python-dotenv...")
# pm.uninstall_multiple(["colorama", "python-dotenv"])
```

### 4. Advanced Features

**Targeting Other Environments**

```python
# Specify the path to the python executable of another virtual environment
other_env_python = "/path/to/your/other/venv/bin/python" # Linux/macOS example
# other_env_python = "C:/path/to/your/other/venv/Scripts/python.exe" # Windows example

# Get a dedicated manager instance for that environment
# Replace with a valid path if you want to test this
# try:
#     other_pm = pm.get_pip_manager(python_executable=other_env_python)
#     print(f"\nChecking 'requests' in environment: {other_env_python}")
#     if other_pm.is_installed("requests"):
#         print("'requests' is installed in the other environment.")
#         other_pm.uninstall("requests") # Example: Uninstall from other env
#     else:
#         print("'requests' is NOT installed in the other environment.")
#         other_pm.install("requests") # Example: Install into other env
# except FileNotFoundError:
#      print(f"Skipping environment targeting test: Path not found '{other_env_python}'")

```

**Dry Run Mode**

Simulate commands without making changes.

```python
print("\n--- Dry Run Examples ---")
# Simulate installing requests
pm.install("requests", dry_run=True)

# Simulate uninstalling multiple packages
pm.uninstall_multiple(["numpy", "pandas"], dry_run=True)

# Simulate installing requirements
pm.install_requirements("reqs.txt", dry_run=True)
print("----------------------\n")
```

**Vulnerability Scanning**

Requires `pipmaster[audit]` to be installed.

```python
print("\n--- Vulnerability Check ---")
# Check the current environment (or the one targeted by a PackageManager instance)
# Note: Needs pip-audit installed in the *environment running this script*
try:
    found_vulns, report = pm.check_vulnerabilities()
    if found_vulns:
        print("WARNING: Vulnerabilities found!")
        # print(report) # Optionally print the full report
    else:
        print("No vulnerabilities found in the environment.")
except ImportError: # Or handle FileNotFoundError if pip-audit isn't installed
    print("Skipping vulnerability check: pip-audit not found. Install with 'pip install pipmaster[audit]'")
print("-------------------------\n")
```

### 5. Asynchronous Usage

Use the `async_` prefixed functions within an `async` context.

```python
async def run_async_tasks():
    print("\n--- Async Examples ---")

    # Async install
    print("Async: Installing 'aiohttp'...")
    success = await pm.async_install("aiohttp")
    if success:
        print("Async: aiohttp installed.")
    else:
        print("Async: Failed to install aiohttp.")

    # Async check vulnerabilities
    print("Async: Checking vulnerabilities...")
    try:
         # Note: check_vulnerabilities itself isn't fully async internally yet,
         # but the wrapper uses asyncio.create_subprocess_shell
        found, report = await pm.async_check_vulnerabilities()
        if found:
             print("Async: WARNING: Vulnerabilities found!")
        else:
             print("Async: No vulnerabilities found.")
    except Exception as e:
         print(f"Async: Vulnerability check failed: {e}")

    # Add more async examples as needed (e.g., async_uninstall)
    print("--------------------\n")

# To run the async functions:
# asyncio.run(run_async_tasks()) # Uncomment to run
```

### 6. Using the `PackageManager` Class Directly

For more control, especially when repeatedly targeting a specific environment or using custom pip commands:

```python
from pipmaster import PackageManager

# Manager for the current environment (same as module functions)
default_pm = PackageManager()
default_pm.install("rich")

# Manager targeting a specific environment
# other_env_python = "/path/to/other/venv/bin/python"
# try:
#     other_pm = PackageManager(python_executable=other_env_python)
#     other_pm.install("requests") # Install requests in the other environment
#     print(f"Version in other env: {other_pm.get_installed_version('requests')}")
# except FileNotFoundError:
#     print(f"Path not found, cannot create manager for: {other_env_python}")


# Advanced: Custom base command (Use with caution!)
# custom_pm = PackageManager(pip_command_base=["/path/to/custom/pip", "--no-cache-dir"])
# custom_pm.install("somepackage")
```
### 7. Ensuring Multiple Package Requirements (`ensure_packages`)

For managing a set of required packages with specific versions efficiently, use `ensure_packages`. It checks all requirements and performs a single installation/update command for only those packages that need it.

```python
# Define your project's requirements
my_requirements = {
    "requests": ">=2.25.0,<3.0.0",
    "pandas": ">=1.3.0",
    "numpy": None, # Install latest if missing, otherwise accept any version
    "torch": "==1.13.1" # Example: exact version
}

print("\n--- Ensuring Project Requirements ---")
# This will check all packages and install/update if needed
success = pm.ensure_packages(my_requirements)

if success:
    print("All project requirements are met.")
else:
    print("Failed to ensure all project requirements.")

# You can also use it with index_url, extra_args, dry_run
# pm.ensure_packages(
#     my_requirements,
#     index_url="https://custom-index.com",
#     extra_args=["--no-cache-dir"],
#     dry_run=True
# )
print("-----------------------------------\n")
```

**How it Works:**

1.  It takes the `requirements` dictionary.
2.  It iterates through each `package`, `specifier` pair.
3.  It uses `self.is_installed(package, version_specifier=specifier)` to check if the current state meets the requirement.
4.  If a requirement is *not* met, it formats the package string (e.g., `"package>=1.2.3"` or just `"package"`) and adds it to a list `packages_to_process`.
5.  If `packages_to_process` is not empty after checking all requirements, it calls `self.install_multiple(packages=packages_to_process, upgrade=True, ...)` once to handle all necessary installations/updates efficiently.
6.  It returns `True` if everything was okay initially or the `install_multiple` call succeeded, `False` otherwise.


## Command-Line Interface (CLI)

A dedicated command-line interface for `pipmaster` is planned for future development, allowing easy environment creation and package management from the terminal using different backends (pip, uv, conda).

## Contributing

Contributions are welcome! If you find a bug, have a feature request, or want to contribute code:

1.  **Search Issues:** Check the GitHub Issues page to see if a similar issue or request already exists.
2.  **Open an Issue:** If not, open a new issue describing the bug or feature.
3.  **Fork & Pull Request:** For code contributions, please fork the repository, create a new branch for your changes, and submit a pull request. Ensure your code includes tests and follows the project's style guidelines (use `ruff` for linting/formatting).

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.