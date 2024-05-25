# pipmaster

[![GitHub stars](https://img.shields.io/github/stars/ParisNeo/pipmaster.svg?style=social&label=Stars)](https://github.com/ParisNeo/pipmaster)
[![PyPI version](https://badge.fury.io/py/pipmaster.svg)](https://badge.fury.io/py/pipmaster)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/ParisNeo/pipmaster/blob/main/LICENSE)

## 🎩✨ Welcome to pipmaster! ✨🎩

Hey there, fellow Pythonista! 🐍 Ever felt like managing packages is like herding cats? Well, fear not! pipmaster is here to save the day! It's like having a magical wand that installs, updates, and checks packages for you. Because who doesn't want a personal assistant for their Python projects? 🌟

### 🚀 Features

- **Install packages with ease!** 🎉
- **Install specific versions like a time traveler!** ⏳
- **Check if packages are installed, like finding unicorns!** 🦄
- **Get package info, because knowledge is power!** 📚
- **Update packages, because everyone loves a makeover!** 💅

### 🛠️ Installation

First things first, let's get pipmaster installed. It's easier than making a cup of coffee!

```shell
pip install pipmaster
```

### 🎬 Usage

Here's where the magic happens. Create an instance of `PackageManager` and let the fun begin!

```python
from pipmaster import PackageManager

# Create a PackageManager instance
pm = PackageManager()

# Install a package
pm.install("requests")

# Install a specific version of a package
pm.install_version("requests", "2.25.1")

# Check if a package is installed
pm.is_installed("requests")

# Get information about a package
info = pm.get_package_info("requests")
print(info)

# Get the installed version of a package
version = pm.get_installed_version("requests")
print(f"Installed version: {version}")

# Install or update a package
pm.install_or_update("requests")
```

### 📚 Documentation

For more detailed information, check out our [documentation](https://github.com/ParisNeo/pipmaster/wiki). It’s like a treasure map for your coding adventures! 🗺️

### 🤝 Contributing

We welcome contributions from everyone! Whether you're a coding wizard or just getting started, feel free to join the fun. Check out our [contributing guidelines](https://github.com/ParisNeo/pipmaster/blob/main/CONTRIBUTING.md).

### 📝 License

pipmaster is licensed under the Apache 2.0 License. For more details, see the [LICENSE](https://github.com/ParisNeo/pipmaster/blob/main/LICENSE) file.

### 🌟 Show Your Support

If you like pipmaster, give us a star on GitHub! ⭐ It's like giving us a virtual high-five! 🙌

### 📞 Contact

Have questions, suggestions, or just want to say hi? Reach out to us!

- **Twitter:** [@ParisNeo_AI](https://twitter.com/ParisNeo_AI)
- **Discord:** [Join our Discord](https://discord.gg/BDxacQmv)
- **Sub-Reddit:** [r/lollms](https://www.reddit.com/r/lollms/)
- **Instagram:** [@spacenerduino](https://www.instagram.com/spacenerduino/)

### 🎥 YouTube

Don't forget to check out our YouTube channel. Hit that subscribe button and join us on an epic coding journey!

- **Catchphrase:** Hi there
- **Ending phrase:** See ya

---

### 🌈 Add Some Color to Your Console with ASCIIColors! 🌈

Feeling like your console output is as dull as a rainy Monday? Say no more! Introducing **ASCIIColors**! It's the ultimate tool to add a splash of color and style to your console text. Think of it as the confetti cannon for your terminal! 🎉

#### Features

- **Colorful Text:** Make your messages pop with vibrant colors! 🌟
- **Stylish Output:** Bold, underline, and more! It's like giving your text a fashion makeover! 💃
- **Easy to Use:** Simpler than tying your shoelaces! 👟

#### Installation

```shell
pip install asciicolors
```

#### Usage

Here's an example to make your console look like it's ready for a party:

```python
from asciicolors import ASCIIColors

# Print an error message
ASCIIColors.error("This is an error message")

# Print a success message
ASCIIColors.success("Operation successful")

# Print a warning message
ASCIIColors.warning("Warning: This action cannot be undone")

# Print text in bold and underline style
ASCIIColors.bold("Important message", ASCIIColors.color_bright_blue)
ASCIIColors.underline("Underlined text", ASCIIColors.color_bright_green)

# Use specific colors directly
ASCIIColors.yellow("Yellow text")
ASCIIColors.red("Red text")
ASCIIColors.green("Green text")
ASCIIColors.cyan("Cyan text")

ASCIIColors.multicolor(["Green text","red text","yellow text"],[ASCIIColors.color_green, ASCIIColors.color_red, ASCIIColors.color_yellow])
```

Trace and color your exceptions using `trace_exception`: 

```python
# Trace all your exceptions using:
from asciicolors import trace_exception

try:
    #some nasty stuff that can crush
except Exception as ex:
    trace_exception(ex)

```

#### Documentation

For more details, hop on over to the [ASCIIColors documentation](https://github.com/ParisNeo/ascii_colors). It's your colorful adventure guide! 🌈

---

Happy coding, and may the pip be with you! 🐍✨