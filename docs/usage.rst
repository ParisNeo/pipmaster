Usage
=====

This section provides examples and guides on how to use pipmaster.

.. code-block:: python

   import pipmaster as pm

   # Install a package
   pm.install("requests")

   # Check if installed with version specifier
   if pm.is_installed("numpy", ">=1.20"):
       print("Compatible NumPy version found!")

   # Install multiple if missing
   pm.install_multiple_if_not_installed(["pandas", "matplotlib"])

   # Target a different environment using the CLI
   # Equivalent CLI command:
   # $ pipmaster equip scikit-learn -e /path/to/other/venv

   # Or create a new environment with a specific Python version using the CLI:
   # $ pipmaster forge -p 3.12 -d ./my_new_env -k scikit-learn

   # Retrieve a manager instance for programmatic control:
   other_env_pm = pm.get_pip_manager("/path/to/other/venv/bin/python")
   other_env_pm.install("scikit-learn")

   # Check vulnerabilities (requires pipmaster[audit])
   found, output = pm.check_vulnerabilities()
