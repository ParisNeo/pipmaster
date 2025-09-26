# `pipmaster`: The Python Package Management Toolkit

<!-- Badges -->
[![PyPI version](https://badge.fury.io/py/pipmaster.svg)](https://badge.fury.io/py/pipmaster)
[![Python Versions](https://img.shields.io/pypi/pyversions/pipmaster.svg)](https://pypi.org/project/pipmaster/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/ParisNeo/pipmaster/blob/main/LICENSE)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/ParisNeo/pipmaster/docs.yml?branch=main&label=docs)](https://github.com/ParisNeo/pipmaster/actions/workflows/docs.yml)
[![GitHub stars](https://img.shields.io/github/stars/ParisNeo/pipmaster.svg?style=social&label=Stars)](https://github.com/ParisNeo/pipmaster)
[![Documentation Status](https://readthedocs.org/projects/pipmaster/badge/?version=latest)](https://parisneo.github.io/pipmaster/) 

Stop telling your users to `pip install -r requirements.txt`. Start building professional, self-sufficient Python applications that **just work**.

`pipmaster` is the ultimate toolkit for declarative and programmatic package management. It provides a robust, unified interface to backends like **`pip`** and **`uv`**, allowing you to automate installations, updates, and environment validation directly from your Python code. With both **synchronous and asynchronous APIs**, it's designed to guarantee that your applications work out-of-the-box by programmatically ensuring all dependencies are correctly installed.

**View the full documentation at [parisneo.github.io/pipmaster/](https://parisneo.github.io/pipmaster/).**

## Why `pipmaster`? The Power to Build Better Software

`pipmaster` bridges the gap between development and deployment, solving the classic "it works on my machine" problem.

*   **Automate Your Setup:** Create a seamless first-time experience. Instead of manual setup steps, your application can configure its own environment on launch.
*   **Write Self-Healing Applications:** Programmatically verify dependencies every time your app runs. If a user accidentally uninstalls a critical package, your application can detect it and fix itself.
*   **Eliminate "Dependency Hell" for Users:** By managing dependencies automatically, you remove the biggest source of friction for non-technical users and simplify deployment for everyone.
*   **Simplify Complex Projects:** Effortlessly manage dependencies across multiple virtual environments, build servers, or CI/CD pipelines from a single, consistent interface.
*   **Code with Confidence:** Use the `dry_run` mode to safely preview any changes before they are made, and leverage the `verbose` flag for crystal-clear debugging.
*   **Future-Proof Your Scripts:** With a multi-backend architecture (`pip`, `uv`, and `conda` planned), your automation scripts remain stable even as the packaging ecosystem evolves.

## Key Use Cases

`pipmaster` is the swiss army knife for anyone who builds and ships Python software.

*   **Desktop GUI Applications (PyQt, Tkinter, etc.):** Ensure all UI libraries and dependencies are met on the very first launch, providing a smooth, installer-like experience.
*   **Command-Line Tools (Click, Typer, Argparse):** Create a fantastic user experience by having your CLI tool install its own dependencies, making it instantly usable.
*   **Data Science & ML Projects:** Guarantee that team members, servers, and Docker containers all share the exact same environment state by running an `ensure_requirements` check at the start of a script.
*   **CI/CD & Automation Scripts:** Programmatically prepare a build environment, install testing tools, and deploy your application with reliable, repeatable Python code instead of brittle shell scripts.
*   **Libraries and Frameworks:** Provide helper scripts for users to set up a correct environment, or use it internally to manage complex testing dependencies.

## Feature Overview

| Feature                                      | `pip` Backend | `uv` Backend (Experimental) | `async` Support |
| -------------------------------------------- | :-----------: | :-------------------------: | :-------------: |
| **Ensure Package State (`ensure_packages`)** |      ✅       |             ❌              |       ✅        |
| **Ensure from `requirements.txt`**           |      ✅       |             ❌              |       ✅        |
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

*   **Vulnerability Auditing (`pip-audit`):**
    ```bash
    pip install pipmaster[audit]
    ```
*   **Development Environment (for contributors):**
    ```bash
    git clone https://github.com/ParisNeo/pipmaster.git
    cd pipmaster
    pip install -e .[dev]
    ```
*   **All Extras:**
    ```bash
    pip install pipmaster[all]
    ```

## The Core Concept: Declarative & Idempotent Management

The `ensure_*` methods are the heart of `pipmaster`. They are **idempotent**, meaning you can run them a thousand times, and they will only perform an action if the environment is out of sync with your declarations.

They are also **efficient**. `pipmaster` checks all requirements first, then triggers a *single, batch installation command* only for the packages that are missing or outdated. This is far superior to running multiple `pip install` commands in a loop.

### `ensure_packages`: Define Dependencies Directly in Code

This is the most powerful feature for creating self-contained applications. Define dependencies as a simple string, a list, or a dictionary.

```python
import pipmaster as pm

# 1. Simple: Ensure a single package is present
pm.ensure_packages("rich")

# 2. List: Ensure multiple packages, with version specifiers
pm.ensure_packages(["pandas", "numpy>=1.20"], verbose=True)

# 3. Dictionary: A clean way to manage a set of requirements
requirements = {
    "requests": ">=2.25.0",
    "tqdm": None  # Any version is acceptable
}
pm.ensure_packages(requirements, verbose=True)
```

### `ensure_requirements`: Automate Your `requirements.txt` Workflow

Use your existing `requirements.txt` files and let `pipmaster` handle the rest. It's the perfect one-line replacement for manual installation commands.

```python
import pipmaster as pm

# Create a demo file
with open("requirements-demo.txt", "w") as f:
    f.write("rich\n")
    f.write("packaging>=21.0\n")

# Ensure the environment matches the file
if pm.ensure_requirements("requirements-demo.txt", verbose=True):
    print("\nEnvironment is in sync with requirements file!")
```

## Advanced Usage & Recipes

### Recipe 1: Conditional Installation from Git

Imagine you need cutting-edge features from a Git branch, but only if the user has an older version installed. `ensure_packages` handles this advanced logic with a special dictionary format.

```python
import pipmaster as pm

# This rule says: "We need diffusers version 0.25.0 or newer. 
# If the installed version doesn't meet this, install from the main branch on GitHub."
conditional_requirement = {
    "name": "diffusers",
    "vcs": "git+https://github.com/huggingface/diffusers.git",
    "condition": ">=0.25.0"
}

# First, let's install an old version to see it trigger
pm.install("diffusers==0.24.0", verbose=True)

print("\n--- Running ensure_packages with a conditional Git requirement ---")
pm.ensure_packages([conditional_requirement], verbose=True)
print(f"Post-check diffusers version: {pm.get_installed_version('diffusers')}")

print("\n--- Running it again (should do nothing) ---")
# Now that a newer version is installed, the condition is met, and pipmaster takes no action.
pm.ensure_packages([conditional_requirement], verbose=True)

```

### Recipe 2: Synchronous vs. Asynchronous API

Every core function has an `async` equivalent. Just prefix with `async_` and `await` the call.

```python
import pipmaster as pm
import asyncio

# Synchronous call
pm.install("httpx")

# Asynchronous equivalent
async def main():
    await pm.async_install("httpx")
    await pm.async_ensure_requirements("requirements.txt")

# asyncio.run(main()) # Uncomment to run
```

### Recipe 3: Using the `uv` Backend

Take advantage of `uv`'s incredible speed for creating environments and installing packages. This requires `uv` to be installed on your system's PATH.

```python
from pipmaster import get_uv_manager
import os
import shutil

temp_env_path = "./my_uv_test_env"

try:
    # Get a manager that is NOT tied to the current environment
    uv_manager = get_uv_manager()

    # Create a new, empty venv
    if uv_manager.create_env(path=temp_env_path):
        print("uv environment created successfully.")
        
        # The manager now targets the new environment for all subsequent calls
        uv_manager.install_multiple(["numpy", "pandas"], verbose=True)
        print("Packages installed in the new environment.")

    # Use uvx to run a tool in an ephemeral environment
    print("\n--- Running black --version with uv's tool runner ---")
    uv_manager.run_with_uvx(["black", "--version"], verbose=True)

except FileNotFoundError:
    print("Skipping uv examples: 'uv' executable not found in PATH.")
finally:
    if os.path.exists(temp_env_path):
        shutil.rmtree(temp_env_path)
```

### Recipe 4: Environment Inspection and Safety

Check packages without changing anything, and audit for security vulnerabilities.

```python
import pipmaster as pm

# --- Inspection (Fast, synchronous calls) ---
if pm.is_installed("requests", version_specifier=">=2.20"):
    print(f"Requests version {pm.get_installed_version('requests')} is compatible.")

# --- Safety: Dry Run ---
print("\n--- Previewing changes with Dry Run ---")
pm.ensure_packages({"numpy": "<1.20"}, dry_run=True, verbose=True)

# --- Safety: Vulnerability Audit ---
print("\n--- Checking for Vulnerabilities ---")
try:
    vulnerabilities_found, report = pm.check_vulnerabilities()
    if vulnerabilities_found:
        print("WARNING: Vulnerabilities found!")
    else:
        print("No known vulnerabilities found in the environment.")
except FileNotFoundError:
    print("Skipping check: pip-audit not found. Install with 'pip install pipmaster[audit]'")
```

## Contributing

Contributions are welcome! If you find a bug, have a feature request, or want to contribute code, please check the GitHub Issues page before opening a new issue or submitting a pull request.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.