******************
Asynchronous API
******************

This section details the asynchronous components of the ``pipmaster`` library, primarily found within the :py:mod:`pipmaster.async_package_manager` module.

.. automodule:: pipmaster.async_package_manager
   :members:
   :undoc-members:
   :show-inheritance:
   :member-order: bysource

.. note::
   Similar to the synchronous API, async functions like ``async_install`` are exposed at the top level (e.g., ``pipmaster.async_install``) as convenience wrappers around a default :py:class:`~pipmaster.async_package_manager.AsyncPackageManager` instance.

.. warning::
   Functions for checking package status (:py:func:`~pipmaster.package_manager.is_installed`, :py:func:`~pipmaster.package_manager.get_installed_version`, :py:func:`~pipmaster.package_manager.is_version_compatible`) do not have direct async counterparts as they rely on the synchronous ``importlib.metadata`` library. See the :doc:`../user_guide/async` guide for strategies on using them in async code.