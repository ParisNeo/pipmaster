************************
Asynchronous Operations
************************

`pipmaster` offers an asynchronous API for non-blocking package management, suitable for use in `asyncio`-based applications.

When to Use Async
=================
Use the asynchronous functions (`async_install`, `async_check_vulnerabilities`, etc.) or the `AsyncPackageManager` class when you are working within an `async def` function and need to perform package operations without blocking the asyncio event loop. This is crucial in applications like web servers, GUI applications, or complex concurrent tasks where responsiveness is important.

Available Async Functions
=========================
Functions that involve running external commands (`pip`, `pip-audit`) have async counterparts:

*   :func:`~pipmaster.async_package_manager.async_install`
*   :func:`~pipmaster.async_package_manager.async_install_if_missing`
*   :func:`~pipmaster.async_package_manager.async_install_multiple`
*   :func:`~pipmaster.async_package_manager.async_ensure_packages`
*   :func:`~pipmaster.async_package_manager.async_ensure_requirements`
*   :func:`~pipmaster.async_package_manager.async_uninstall`
*   :func:`~pipmaster.async_package_manager.async_uninstall_multiple`
*   :func:`~pipmaster.async_package_manager.async_check_vulnerabilities`
*   :func:`~pipmaster.async_package_manager.async_get_package_info`

Functions that rely purely on synchronous libraries like `importlib.metadata` (:func:`~pipmaster.package_manager.is_installed`, :func:`~pipmaster.package_manager.get_installed_version`, :func:`~pipmaster.package_manager.is_version_compatible`) **do not** have direct async versions. See :ref:`async-sync-checks` below.

Basic Async Usage
=================

.. code-block:: python

   import pipmaster as pm
   import asyncio

   async def main():
       print("Starting async package management...")

       # Ensure requirements from a file asynchronously
       # First, create a dummy file
       with open("async_reqs.txt", "w") as f:
           f.write("httpx\n")
           f.write("rich\n")

       print("Ensuring requirements from file asynchronously...")
       await pm.async_ensure_requirements("async_reqs.txt", verbose=True)

       # Check vulnerabilities asynchronously
       print("\nRunning async vulnerability check...")
       try:
           found, report = await pm.async_check_vulnerabilities()
           if found:
               print("Async check found vulnerabilities.")
           else:
               print("Async check found no vulnerabilities.")
       except Exception as e:
           print(f"Async vulnerability check encountered an error: {e}")

   # Run the main async function
   if __name__ == "__main__":
       asyncio.run(main())

Using `AsyncPackageManager`
===========================
For targeting specific environments or more structured async code, use the `AsyncPackageManager` class. Its interface mirrors the synchronous `PackageManager`.

.. code-block:: python

   from pipmaster.async_package_manager import AsyncPackageManager
   import asyncio
   import sys

   async def manage_env_async(python_path=None):
       if python_path is None:
           python_path = sys.executable
           print(f"Using default environment: {python_path}")
       else:
            print(f"Targeting environment: {python_path}")

       try:
           async_pm = AsyncPackageManager(python_executable=python_path)

           # Example: Async install into the target environment
           await async_pm.install("rich") # Installs rich into the targeted env

           # Note: Checks still need executor for now
           loop = asyncio.get_running_loop()
           from pipmaster import PackageManager # Need sync version for check
           sync_pm_for_check = PackageManager(python_executable=python_path)
           is_rich_installed = await loop.run_in_executor(
               None, sync_pm_for_check.is_installed, "rich"
           )
           print(f"Is 'rich' installed in target env? {is_rich_installed}")

       except FileNotFoundError:
           print(f"Error: Python executable not found at {python_path}")
       except Exception as e:
           print(f"An error occurred: {e}")

   # Example usage:
   # venv_python_path = "/path/to/your/other/venv/bin/python" # EDIT THIS
   # asyncio.run(manage_env_async(venv_python_path))
   # asyncio.run(manage_env_async()) # Target current env


.. _async-sync-checks:

Handling Synchronous Checks in Async Code
=========================================
As mentioned, checks like `is_installed`, `get_installed_version`, and `is_version_compatible` are currently synchronous because they use `importlib.metadata`. To use them in an async application without blocking the event loop, run them in an executor:

.. code-block:: python

   import pipmaster as pm
   import asyncio

   async def check_package_non_blocking(package_name):
       loop = asyncio.get_running_loop()

       print(f"Checking '{package_name}' without blocking...")
       # Run the synchronous pm.is_installed in the default thread pool executor
       installed = await loop.run_in_executor(None, pm.is_installed, package_name)

       if installed:
           # Run get_installed_version in the executor as well
           version = await loop.run_in_executor(None, pm.get_installed_version, package_name)
           print(f"'{package_name}' is installed (Version: {version})")
       else:
           print(f"'{package_name}' is not installed.")

   # To run:
   # asyncio.run(check_package_non_blocking("numpy"))