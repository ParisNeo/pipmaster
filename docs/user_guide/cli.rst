.. _cli_documentation:

Command Line Interface (CLI)
============================

``pipmaster`` ships with a powerful command‑line interface that mirrors the functionality of the library’s Python API. The CLI is installed as the ``pipmaster`` console entry point when you install the package.

Running ``pipmaster -h`` displays the top‑level help, listing all available sub‑commands. Each sub‑command also supports ``-h``/``--help`` for detailed usage information.

Available Sub‑Commands
----------------------

forge – Create a Portable Python Environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create (or recreate) a virtual environment using a specific portable Python build. The command automatically downloads the requested Python version if it is not already cached.

::

    pipmaster forge -p <python_version> -d <path> [-k <package> ...]

**Options**

* ``-p``, ``--python`` – Target Python version (e.g. ``3.10``, ``3.12``). **Required**.
* ``-d``, ``--path`` – Destination directory for the new virtual environment. **Required**.
* ``-k``, ``--packages`` – Optional list of packages to install immediately after the environment is created.

**Example**

.. code-block:: bash

    pipmaster forge -p 3.12 -d ./my_env -k rich tqdm

equip – Install Packages
~~~~~~~~~~~~~~~~~~~~~~~~

Install one or more packages into an existing environment (or the current interpreter when ``--env .`` is used).

::

    pipmaster equip <package> [<package> ...] [-e <env_path>] [--dry-run]

**Options**

* ``-e``, ``--env`` – Path to a virtual environment directory. Defaults to ``.`` (current environment).
* ``--dry-run`` – Show the pip command that would be executed without performing any changes.

**Example**

.. code-block:: bash

    pipmaster equip numpy pandas -e ./my_env

banish – Uninstall Packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Remove packages from a target environment.

::

    pipmaster banish <package> [<package> ...] [-e <env_path>]

**Options**

* ``-e``, ``--env`` – Path to a virtual environment directory. Defaults to ``.``.

**Example**

.. code-block:: bash

    pipmaster banish matplotlib -e ./my_env

scout – Query Package Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Display version and detailed ``pip show`` information for a single package.

::

    pipmaster scout <package> [-e <env_path>]

**Options**

* ``-e``, ``--env`` – Path to a virtual environment directory. Defaults to ``.``.

**Example**

.. code-block:: bash

    pipmaster scout requests -e ./my_env

scan – Vulnerability Audit
~~~~~~~~~~~~~~~~~~~~~~~~~

Run a vulnerability scan using ``pip‑audit`` against the target environment (or the current interpreter).

::

    pipmaster scan [-e <env_path>]

**Options**

* ``-e``, ``--env`` – Path to a virtual environment directory. Defaults to ``.``.

**Example**

.. code-block:: bash

    pipmaster scan -e ./my_env

Advanced Usage
--------------

All CLI commands forward any additional arguments supported by the underlying ``pip`` or ``pip‑audit`` tools. For example, to install a package from a custom index URL:

.. code-block:: bash

    pipmaster equip torch -e ./my_env -- --index-url https://download.pytorch.org/whl/cu121

The ``forge`` command also respects the same portable‑Python download logic used by the library’s :func:`pipmaster.get_pip_manager_for_version` factory.

Help
----

For a complete list of options and sub‑commands, run:

::

    pipmaster -h

This displays the same help text shown above.
