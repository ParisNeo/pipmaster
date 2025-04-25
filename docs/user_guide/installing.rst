********************
Installing Packages
********************

`pipmaster` provides several functions for installing packages programmatically.

Basic Installation
==================
Use :func:`~pipmaster.package_manager.install` to install a single package. By default, it acts like `pip install --upgrade`, installing the package if missing or upgrading it if already present.

.. code-block:: python

   import pipmaster as pm

   # Install the latest version of 'requests', or upgrade if already installed
   pm.install("requests")

   # Install 'numpy' but *don't* upgrade it if it's already installed
   pm.install("numpy", upgrade=False)

   # Force reinstall 'pandas', even if the latest version is present
   pm.install("pandas", force_reinstall=True)

Installing Multiple Packages
============================
Use :func:`~pipmaster.package_manager.install_multiple` to install or upgrade several packages in a single `pip` command, which is generally more efficient.

.. code-block:: python

   packages_to_install = ["matplotlib", "seaborn", "plotly"]
   pm.install_multiple(packages_to_install)

Installing Specific Versions
============================
You can specify versions directly in the package string (PEP 508 format) passed to :func:`~pipmaster.package_manager.install` or :func:`~pipmaster.package_manager.install_multiple`. Alternatively, use :func:`~pipmaster.package_manager.install_version` for installing an exact version.

.. code-block:: python

   # Using install with version specifiers
   pm.install("requests>=2.25.0")
   pm.install("django<4.0")
   pm.install_multiple(["pandas==1.5.3", "numpy~=1.23.0"]) # Compatible release

   # Using install_version for an exact version
   pm.install_version("colorama", "0.4.6")

Conditional Installation
========================

Install Only if Missing
-----------------------
Use :func:`~pipmaster.package_manager.install_multiple_if_not_installed` to install packages *only* if they are not currently found in the environment. This function **does not** check version compatibility.

.. code-block:: python

   # Install 'tqdm' and 'python-dotenv' only if they aren't already installed
   dev_tools = ["tqdm", "python-dotenv"]
   pm.install_multiple_if_not_installed(dev_tools)

Install Based on Version Requirements
-------------------------------------
Use :func:`~pipmaster.package_manager.install_if_missing` to install a package only if it's missing *or* if the installed version doesn't meet the specified requirement (using ``version_specifier``).

.. code-block:: python

   # Ensure numpy is at least version 1.21.0
   pm.install_if_missing("numpy", version_specifier=">=1.21.0")

   # Ensure requests is exactly version 2.28.1
   pm.install_if_missing("requests", version_specifier="==2.28.1")

   # Ensure requests is installed, and update to latest if already present
   pm.install_if_missing("requests", always_update=True)

Installing from Requirements Files
==================================
Use :func:`~pipmaster.package_manager.install_requirements` to install all packages listed in a standard `requirements.txt` file.

.. code-block:: python
   :caption: requirements.txt

   click>=8.0
   flask
   # This is a comment
   rich ; python_version >= '3.6'

.. code-block:: python

   # Create the file first for the example
   with open("requirements.txt", "w") as f:
       f.write("click>=8.0\nflask\nrich ; python_version >= '3.6'\n")

   pm.install_requirements("requirements.txt")

Installing in Editable Mode
===========================
Use :func:`~pipmaster.package_manager.install_edit` for installing local packages in editable mode (`pip install -e`).

.. code-block:: python

   # Assuming you have a package source in a directory named 'my_local_project'
   # pm.install_edit("./my_local_project") # Uncomment to run

Using Custom Index URLs
=======================
All installation functions accept an ``index_url`` parameter to specify a custom Python Package Index.

.. code-block:: python

   pytorch_index = "https://download.pytorch.org/whl/cu121" # Example
   pm.install("torch", index_url=pytorch_index)
   pm.install_multiple(["torchvision", "torchaudio"], index_url=pytorch_index)
   pm.install_requirements("torch_reqs.txt", index_url=pytorch_index)

Passing Extra Arguments
=======================
All installation functions also accept an ``extra_args`` parameter, which is a list of strings to be appended to the `pip` command line.

.. code-block:: python

   # Example: Install with --no-cache-dir and --prefer-binary
   pm.install("somepackage", extra_args=["--no-cache-dir", "--prefer-binary"])