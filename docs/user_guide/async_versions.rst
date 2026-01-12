*****************************
Async Factory for Portable Python
*****************************

When you need to work with a **portable Python** version (e.g., 3.10, 3.12) in an asynchronous context, ``pipmaster`` now provides a dedicated factory:

.. code-block:: python

   import pipmaster as pm
   import asyncio

   async def main():
       # Create an AsyncPackageManager that uses a portable Python 3.12
       async_pm = pm.get_async_pip_manager_for_version("3.12", "./my_portable_venv")
       
       # Install a package asynchronously in that environment
       await async_pm.install("rich", verbose=True)

       # Verify installation (run in executor because ``is_installed`` is sync)
       loop = asyncio.get_running_loop()
       installed = await loop.run_in_executor(None, async_pm.is_installed, "rich")
       print(f"'rich' installed? {installed}")

   asyncio.run(main())

**What it does**

* Uses the synchronous ``get_pip_manager_for_version`` factory to download / locate the requested portable Python build.
* Creates (or re‑uses) a virtual environment at the supplied ``venv_path``.
* Returns an ``AsyncPackageManager`` instance that targets that portable interpreter, giving you full async ``install`` / ``uninstall`` / ``ensure`` capabilities.

**When to use**

* Automated CI pipelines that need a specific Python version without relying on the system interpreter.
* Applications that spin up temporary environments on‑the‑fly and want non‑blocking package management.
* Any scenario where you would previously call ``get_pip_manager_for_version`` synchronously but now need async behaviour.

**Parameters**

* ``target_python_version`` (str): The portable Python version, e.g. ``"3.12"``, ``"3.11"``, or a full ``"3.12.9"``.
* ``venv_path`` (str): Directory where the virtual environment should be created or used.

**Returns**

An :class:`pipmaster.async_package_manager.AsyncPackageManager` instance ready for async operations.

**Example with a requirements file**

.. code-block:: python

   async def ensure_requirements():
       async_pm = pm.get_async_pip_manager_for_version("3.12", "./venv3_12")
       await async_pm.ensure_requirements("requirements.txt", verbose=True)

This new page is automatically linked from the **User Guide** table of contents, making it easy to discover the async portable‑Python workflow.
