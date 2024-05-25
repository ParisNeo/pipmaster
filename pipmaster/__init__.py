"""
╔════════════════════════════════════════════════════════════════════════╗
║                        🐍✨ PackageManager 3000 ✨🐍                 ║
║────────────────────────────────────────────────────────────────────────║
║ Author: ParisNeo, a computer geek passionate about AI and robotics     ║
║                                                                        ║
║ Description:                                                           ║
║ This Python script is your one-stop-shop for managing packages!        ║
║ It installs, updates, and checks the existence of packages like a      ║
║ boss. It's like having a personal assistant for your Python projects!  ║
║                                                                        ║
║ Features:                                                              ║
║ - Install packages with ease! 🎉🎉                                    ║
║ - Install specific versions like a time traveler! ⏳⏳                ║
║ - Check if packages are installed, like finding unicorns! 🦄🦄        ║
║ - Get package info, because knowledge is power! 🦄 🦄                 ║
║ - Update packages, because everyone loves a makeover! 💅💅            ║
║                                                                        ║
║ Usage:                                                                 ║
║ Just create an instance of PackageManager and call the methods!        ║
║ Example:                                                               ║
║     pm = PackageManager()                                              ║
║     pm.install_version("requests", "2.25.1")                           ║
║                                                                        ║
║ Note: This script uses pip as the default package manager.             ║
║                                                                        ║
║ Fun Fact: This header is 100% funnier than your average docstring!😂😂║
╚════════════════════════════════════════════════════════════════════════╝
"""
import subprocess

class PackageManager:
    def __init__(self, package_manager="pip"):
        self.package_manager = package_manager

    def install(self, package):
        """
        Install a Python package using the specified package manager.

        Args:
            package (str): The name of the package to install.

        Returns:
            bool: True if the package was installed successfully, False otherwise.
        """
        try:
            subprocess.run([self.package_manager, "install", package], check=True)
            print(f"Successfully installed {package}. Abra-cadabra!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}. Oopsie daisy!")
            return False

    def install_version(self, package, version):
        """
        Install a specific version of a Python package using the specified package manager.

        Args:
            package (str): The name of the package to install.
            version (str): The version of the package to install.

        Returns:
            bool: True if the package was installed successfully, False otherwise.
        """
        try:
            subprocess.run([self.package_manager, "install", f"{package}=={version}"], check=True)
            print(f"Successfully installed {package} version {version}. It's like hitting the jackpot!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package} version {version}: {e}. The version fairy is on strike!")
            return False

    def is_installed(self, package):
        """
        Check if a Python package is installed.

        Args:
            package (str): The name of the package to check.

        Returns:
            bool: True if the package is installed, False otherwise.
        """
        try:
            subprocess.run([self.package_manager, "show", package], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"{package} is already installed. It's like finding a unicorn in your backyard!")
            return True
        except subprocess.CalledProcessError:
            print(f"{package} is not installed. It's as elusive as Bigfoot!")
            return False

    def get_package_info(self, package):
        """
        Get information about an installed Python package.

        Args:
            package (str): The name of the package to get information for.

        Returns:
            str: The output of the package manager's show command, containing package information.
        """
        try:
            output = subprocess.check_output([self.package_manager, "show", package], universal_newlines=True)
            print(f"Here's the scoop on {package}:")
            return output
        except subprocess.CalledProcessError as e:
            print(f"Error getting information for {package}: {e}. Looks like the cat's got the info!")
            return None

    def get_installed_version(self, package):
        """
        Get the installed version of a Python package.

        Args:
            package (str): The name of the package to check.

        Returns:
            str: The installed version of the package, or None if the package is not installed.
        """
        try:
            output = subprocess.check_output([self.package_manager, "show", package], universal_newlines=True)
            for line in output.splitlines():
                if line.startswith("Version:"):
                    version = line.split(":", 1)[1].strip()
                    print(f"The installed version of {package} is {version}. It's like finding out your favorite ice cream flavor!")
                    return version
            return None
        except subprocess.CalledProcessError as e:
            print(f"Error getting version for {package}: {e}. The version is playing hide and seek!")
            return None

    def install_or_update(self, package):
        """
        Install or update a Python package.

        Args:
            package (str): The name of the package to install or update.

        Returns:
            bool: True if the package was installed or updated successfully, False otherwise.
        """
        if self.is_installed(package):
            print(f"{package} is already installed. Let's see if it needs a makeover!")
            installed_version = self.get_installed_version(package)
            if installed_version:
                print(f"Updating {package} from version {installed_version}. It's like a software spa day!")
                try:
                    subprocess.run([self.package_manager, "install", "--upgrade", package], check=True)
                    print(f"Successfully updated {package}. New version, who dis?")
                    return True
                except subprocess.CalledProcessError as e:
                    print(f"Error updating {package}: {e}. The update fairy took a day off!")
                    return False
        else:
            print(f"{package} is not installed. Time to add it to your collection!")
            return self.install(package)

if __name__ == "__main__":
    # Example usage
    pm = PackageManager()
    pm.install_version("requests", "2.25.1")
