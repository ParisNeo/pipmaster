**********
Changelog
**********

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[0.7.1] - 2025-04-29
====================

Changed
-------
*   Refactored core logic into `PackageManager` class. Module-level functions now wrap methods of a default instance.
*   `is_installed` now accepts an optional `version_specifier` argument.
*   `install_if_missing` now uses `version_specifier` instead of separate `version` and `enforce_version` arguments (old arguments are deprecated but handled with warnings).
*   **`ensure_packages` now accepts both a dictionary and a list of requirement strings.** (New)
*   **Added `verbose` parameter to installation/uninstallation functions to control direct output.** (New)
*   Improved internal command execution and error handling.
*   Updated dependencies (`packaging`, `ascii_colors`).
*   Switched build system to use `pyproject.toml` with `setuptools`.
*   Minimum Python version raised to 3.8.


[0.7.0] - 2025-04-25
====================
Added
-----
*   `ensure_packages` function for efficiently checking and installing/updating a dictionary of requirements.
*   `dry_run` parameter added to most installation/uninstallation functions.
*   Asynchronous API (`async_package_manager` module) with `AsyncPackageManager`, `async_install`, `async_install_if_missing`, `async_check_vulnerabilities`.
*   `check_vulnerabilities` function using `pip-audit` (requires `pipmaster[audit]`).
*   `get_pip_manager` factory function to get `PackageManager` instances for specific environments.
*   `get_package_info` function to run `pip show`.
*   `install_or_update` and `install_or_update_multiple` convenience functions.
*   Placeholders for future `uv` and `conda` backend support.
*   More robust logging using `ascii_colors`.
*   Comprehensive documentation generated with Sphinx.
*   GitHub Actions workflow for building and deploying documentation.
*   Development dependencies (`[dev]` extra) including `pytest`, `pytest-asyncio`, `ruff`, `mypy`, `sphinx`.

Changed
-------
*   Refactored core logic into `PackageManager` class. Module-level functions now wrap methods of a default instance.
*   `is_installed` now accepts an optional `version_specifier` argument.
*   `install_if_missing` now uses `version_specifier` instead of separate `version` and `enforce_version` arguments (old arguments are deprecated but handled with warnings).
*   Improved internal command execution and error handling.
*   Updated dependencies (`packaging`, `ascii_colors`).
*   Switched build system to use `pyproject.toml` with `setuptools`.
*   Minimum Python version raised to 3.8.

Deprecated
----------
*   `is_version_higher` (use `is_version_compatible` with `>=`).
*   `is_version_exact` (use `is_version_compatible` with `==`).
*   `install_if_missing` parameters `version` and `enforce_version` (use `version_specifier`).

Removed
-------
*   *(No major removals in this version)*

[0.1.0] - 2024-04-01
====================
Added
-----
* Initial release with basic `install`, `is_installed`, `get_installed_version`, `uninstall` functions.