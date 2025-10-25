*********************************
Experimental `uv` Backend
*********************************

`pipmaster` provides experimental support for `uv`_, an extremely fast Python package installer and resolver. This allows you to leverage `uv`'s speed for creating environments and managing packages programmatically.

.. _uv: https://github.com/astral-sh/uv

Prerequisites
=============
To use the `uv` backend, you must have the `uv` executable installed and available in your system's PATH.

.. code-block:: bash

   # Example installation for macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # See the official uv documentation for other installation methods.

Getting the `uv` Manager
========================
Use the :func:`~pipmaster.package_manager.get_uv_manager` factory function to get an instance of the :py:class:`~pipmaster.package_manager.UvPackageManager`.

.. code-block:: python

   from pipmaster import get_uv_manager

   try:
       uv_manager = get_uv_manager()
       print("UvPackageManager created successfully.")
   except FileNotFoundError as e:
       print(e)
       # Handle the case where 'uv' is not installed

Creating a Virtual Environment
==============================
The primary use case for the `uv` manager is to create and manage new virtual environments.

.. code-block:: python

   import os
   import shutil
   from pipmaster import get_uv_manager

   env_path = "./my_uv_env"

   if os.path.exists(env_path):
       shutil.rmtree(env_path)

   try:
       uv_manager = get_uv_manager()
       
       print(f"Creating uv environment at: {env_path}")
       if uv_manager.create_env(path=env_path):
           print("Environment created successfully.")
           # The manager now targets this new environment for subsequent calls
           print(f"Manager now targets Python: {uv_manager.python_executable}")
       else:
           print("Failed to create environment.")

   except FileNotFoundError:
       print("Skipping example: 'uv' executable not found in PATH.")
   finally:
       if os.path.exists(env_path):
           shutil.rmtree(env_path)

Installing and Uninstalling Packages
====================================
Once an environment is created or assigned, you can install and uninstall packages into it.

.. code-block:: python
   :emphasize-lines: 16, 22

   # ... (previous code for creating the environment) ...
   try:
       uv_manager = get_uv_manager()
       if uv_manager.create_env(path=env_path):
           print("Environment created. Now installing packages...")
           
           # Install multiple packages
           uv_manager.install_multiple(["numpy", "pandas"], verbose=True)

           # You can now use this environment to run code
           # (e.g., using subprocess with uv_manager.python_executable)

           print("\nUninstalling pandas...")
           uv_manager.uninstall("pandas", verbose=True)

   # ... (error handling and cleanup) ...

Running Ephemeral Tools (`uvx`)
===============================
`pipmaster` exposes `uv`'s ability to run a tool in a temporary, ephemeral environment via the `run_with_uvx` method. This is the equivalent of the `uvx` or `uv tool run` command.

This is perfect for running formatters, linters, or other tools without polluting your global or project environments.

.. code-block:: python

   from pipmaster import get_uv_manager

   try:
       # No environment path is needed for this
       uv_manager = get_uv_manager()
       
       print("Running 'black --version' with uvx...")
       uv_manager.run_with_uvx(["black", "--version"], verbose=True)
       
       print("\nRunning 'ruff check .' with uvx...")
       # This would check the current directory with ruff
       # uv_manager.run_with_uvx(["ruff", "check", "."], verbose=True)

   except FileNotFoundError:
       print("Skipping example: 'uv' executable not found in PATH.")