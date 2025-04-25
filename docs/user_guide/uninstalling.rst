**********************
Uninstalling Packages
**********************

Use :func:`~pipmaster.package_manager.uninstall` and :func:`~pipmaster.package_manager.uninstall_multiple` to remove packages. These functions automatically add the ``-y`` flag to the `pip uninstall` command to bypass confirmation prompts.

Uninstalling a Single Package
=============================

.. code-block:: python

   import pipmaster as pm

   # First, let's install something to uninstall
   print("Installing 'termcolor' for uninstallation example...")
   pm.install("termcolor")

   if pm.is_installed("termcolor"):
       print("Uninstalling 'termcolor'...")
       if pm.uninstall("termcolor"):
           print("'termcolor' successfully uninstalled.")
       else:
           print("Failed to uninstall 'termcolor'.")
   else:
       print("'termcolor' was not installed.")

Uninstalling Multiple Packages
==============================

.. code-block:: python

   # Install a couple of packages first
   print("\nInstalling 'colorama' and 'rich' for multiple uninstall example...")
   pm.install_multiple(["colorama", "rich"])

   packages_to_remove = ["colorama", "rich"]
   print(f"\nUninstalling: {', '.join(packages_to_remove)}")
   if pm.uninstall_multiple(packages_to_remove):
       print("Packages uninstalled successfully.")
   else:
       print("Failed to uninstall one or more packages.")

Passing Extra Arguments
=======================
You can pass additional arguments to `pip uninstall` using the ``extra_args`` parameter.

.. code-block:: python

   # Example: Uninstall package installed from a requirements file
   # pm.uninstall("package-from-reqs", extra_args=["-r", "requirements.txt"])
   # Note: This specific use case might be less common programmatically.