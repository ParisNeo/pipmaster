***************
Getting Started
***************

This tutorial provides a quick overview of common `pipmaster` tasks.

1. Import the Library
=====================

Start by importing `pipmaster`:

.. code-block:: python

   import pipmaster as pm
   import asyncio # Needed for async examples later

2. Install a Package
====================

Use :func:`~pipmaster.package_manager.install` to ensure a package is installed (it will upgrade if already present by default):

.. code-block:: python

   package_name = "requests"
   print(f"Ensuring '{package_name}' is installed...")
   if pm.install(package_name):
       print(f"'{package_name}' installed or already up-to-date.")
   else:
       print(f"Failed to install '{package_name}'.")

3. Check if a Package is Installed
==================================

Use :func:`~pipmaster.package_manager.is_installed` and :func:`~pipmaster.package_manager.get_installed_version`:

.. code-block:: python

   package_to_check = "packaging" # A dependency of pipmaster
   if pm.is_installed(package_to_check):
       version = pm.get_installed_version(package_to_check)
       print(f"'{package_to_check}' is installed, version: {version}")
   else:
       print(f"'{package_to_check}' is not installed.")

4. Conditional Installation Based on Version
============================================

Use :func:`~pipmaster.package_manager.install_if_missing` with the ``version_specifier`` argument:

.. code-block:: python

   # Ensure 'requests' version 2.25.0 or higher, but less than 3.0.0
   specifier = ">=2.25.0,<3.0.0"
   print(f"Ensuring 'requests' meets specifier: '{specifier}'")
   if pm.install_if_missing("requests", version_specifier=specifier):
       print("'requests' requirement met or installation/update succeeded.")
   else:
       print("Failed to meet 'requests' requirement.")

5. Install Multiple Packages (Only if Missing)
==============================================

Use :func:`~pipmaster.package_manager.install_multiple_if_not_installed`:

.. code-block:: python

   extras = ["rich", "tqdm"] # Example utility packages
   print(f"Installing missing packages from: {extras}")
   if pm.install_multiple_if_not_installed(extras):
       print("Checked/installed extra utility packages.")
   else:
       print("Failed to install some utility packages.")

6. Uninstall a Package
======================

Use :func:`~pipmaster.package_manager.uninstall` (uncomment to run):

.. code-block:: python

   # print("Uninstalling 'tqdm'...")
   # if pm.uninstall("tqdm"):
   #     print("'tqdm' uninstalled successfully.")
   # else:
   #     print("Failed to uninstall 'tqdm' (or it wasn't installed).")

7. Asynchronous Installation (Example)
======================================

Use the `async_` functions within an `async def` function:

.. code-block:: python

   async def install_async_package():
       pkg = "aiohttp"
       print(f"Asynchronously installing '{pkg}'...")
       if await pm.async_install(pkg):
           print(f"Async install of '{pkg}' succeeded.")
       else:
           print(f"Async install of '{pkg}' failed.")

   # To run the async function:
   # asyncio.run(install_async_package())

Next Steps
==========

Explore the :doc:`user_guide/index` for detailed explanations of features like environment targeting, vulnerability scanning, and more advanced installation options. Check the :doc:`api/index` for the full reference of all functions and classes.