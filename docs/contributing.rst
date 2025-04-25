************
Contributing
************

Contributions to `pipmaster` are welcome!

Reporting Issues
================
If you encounter a bug, have a question, or want to suggest a feature, please check the `GitHub Issues <https://github.com/ParisNeo/pipmaster/issues>`_ page first to see if a similar issue already exists.

If not, feel free to open a new issue. Please provide:

*   A clear description of the issue or feature request.
*   Steps to reproduce the bug (if applicable).
*   Your Python version and operating system.
*   The version of `pipmaster` you are using.
*   Any relevant error messages or logs.

Submitting Pull Requests
========================
If you'd like to contribute code:

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally: `git clone https://github.com/YourUsername/pipmaster.git`
3.  **Create a new branch** for your changes: `git checkout -b feature/your-feature-name` or `git checkout -b fix/issue-number`
4.  **Set up a development environment:** It's recommended to use a virtual environment.
    .. code-block:: bash

       python -m venv venv
       source venv/bin/activate  # Linux/macOS
       # venv\Scripts\activate  # Windows
       pip install -e ".[dev]" # Install in editable mode with dev dependencies

5.  **Make your changes.** Ensure your code follows the project's style (use `ruff check .` and `ruff format .`).
6.  **Add tests** for your changes in the `tests/` directory. Run tests using `pytest`.
7.  **Update documentation** in the `docs/` directory if you added or changed features. Build the docs locally (`sphinx-build -b html docs docs/_build/html`) to check for errors.
8.  **Commit your changes:** `git commit -am "feat: Add feature X"` or `git commit -am "fix: Resolve issue Y"`
9.  **Push to your fork:** `git push origin feature/your-feature-name`
10. **Open a Pull Request** on the `ParisNeo/pipmaster` repository. Provide a clear description of your changes.

Thank you for contributing!