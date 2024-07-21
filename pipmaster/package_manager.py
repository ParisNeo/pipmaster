import subprocess

class PackageManager:
    def __init__(self, package_manager="pip"):
        self.package_manager = package_manager

    def install(self, package, force_reinstall=False, index_url=None):
        """
        Install a Python package using the specified package manager.

        Args:
            package (str): The name of the package to install.
            force_reinstall (bool): Whether to force reinstall the package.
            index_url (str): Optional URL of the package index to use.

        Returns:
            bool: True if the package was installed successfully, False otherwise.
        """
        command = [self.package_manager, "install"]
        if force_reinstall:
            command.append("--force-reinstall")
        if index_url:
            command.extend(["--index-url", index_url])
        command.append(package)

        try:
            subprocess.run(command, check=True)
            return True
        except subprocess.CalledProcessError as e:
            return False

    def install_multiple(self, packages, force_reinstall=False, index_url=None):
        """
        Install multiple Python packages.

        Args:
            packages (list): A list of package names to install.
            force_reinstall (bool): Whether to force reinstall the packages.
            index_url (str): Optional URL of the package index to use.

        Returns:
            dict: A dictionary with package names as keys and installation success as values.
        """
        results = {}
        for package in packages:
            results[package] = self.install(package, force_reinstall, index_url)
        return results

    def install_version(self, package, version, force_reinstall=False, index_url=None):
        """
        Install a specific version of a Python package using the specified package manager.

        Args:
            package (str): The name of the package to install.
            version (str): The version of the package to install.
            force_reinstall (bool): Whether to force reinstall the package.
            index_url (str): Optional URL of the package index to use.

        Returns:
            bool: True if the package was installed successfully, False otherwise.
        """
        command = [self.package_manager, "install"]
        if force_reinstall:
            command.append("--force-reinstall")
        if index_url:
            command.extend(["--index-url", index_url])
        command.append(f"{package}=={version}")

        try:
            subprocess.run(command, check=True)
            return True
        except subprocess.CalledProcessError as e:
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
                    return version
            return None
        except subprocess.CalledProcessError as e:
            return None

    def install_or_update(self, package, index_url=None):
        """
        Install or update a Python package.

        Args:
            package (str): The name of the package to install or update.
            index_url (str): Optional URL of the package index to use.

        Returns:
            bool: True if the package was installed or updated successfully, False otherwise.
        """
        if self.is_installed(package):
            print(f"{package} is already installed. Let's see if it needs a makeover!")
            installed_version = self.get_installed_version(package)
            if installed_version:
                print(f"Updating {package} from version {installed_version}. It's like a software spa day!")
                try:
                    self.install(package, force_reinstall=True, index_url=index_url)
                    return True
                except subprocess.CalledProcessError as e:
                    print(f"Error updating {package}: {e}. The update fairy took a day off!")
                    return False
        else:
            return self.install(package, index_url=index_url)

# Create a single instance of PackageManager
_pm = PackageManager()

# Create module-level functions that use the _pm instance
def install(package, force_reinstall=False, index_url=None):
    return _pm.install(package, force_reinstall, index_url)

def install_multiple(packages, force_reinstall=False, index_url=None):
    return _pm.install_multiple(packages, force_reinstall, index_url)

def install_version(package, version, force_reinstall=False, index_url=None):
    return _pm.install_version(package, version, force_reinstall, index_url)

def is_installed(package):
    return _pm.is_installed(package)

def get_package_info(package):
    return _pm.get_package_info(package)

def get_installed_version(package):
    return _pm.get_installed_version(package)

def install_or_update(package, index_url=None):
    return _pm.install_or_update(package, index_url)

if __name__ == "__main__":
    pm = PackageManager()
    
    # List of packages to install for PyTorch with CUDA 12.1 support
    packages = [
        "torch",  # PyTorch with CUDA 12.1
        "torchvision",  # torchvision with CUDA 12.1
        "torchaudio"  # torchaudio with CUDA 12.1
    ]
    
    # Specify the index URL for PyTorch packages
    index_url = "https://download.pytorch.org/whl/cu121"

    # Install the packages
    results = pm.install_multiple(packages, force_reinstall=True, index_url=index_url)

    # Print the results
    for package, success in results.items():
        if success:
            print(f"Successfully installed {package}.")
        else:
            print(f"Failed to install {package}.")
