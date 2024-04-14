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
            print(f"Successfully installed {package}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error installing {package}: {e}")
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
            return True
        except subprocess.CalledProcessError:
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
            return output
        except subprocess.CalledProcessError as e:
            print(f"Error getting information for {package}: {e}")
            return None
