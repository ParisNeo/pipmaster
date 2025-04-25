*************************
Vulnerability Scanning
*************************

`pipmaster` integrates with `pip-audit`_ to provide vulnerability scanning capabilities for your Python environments or requirements files.

.. _pip-audit: https://github.com/pypa/pip-audit

Prerequisites
=============
To use the vulnerability checking functions, you need:

1.  **`pipmaster[audit]` installed:** This installs `pip-audit` as a dependency.
    .. code-block:: bash

       pip install pipmaster[audit]

2.  **`pip-audit` in PATH:** The `pip-audit` command-line tool must be executable and discoverable in the system's PATH environment variable from where you run your Python script.

Checking Vulnerabilities
========================
Use the :func:`~pipmaster.package_manager.check_vulnerabilities` (sync) or :func:`~pipmaster.async_package_manager.async_check_vulnerabilities` (async) function.

These functions return a tuple: `(vulnerabilities_found: bool, report: str)`.

*   `vulnerabilities_found`: `True` if `pip-audit` found vulnerabilities or if an error occurred during the scan (fail-safe), `False` otherwise.
*   `report`: A string containing the output from `pip-audit` (either the vulnerability report, a "no vulnerabilities found" message, or error details).

**Checking the Current Environment**

By default, it scans the environment targeted by the `PackageManager` instance (or the default environment if using module-level functions).

.. code-block:: python

   import pipmaster as pm

   print("Scanning current environment for vulnerabilities...")
   try:
       found, report = pm.check_vulnerabilities()
       if found:
           print("\n--- Vulnerability Report ---")
           print(report)
           print("--------------------------\n")
       else:
           print("No vulnerabilities found.")
   except Exception as e: # More specific exceptions can be caught if needed
       print(f"Vulnerability check failed: {e}")
       print("Ensure 'pip-audit' is installed and in PATH ('pip install pipmaster[audit]')")

**Checking a Requirements File**

You can check the dependencies listed in a requirements file without necessarily scanning the whole installed environment.

.. code-block:: python

   # Assuming requirements.txt exists from previous examples
   print("\nScanning 'requirements.txt' for vulnerabilities...")
   try:
       found_req, report_req = pm.check_vulnerabilities(requirements_file="requirements.txt")
       if found_req:
           print("\n--- Requirements Vulnerability Report ---")
           print(report_req)
           print("---------------------------------------\n")
       else:
           print("No vulnerabilities found for packages in requirements.txt.")
   except Exception as e:
       print(f"Vulnerability check failed: {e}")


**Checking a Specific Package (Limited Support)**

`pip-audit` doesn't have a direct flag to check *only* a single installed package easily. `pipmaster` currently logs a warning and defaults to scanning the whole environment if only `package_name` is provided. Checking specific packages is best done via a temporary requirements file if needed.

**Passing Extra Arguments**

You can pass additional arguments directly to the `pip-audit` command line:

.. code-block:: python

   # Example: Check requirements and attempt automated fixes
   # found_fix, report_fix = pm.check_vulnerabilities(
   #     requirements_file="requirements.txt",
   #     extra_args=["--fix"] # Pass the --fix flag to pip-audit
   # )

Asynchronous Checking
=====================
Use the async version in async contexts:

.. code-block:: python

   import asyncio
   import pipmaster as pm

   async def check_vulns_async():
       print("\nAsync: Scanning environment...")
       try:
           found, report = await pm.async_check_vulnerabilities()
           if found:
               print("Async: Vulnerabilities found!")
               # print(report) # Optionally print
           else:
               print("Async: No vulnerabilities found.")
       except Exception as e:
           print(f"Async vulnerability check failed: {e}")

   # To run:
   # asyncio.run(check_vulns_async())