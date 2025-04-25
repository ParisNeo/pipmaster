*************
Core Concepts
*************

Understanding these core concepts will help you use `pipmaster` effectively.

Target Environment
==================

By default, `pipmaster` operates on the same Python environment where the script using it is currently running (identified by `sys.executable`).

You can target a **different** Python environment (like a specific virtual environment) by providing the path to its Python executable when creating a `PackageManager` instance or using the `get_pip_manager` factory function.

.. code-block:: python

   import pipmaster as pm
   import sys

   # Default manager targets the current environment
   default_pm = pm.PackageManager()
   print(f"Default targets: {default_pm.target_python_executable}")
   # is equivalent to:
   current_pm = pm.PackageManager(python_executable=sys.executable)
   print(f"Current targets: {current_pm.target_python_executable}")

   # Target a specific venv (replace with a valid path on your system)
   # venv_python_path = "/path/to/myenv/bin/python" # Linux/macOS
   venv_python_path = "C:/path/to/myenv/Scripts/python.exe" # Windows

   try:
       # Get a manager instance specifically for this environment
       venv_pm = pm.get_pip_manager(python_executable=venv_python_path)
       print(f"Targeting venv: {venv_pm.target_python_executable}")

       # Operations using venv_pm will affect the other environment
       venv_pm.install("requests") # Installs requests into the venv

   except FileNotFoundError:
       print(f"Warning: Path not found for target environment: {venv_python_path}")

Synchronous vs. Asynchronous API
================================

`pipmaster` provides both synchronous and asynchronous functions:

*   **Synchronous:** Functions like `pm.install()`, `pm.is_installed()`. These block execution until the `pip` command completes. They are suitable for standard scripts, setup routines, and simple automation.
*   **Asynchronous:** Functions prefixed with `async_`, like `pm.async_install()`. These use Python's `asyncio` library and return *awaitables*. They are designed for use in asynchronous applications (e.g., using `async def`, `await`, `asyncio.run()`) where blocking operations should be avoided.

Currently, only operations that involve running external commands (like `pip install`, `pip uninstall`, `pip-audit`) have async counterparts. Checks that rely on `importlib.metadata` (like `is_installed`, `get_installed_version`) remain synchronous as the underlying library is sync. If you need to perform these checks in an async application without blocking, you can run the synchronous `pipmaster` functions within an asyncio executor using `loop.run_in_executor()`.

.. code-block:: python
   :caption: Example Async Usage

   import pipmaster as pm
   import asyncio

   async def manage_packages_async():
       print("Async: Installing httpx...")
       await pm.async_install("httpx")

       print("Async: Checking requests (sync check in executor)...")
       loop = asyncio.get_running_loop()
       # Run the synchronous is_installed function in the default executor
       req_installed = await loop.run_in_executor(None, pm.is_installed, "requests")
       print(f"Async: Is requests installed? {req_installed}")

   # To run this:
   # asyncio.run(manage_packages_async())

Package Management Backends
===========================

Currently, `pipmaster` primarily uses **pip** as its backend for package operations.

The design includes placeholders and factory functions (`get_uv_manager`, `get_conda_manager`) for potential future support of other backends like `uv`_ or `conda`_. These are **not yet implemented**.

.. _uv: https://github.com/astral-sh/uv
.. _conda: https://docs.conda.io/en/latest/

Error Handling
==============

Most installation and uninstallation functions return `True` on success and `False` on failure. Errors during the execution of `pip` commands (e.g., network issues, package not found, build errors) are logged using Python's `logging` module (configured to use `ascii_colors` for terminal output). Detailed error messages from `pip` are often captured and included in the logs or returned in the output string of functions like `_run_command`.

Functions that retrieve information (like `get_installed_version`) typically return `None` if the package is not found or an error occurs.

Always check the return values of functions and consult the logs for troubleshooting.