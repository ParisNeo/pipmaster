#!/usr/bin/env python
import sys
import platform
import rich

print(f"Running inside: {sys.executable}")
print(f"Python {platform.python_version()} on {platform.system()}")
rich.print("[bold green]Hello from the custom venv![/bold green]")
