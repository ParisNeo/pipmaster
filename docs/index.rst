************
Installation
************

`pipmaster` requires **Python 3.8 or higher**.

Basic Installation
==================

You can install the core `pipmaster` library using pip:

.. code-block:: bash

   pip install pipmaster

This provides all the core functionality for installing, checking, and managing packages using `pip` as the backend.

Optional Features
=================

`pipmaster` offers optional features that require extra dependencies. Install them using extras syntax (e.g., `pip install pipmaster[extra]`).

Vulnerability Auditing (`[audit]`)
----------------------------------
To enable the :func:`~pipmaster.package_manager.check_vulnerabilities` and :func:`~pipmaster.async_package_manager.async_check_vulnerabilities` functions, which use `pip-audit`_, you need to install the `audit` extra:

.. code-block:: bash

   pip install pipmaster[audit]

.. _pip-audit: https://github.com/pypa/pip-audit

Development Tools (`[dev]`)
---------------------------
If you want to contribute to `pipmaster` or run tests, install the `dev` extra. This includes tools like `pytest`, `pytest-asyncio`, `ruff`, `mypy`, `sphinx`, and `sphinx-rtd-theme`.

.. code-block:: bash

   # For regular install with dev tools
   pip install pipmaster[dev]

   # For editable install during development
   git clone https://github.com/ParisNeo/pipmaster.git
   cd pipmaster
   pip install -e .[dev]

All Extras (`[all]`)
--------------------
To install all optional dependencies at once:

.. code-block:: bash

   pip install pipmaster[all]

   # Or for editable install:
   # pip install -e .[all]