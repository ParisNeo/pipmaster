# `pipmaster`: The Python Package Management Toolkit

<!-- Badges -->
[![PyPI version](https://badge.fury.io/py/pipmaster.svg)](https://badge.fury.io/py/pipmaster)
[![Python Versions](https://img.shields.io/pypi/pyversions/pipmaster.svg)](https://pypi.org/project/pipmaster/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/ParisNeo/pipmaster/blob/main/LICENSE)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/ParisNeo/pipmaster/docs.yml?branch=main&label=docs)](https://github.com/ParisNeo/pipmaster/actions/workflows/docs.yml)
[![GitHub stars](https://img.shields.io/github/stars/ParisNeo/pipmaster.svg?style=social&label=Stars)](https://github.com/ParisNeo/pipmaster)
[![Documentation Status](https://readthedocs.org/projects/pipmaster/badge/?version=latest)](https://parisneo.github.io/pipmaster/) 
[![Code Coverage](https://img.shields.io/codecov/c/github/ParisNeo/pipmaster)](https://codecov.io/gh/ParisNeo/pipmaster)
[![Code Quality](https://img.shields.io/codacy/grade/your-project-id)](https://www.codacy.com/app/your-username/pipmaster)

Stop telling your users to `pip install -r requirements.txt`. Start building professional, self‑sufficient Python applications that **just work**.

`pipmaster` is the ultimate toolkit for declarative and programmatic package management. It provides a robust, unified interface to backends like **`pip`** and **`uv`**, allowing you to automate installations, updates, and environment validation directly from your Python code. With both **synchronous and asynchronous APIs**, it's designed to guarantee that your applications work out‑of‑the‑box by programmatically ensuring all dependencies are correctly installed.

**View the full documentation at [parisneo.github.io/pipmaster/](https://parisneo.github.io/pipmaster/).**

## Why `pipmaster`? The Power to Build Better Software

`pipmaster` bridges the gap between development and deployment, solving the classic “it works on my machine” problem.

* **Automate Your Setup**: Your application can configure its own environment on first launch.
* **Self‑Healing Applications**: Detect missing or outdated packages at runtime and fix them automatically.
* **Eliminate “Dependency Hell”**: Manage dependencies for non‑technical users with zero manual steps.
* **Multi‑Environment Management**: Seamlessly work across multiple virtual environments, CI pipelines, or portable Python builds.
* **Dry‑Run & Verbose Modes**: Preview changes safely before they happen and get crystal‑clear debugging output.
* **Future‑Proof**: A pluggable architecture for additional backends (`uv`, `conda` planned).

## Key Use Cases

* **Desktop GUI Apps** – Ensure UI libraries are present on first run.
* **CLI Tools** – Auto‑install required plugins, making the tool instantly usable.
* **Data Science / ML Projects** – Keep notebooks, servers, and containers in sync with exact dependencies.
* **CI/CD Pipelines** – Prepare clean build environments programmatically.
* **Libraries & Frameworks** – Provide helper scripts that set up a correct environment for users.

## Quick Start

### Installation

```bash
pip install pipmaster
```

### Basic Usage

```python
import pipmaster as pm

# Ensure a single package is installed
pm.ensure_packages("rich")

# Ensure multiple packages with version requirements
pm.ensure_packages(["pandas", "numpy>=1.20"], verbose=True)

# Ensure packages from a requirements.txt file
pm.ensure_requirements("requirements.txt")
```

### Advanced Example

```python
import pipmaster as pm

# Conditional installation based on platform
required_packages = {
    "torch": {"index_url": "https://download.pytorch.org/whl/cu121", "specifier": ">=2.0.0"},
    "transformers": {"specifier": ">=4.30.0"},
}

# Check and install/update packages
pm.ensure_packages(required_packages, verbose=True)
```

## Feature Overview

| Feature                                      | `pip` Backend | `uv` Backend (Experimental) | Async Support |
| -------------------------------------------- | :-----------: | :------------------------: | :-----------: |
| **Ensure Package State (`ensure_packages`)**| ✅            | ❌                         | ✅            |
| **Ensure from `requirements.txt`**          | ✅            | ❌                         | ✅            |
| Install / Upgrade Packages                   | ✅            | ✅                         | ✅            |
| Uninstall Packages                           | ✅            | ✅                         | ✅            |
| Vulnerability Scanning (`pip-audit`)        | ✅            | N/A                        | ✅            |
| Check Installed Status (`is_installed`)      | ✅            | N/A                        | (Sync)        |
| Create Virtual Environments                  | N/A            | ✅                         | N/A           |
| Run Ephemeral Tools (`uvx`)                  | N/A            | ✅                         | N/A           |
| Dry Run Mode                                 | ✅            | ❌                         | ✅            |
| Portable Python Management                   | ✅            | ❌                         | ✅            |

## Core Concept: Declarative & Idempotent Management

The `ensure_*` methods are **idempotent** – you can run them repeatedly, and they only act when the environment diverges from your declaration.

### `ensure_packages`

```python
import pipmaster as pm

# 1️⃣ Simple: ensure a single package is present
pm.ensure_packages("rich")

# 2️⃣ List: ensure multiple packages with version specifiers
pm.ensure_packages(["pandas", "numpy>=1.20"], verbose=True)

# 3️⃣ Dictionary: clean mapping of package → version specifier
requirements = {
    "requests": ">=2.25.0",
    "tqdm": None,                     # any version accepted
    "torch": {"index_url": "https://download.pytorch.org/whl/cu121", "specifier": ">=2.0.0"},
}
pm.ensure_packages(requirements, verbose=True)
```

### `ensure_requirements`

```python
import pipmaster as pm

# Assuming a requirements.txt exists
if pm.ensure_requirements("requirements.txt", verbose=True):
    print("Environment now matches requirements.txt!")
```

## Advanced Usage

### Conditional Installation from Git (VCS)

```python
import pipmaster as pm

# Install from Git only if the installed version is <0.25.0
conditional_req = {
    "name": "diffusers",
    "vcs": "git+https://github.com/huggingface/diffusers.git",
    "condition": ">=0.25.0"
}
pm.ensure_packages([conditional_req], verbose=True)
```

### Asynchronous API

All core functions have async equivalents prefixed with `async_`.  

```python
import pipmaster as pm
import asyncio

async def async_demo():
    await pm.async_install("httpx")
    await pm.async_ensure_requirements("requirements.txt", verbose=True)

# asyncio.run(async_demo())
```

### Async Factory for Portable Python

When you need a specific portable Python version in an async context:

```python
import pipmaster as pm
import asyncio

async def main():
    async_pm = pm.get_async_pip_manager_for_version("3.12", "./portable_venv")
    await async_pm.install("rich", verbose=True)

    loop = asyncio.get_running_loop()
    installed = await loop.run_in_executor(None, async_pm.is_installed, "rich")
    print(f"'rich' installed? {installed}")

# asyncio.run(main())
```

### `uv` Backend (Experimental)

```python
from pipmaster import get_uv_manager
import os, shutil

env_path = "./my_uv_env"

if os.path.exists(env_path):
    shutil.rmtree(env_path)

uv = get_uv_manager()
if uv.create_env(path=env_path):
    uv.install_multiple(["numpy", "pandas"], verbose=True)
    uv.run_with_uvx(["black", "--version"], verbose=True)
```

## Vulnerability Scanning

```python
import pipmaster as pm

found, report = pm.check_vulnerabilities()
if found:
    print("Vulnerabilities detected!")
    print(report)
else:
    print("No known vulnerabilities.")
```

## Why Choose `pipmaster`?

### Compared to Manual `pip install`

| Feature | Manual `pip install` | `pipmaster` |
|---------|----------------------|-------------|
| Automation | Manual process | Fully automated |
| Error Handling | User must handle errors | Built-in error handling |
| Cross-platform | Platform-specific commands | Unified API |
| Version Management | Manual version checking | Automatic version validation |
| Environment Isolation | Manual venv management | Built-in venv support |

### Compared to Other Package Managers

| Feature | `pip` | `conda` | `uv` | `pipmaster` |
|---------|-------|---------|------|-------------|
| Programmatic API | Limited | Limited | Limited | Full API support |
| Async Support | No | No | Limited | Full async support |
| Portable Python | No | No | No | Built-in support |
| Cross-backend | No | No | No | Supports pip, uv, planned conda |

## Contributing

Contributions are welcome! Please see the [Contributing guide](docs/contributing.rst) for details on reporting issues, submitting pull requests, and running tests.

### How to Contribute

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Support

Need help? Join our community:

- **GitHub Discussions**: [Ask questions on GitHub](https://github.com/ParisNeo/pipmaster/discussions)

## License

This project is licensed under the Apache 2.0 License – see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the Python community for creating such a powerful ecosystem
- Special thanks to the developers of `pip`, `uv`, and `pip-audit` for their excellent tools
- Inspired by the need for better package management in production applications