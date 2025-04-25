******************
Asynchronous API
******************

These classes and functions provide non-blocking operations using `asyncio`, suitable for asynchronous applications.

.. currentmodule:: pipmaster.async_package_manager

Classes
=======

.. autosummary::
   :toctree: _autosummary_async
   :nosignatures:

   AsyncPackageManager

Module Functions
================

These functions operate on the default `AsyncPackageManager` instance, targeting the current Python environment.

.. autosummary::
   :toctree: _autosummary_async
   :nosignatures:

   async_install
   async_install_if_missing
   async_check_vulnerabilities
   # Add others here as they are implemented, e.g.:
   # async_uninstall
   # async_install_multiple

.. note::
    The detailed documentation for each function and class method listed above can be found on the pages generated in the ``_autosummary_async`` directory.

.. warning::
    Functions for checking package status (:func:`~pipmaster.package_manager.is_installed`, :func:`~pipmaster.package_manager.get_installed_version`, :func:`~pipmaster.package_manager.is_version_compatible`) do not have direct async counterparts as they rely on the synchronous ``importlib.metadata`` library. See the :doc:`../user_guide/async` guide for strategies on using them in async code.