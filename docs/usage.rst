Usage
=====

This section provides examples and guides on how to use pipmaster.

.. code-block:: python

   import pipmaster as pm

   # Install a package
   pm.install("requests")

   # Check if installed with version specifier
   if pm.is_installed("numpy", ">=1.20"):
       print("Compatible NumPy version found!")

   # Install multiple if missing
   pm.install_multiple_if_not_installed(["pandas", "matplotlib"])

   # Target a different environment
   other_env_pm = pm.get_pip_manager("/path/to/other/venv/bin/python")
   other_env_pm.install("scikit-learn")

   # Check vulnerabilities (requires pipmaster[audit])
   found, output = pm.check_vulnerabilities()
   if found:
       print("Vulnerabilities detected!")
       print(output)

   # --- Async Usage ---
   import asyncio

   async def main():
       success = await pm.async_install("aiohttp")
       if success:
           print("aiohttp installed asynchronously")

   # asyncio.run(main())


*(More detailed examples will be added here)*