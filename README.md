# pipmaster

[![GitHub stars](https://img.shields.io/github/stars/ParisNeo/pipmaster.svg?style=social&label=Stars)](https://github.com/ParisNeo/pipmaster)
[![PyPI version](https://badge.fury.io/py/pipmaster.svg)](https://badge.fury.io/py/pipmaster)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/ParisNeo/pipmaster/blob/main/LICENSE)

A simple and versatile Python package manager for automating installation and verification across platforms.

## Installation

```
pip install pipmaster
```

## Usage

```python
from pipmaster import PackageManager

# Create a PackageManager instance
pm = PackageManager()

# Install a package
pm.install("requests")

# Check if a package is installed
is_installed = pm.is_installed("numpy")
print(f"NumPy is installed: {is_installed}")

# Get information about an installed package
package_info = pm.get_package_info("pandas")
print(package_info)
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on the [GitHub repository](https://github.com/ParisNeo/pipmaster).

## Author

- ParisNeo ([@ParisNeo_AI](https://twitter.com/ParisNeo_AI))

## Social

- Twitter: [@ParisNeo_AI](https://twitter.com/ParisNeo_AI)
- Discord: [https://discord.gg/BDxacQmv](https://discord.gg/BDxacQmv)
- Sub-Reddit: [r/lollms](https://www.reddit.com/r/lollms/)
- Instagram: [https://www.instagram.com/spacenerduino/](https://www.instagram.com/spacenerduino/)

## License

This project is licensed under the [Apache 2.0 License](LICENSE).