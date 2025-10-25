********************
Installing Packages
********************

`pipmaster` provides several functions for installing packages programmatically. For managing a set of dependencies for an application, the `ensure_*` methods are the most powerful and recommended approach.

The `ensure_*` Philosophy
=========================
The `ensure_packages` and `ensure_requirements` functions are **idempotent**. This means you can run them repeatedly, and they will only perform an action if the environment's state does not match your declared requirements.

They are also **efficient**. They first check all packages, then run a single `pip install` command for only the packages that are missing or need updating. This is much faster than running `pip install` in a loop.

Ensuring Dependencies with `ensure_packages`
--------------------------------------------
This is the recommended way to manage dependencies directly within your code, creating self-contained and self-validating applications. It accepts a string, a list of strings, or a dictionary.

.. code-block:: python
   
   import pipmaster as pm

   # 1. Ensure a single package is present (any version)
   pm.ensure_packages("rich", verbose=True)

   # 2. Ensure a list of packages with version specifiers
   pm.ensure_packages(["pandas", "numpy>=1.20"], verbose=True)

   # 3. Ensure dependencies from a dictionary
   requirements = {
       "requests": ">=2.25.0",
       "tqdm": None  # Any version is acceptable
   }
   pm.ensure_packages(requirements, verbose=True)

   # 4. Force update for packages without a version pin
   # This will update 'tqdm' to the latest version but respect the 'requests' specifier.
   pm.ensure_packages(requirements, always_update=True, verbose=True)


**Advanced: Conditional Git Installation**

You can define a rule to install a package from a Git repository *only if* the currently installed version doesn't meet a specific condition. This is useful for requiring cutting-edge features from a development branch.

.. code-block:: python

   # This rule means: "We need diffusers>=0.25.0. 
   # If not met, install from the main branch on GitHub."
   conditional_req = {
       "name": "diffusers",
       "vcs": "git+https://github.com/huggingface/diffusers.git",
       "condition": ">=0.25.0"
   }

   # This will trigger the git install if an older version is present
   pm.ensure_packages([conditional_req], verbose=True)


Ensuring Dependencies from a File with `ensure_requirements`
-------------------------------------------------------------
This function provides a programmatic and idempotent way to sync your environment with a `requirements.txt` file.

.. code-block:: python
   :caption: requirements.txt

   --extra-index-url https://download.pytorch.org/whl/cu121
   torch
   # A comment
   rich ; python_version >= '3.8'

.. code-block:: python

   import pipmaster as pm

   # Create the file for the example
   with open("requirements.txt", "w") as f:
       f.write("--extra-index-url https://download.pytorch.org/whl/cu121\n")
       f.write("torch\n")
       f.write("rich ; python_version >= '3.8'\n")

   # This single command ensures the environment matches the file.
   # It handles the index-url option and installs only what's needed.
   if pm.ensure_requirements("requirements.txt", verbose=True):
       print("Environment is now in sync with requirements.txt!")


Legacy Installation Methods
===========================

While the `ensure_*` methods are preferred, `pipmaster` also provides direct wrappers around `pip install` commands for simpler, one-off tasks.

Basic Installation
------------------
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
Use :func:`~pipmaster.package_manager.install_requirements` to install all packages listed in a standard `requirements.txt` file. This is a direct wrapper around `pip install -r`. For idempotent checks, use `ensure_requirements` instead.

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