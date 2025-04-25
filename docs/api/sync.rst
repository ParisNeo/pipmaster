***************
Synchronous API
***************

This section details the synchronous components of the ``pipmaster`` library, primarily found within the :py:mod:`pipmaster.package_manager` module.

.. automodule:: pipmaster.package_manager
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

.. note::
   Many functions documented here (like ``install``, ``is_installed``, etc.) are also exposed directly at the top level (e.g., ``pipmaster.install``). These are convenience wrappers around the methods of a default :py:class:`~pipmaster.package_manager.PackageManager` instance targeting the current Python environment. Use the top-level imports for simplicity or instantiate :py:class:`~pipmaster.package_manager.PackageManager` directly (often via :py:func:`~pipmaster.package_manager.get_pip_manager`) for more control, especially when targeting different environments.