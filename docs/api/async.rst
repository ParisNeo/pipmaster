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

Progress Callbacks
==================
The :py:meth:`~pipmaster.async_package_manager.AsyncPackageManager.ensure_packages` method and :py:func:`~pipmaster.async_package_manager.async_ensure_packages` function accept an optional ``progress_callback`` parameter. This callable can be either synchronous or asynchronous (coroutine) and receives progress updates during package processing.

The callback receives a dictionary with the following keys:

* ``status``: ``"checking"``, ``"processing"``, ``"complete"``, or ``"failed"``
* ``message``: Description of the current operation
* ``package`` / ``packages``: Package name(s) being processed
* ``progress`` / ``total``: Progress counters during the checking phase
* ``success``: Boolean result (in final status)

Example async callback:

.. code-block:: python

   async def progress_handler(data):
       print(f"{data['status']}: {data['message']}")
       if data.get('packages'):
           print(f"  Packages: {data['packages']}")

   await async_ensure_packages(["requests"], progress_callback=progress_handler)