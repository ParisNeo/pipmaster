***************
Synchronous API
***************

These classes and functions provide blocking operations suitable for standard Python scripts.

.. currentmodule:: pipmaster.package_manager

Classes
=======

.. autosummary::
   :toctree: _autosummary_sync
   :nosignatures:

   PackageManager
   CondaPackageManager
   UvPackageManager

Module Functions
================

These functions operate on the default `PackageManager` instance, targeting the current Python environment unless a different manager is obtained via :func:`get_pip_manager`.

Factory Function
----------------
.. autosummary::
   :toctree: _autosummary_sync
   :nosignatures:

   get_pip_manager

Installation Functions
----------------------
.. autosummary::
   :toctree: _autosummary_sync
   :nosignatures:

   install
   install_multiple
   install_version
   install_if_missing
   install_multiple_if_not_installed
   install_or_update
   install_or_update_multiple
   install_requirements
   install_edit
   ensure_packages

Checking Functions
------------------
.. autosummary::
   :toctree: _autosummary_sync
   :nosignatures:

   is_installed
   get_installed_version
   is_version_compatible
   get_package_info

Uninstallation Functions
------------------------
.. autosummary::
   :toctree: _autosummary_sync
   :nosignatures:

   uninstall
   uninstall_multiple

Other Utility Functions
-----------------------
.. autosummary::
   :toctree: _autosummary_sync
   :nosignatures:

   check_vulnerabilities

Deprecated Functions
--------------------
.. autosummary::
   :toctree: _autosummary_sync
   :nosignatures:

   is_version_higher
   is_version_exact

Backend Factory Functions (Not Implemented)
-------------------------------------------
.. autosummary::
   :toctree: _autosummary_sync
   :nosignatures:

   get_conda_manager
   get_uv_manager

.. note::
    The detailed documentation for each function and class method listed above can be found on the pages generated in the ``_autosummary_sync`` directory.