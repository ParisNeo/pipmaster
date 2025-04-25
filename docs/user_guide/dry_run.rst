***********
Dry Run Mode
***********

Most `pipmaster` functions that modify the environment (install, uninstall, install_requirements, etc.) support a **dry run** mode.

Enabling Dry Run
================
To enable dry run mode, pass the argument ``dry_run=True`` to the function call.

.. code-block:: python

   import pipmaster as pm

   # Simulate installing requests
   print("Dry run: Installing requests...")
   pm.install("requests", dry_run=True)

   # Simulate uninstalling multiple packages
   print("\nDry run: Uninstalling numpy and pandas...")
   pm.uninstall_multiple(["numpy", "pandas"], dry_run=True)

   # Simulate installing from requirements
   # (Create a dummy file first)
   with open("dummy_reqs.txt", "w") as f: f.write("flask\n")
   print("\nDry run: Installing from dummy_reqs.txt...")
   pm.install_requirements("dummy_reqs.txt", dry_run=True)

What Happens in Dry Run Mode?
=============================
When ``dry_run=True``:

1.  **Logging:** `pipmaster` logs that it is performing a dry run and constructs the command string it *would* have executed.
2.  **No Execution:** The actual `pip` (or `pip-audit`) command is **not** executed via `subprocess`. No changes are made to your environment.
3.  **`--dry-run` Flag (Pip):** For `pip` commands that support it (like `install`, `uninstall`, `download`), `pipmaster` attempts to intelligently insert the `--dry-run` flag into the simulated command string shown in the logs. This flag tells `pip` itself to simulate the operation.
4.  **Return Value:** The function generally returns `True` if the command *could* be simulated (indicating the arguments were valid enough to construct the command), along with a message indicating it was a dry run. It returns `False` only if there was an error *before* the simulation stage (e.g., invalid arguments passed to the `pipmaster` function itself).

Use Cases
=========
*   **Testing:** Verify that your script constructs the correct `pip` commands before actually running them.
*   **Automation Preview:** See what packages *would* be installed or uninstalled by an automation script without modifying the system state.
*   **Debugging:** Help diagnose issues by seeing the exact command `pipmaster` intends to run.

Limitations
===========
*   **Backend Support:** The insertion of the `--dry-run` flag is currently implemented specifically for `pip`. Future backends (like `uv` or `conda`) might have different dry run mechanisms or flags.
*   **Simulation Accuracy:** While `pip --dry-run` simulates dependency resolution, it doesn't perform actual downloads or builds, so it might not catch all potential installation errors. `pipmaster`'s dry run primarily checks the command construction and relies on the backend's dry run capability where available.
*   **Non-Modifying Functions:** Dry run has no effect on functions that only read information (e.g., `is_installed`, `get_installed_version`, `get_package_info`).