******************
Checking Packages
******************

`pipmaster` provides functions to check the installation status and version compatibility of packages using Python's standard `importlib.metadata`_ library.

.. _importlib.metadata: https://docs.python.org/3/library/importlib.metadata.html

Checking if Installed
=====================
Use :func:`~pipmaster.package_manager.is_installed` to determine if a package exists in the target environment.

.. code-block:: python

   import pipmaster as pm

   if pm.is_installed("requests"):
       print("requests is installed.")
   else:
       print("requests is NOT installed.")

   # Check a non-existent package
   if not pm.is_installed("no_such_package_exists_i_hope"):
       print("Confirmed: The non-existent package is not installed.")

Getting the Installed Version
=============================
Use :func:`~pipmaster.package_manager.get_installed_version` to retrieve the version string of an installed package. It returns `None` if the package is not found.

.. code-block:: python

   package_name = "packaging" # Dependency of pipmaster
   version = pm.get_installed_version(package_name)

   if version:
       print(f"Installed version of '{package_name}': {version}")
   else:
       print(f"'{package_name}' not found.")

Checking Version Compatibility
==============================
Use :func:`~pipmaster.package_manager.is_version_compatible` to check if the installed version of a package meets a specific version requirement defined by a PEP 440 specifier string.

.. code-block:: python

   # Assume 'packaging' version 23.2 is installed for these examples

   # Check if >= 21.0 (Should be True)
   if pm.is_version_compatible("packaging", ">=21.0"):
       print("packaging version is >= 21.0")

   # Check if == 23.2 (Should be True)
   if pm.is_version_compatible("packaging", "==23.2"):
       print("packaging version is exactly 23.2")

   # Check if < 23.0 (Should be False)
   if not pm.is_version_compatible("packaging", "<23.0"):
       print("packaging version is NOT < 23.0")

   # Check against a non-existent package (will be False)
   if not pm.is_version_compatible("nonexistent_pkg", ">=1.0"):
       print("Compatibility check returns False for non-existent packages.")

You can combine `is_installed` and `is_version_compatible` for more robust checks, although `is_installed` now accepts a `version_specifier` argument directly:

.. code-block:: python

   # Recommended way:
   if pm.is_installed("requests", version_specifier=">=2.25.0"):
        print("requests >= 2.25.0 is installed.")

   # Equivalent older way:
   if pm.is_installed("requests") and pm.is_version_compatible("requests", ">=2.25.0"):
        print("(Old way) requests >= 2.25.0 is installed.")


Getting Detailed Package Information
====================================
Use :func:`~pipmaster.package_manager.get_package_info` to retrieve the output of the `pip show <package_name>` command, which includes details like version, summary, dependencies, location, etc.

.. code-block:: python

   info = pm.get_package_info("pipmaster") # Get info about pipmaster itself
   if info:
       print("\n--- pipmaster info ---")
       print(info)
       print("----------------------\n")
   else:
       print("Could not get info for pipmaster (is it installed?).")