******************************************
Working with Different Environments
******************************************

A key feature of `pipmaster` is its ability to manage packages not just in the current Python environment, but also in other specified environments (like virtual environments).

Default Behavior
================
If you don't specify an environment, `pipmaster` functions operate on the environment associated with the Python interpreter running the script (i.e., `sys.executable`).

.. code-block:: python

    import pipmaster as pm
    import sys

    # These commands affect the current environment
    pm.install("requests")
    print(f"Running in: {sys.executable}")
    print(f"Requests version: {pm.get_installed_version('requests')}")

Targeting a Specific Environment
================================
To target a different environment, you need the path to that environment's Python executable.

1.  **Using `get_pip_manager`:** This factory function returns a `PackageManager` instance configured for the specified environment.

    .. code-block:: python

       import pipmaster as pm

       # --- IMPORTANT ---
       # Replace this path with the actual path to the Python executable
       # within a VIRTUAL ENVIRONMENT on your system to test this properly.
       # Example paths:
       # Linux/macOS: venv_python_path = "/home/user/my_projects/my_venv/bin/python"
       # Windows:     venv_python_path = "C:/Users/user/my_projects/my_venv/Scripts/python.exe"
       venv_python_path = "/path/to/your/other/venv/bin/python" # EDIT THIS

       try:
           print(f"\nTargeting environment: {venv_python_path}")
           other_pm = pm.get_pip_manager(python_executable=venv_python_path)

           # Check if 'flask' is installed in the *other* environment
           if other_pm.is_installed("flask"):
               print("'flask' is installed in the target environment.")
               version = other_pm.get_installed_version("flask")
               print(f"  -> Version: {version}")
               print("  -> Uninstalling 'flask' from target environment...")
               other_pm.uninstall("flask")
           else:
               print("'flask' is NOT installed in the target environment.")
               print("  -> Installing 'flask' into target environment...")
               other_pm.install("flask")

       except FileNotFoundError:
           print(f"\nError: The specified Python path does not exist: '{venv_python_path}'")
           print("Skipping environment targeting example.")
       except Exception as e:
           print(f"\nAn error occurred: {e}")
           print("Skipping environment targeting example.")


2.  **Creating `PackageManager` Instances:** You can also directly instantiate the class.

    .. code-block:: python

       from pipmaster import PackageManager

       # venv_python_path = "/path/to/your/other/venv/bin/python" # EDIT THIS
       # try:
       #    venv_pm = PackageManager(python_executable=venv_python_path)
       #    # ... perform operations using venv_pm ...
       # except FileNotFoundError:
       #    # Handle error


Automatic Environment Creation
==============================
When creating a `PackageManager` instance, you can provide a path to a virtual environment directory using the `venv_path` argument. If the environment does not exist at that path, `pipmaster` will automatically create it for you.

.. code-block:: python

   from pipmaster import PackageManager
   import os
   import shutil

   # Path for our new environment
   new_venv_path = "./my_new_test_venv"

   # Clean up from previous runs if it exists
   if os.path.exists(new_venv_path):
       shutil.rmtree(new_venv_path)

   print(f"Attempting to create and use a venv at: {new_venv_path}")
   
   # This will create the venv because it doesn't exist
   venv_pm = PackageManager(venv_path=new_venv_path)

   print(f"PackageManager is now targeting: {venv_pm.target_python_executable}")

   # Install a package into the newly created environment
   venv_pm.install("rich", verbose=True)

   # Clean up the created environment
   shutil.rmtree(new_venv_path)


How it Works
============
When a `python_executable` or `venv_path` is provided, `pipmaster` constructs the `pip` command like this:

.. code-block:: bash

   /path/to/your/other/venv/bin/python -m pip <command> [options]

This ensures that `pip` operations (install, uninstall, show, etc.) are executed within the context of the specified environment, affecting its packages rather than the environment running the `pipmaster` script.

Considerations
==============
*   **Path Existence:** Ensure the path provided to `python_executable` is correct and points to a valid Python interpreter. If using `venv_path`, the parent directory must be writable.
*   **Permissions:** The script running `pipmaster` needs appropriate permissions to execute the target Python interpreter and modify its site-packages directory.
*   **`pip` Availability:** The target environment must have `pip` installed and accessible via `python -m pip`. This is handled automatically when creating a venv with `pipmaster`.