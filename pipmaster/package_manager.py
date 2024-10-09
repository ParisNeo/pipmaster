import subprocess
import sys
from ascii_colors import ASCIIColors
import pkg_resources
class PackageManager:
    def __init__(self, package_manager=None):
        if package_manager is None:
            package_manager = f'"{sys.executable}" -m pip'
        self.package_manager = package_manager

    def _run_pip_command(self, command):
        """
        Run a pip command and return the output.
        """
        try:
            result = subprocess.run(self.package_manager.split() + command, 
                                    check=True, capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"Error running pip command: {e}")
            return None

    def install(self, package, index_url=None, force_reinstall=False, upgrade=True):
        command = ["install", package]
        if force_reinstall:
            command.append("--force-reinstall")
        if upgrade:
            command.append("--upgrade")
        if index_url:
            command.extend(["--index-url", index_url])
        return self._run_pip_command(command) is not None

    def install_multiple(self, packages, index_url=None, force_reinstall=False):
        command = ["install"] + packages
        if force_reinstall:
            command.append("--force-reinstall")
        if index_url:
            command.extend(["--index-url", index_url])
        return self._run_pip_command(command) is not None

    def install_version(self, package, version, index_url=None, force_reinstall=False):
        command = ["install", f"{package}=={version}"]
        if force_reinstall:
            command.append("--force-reinstall")
        if index_url:
            command.extend(["--index-url", index_url])
        return self._run_pip_command(command) is not None

    def is_installed(self, package):
        try:
            pkg_resources.get_distribution(package)
            return True
        except pkg_resources.DistributionNotFound:
            return False

    def get_package_info(self, package):
        return self._run_pip_command(["show", package])

    def get_installed_version(self, package):
        try:
            return pkg_resources.get_distribution(package).version
        except pkg_resources.DistributionNotFound:
            return None

    def install_or_update(self, package, index_url=None, force_reinstall=False):
        if self.is_installed(package):
            print(f"{package} is already installed. Updating if necessary.")
            return self.install(package, index_url, force_reinstall=True, upgrade=True)
        else:
            return self.install(package, index_url, force_reinstall)

    def uninstall(self, package):
        return self._run_pip_command(["uninstall", "-y", package]) is not None

    def uninstall_multiple(self, packages):
        return self._run_pip_command(["uninstall", "-y"] + packages) is not None

    def install_or_update_multiple(self, packages, index_url=None, force_reinstall=False):
        return self.install_multiple(packages, index_url, force_reinstall)
    
    
# Create a single instance of PackageManager
_pm = PackageManager()

# Create module-level functions that use the _pm instance
def install(package, index_url=None, force_reinstall=False, upgrade=True):
    return _pm.install(package, index_url, force_reinstall, upgrade)

def install_multiple(packages, index_url=None, force_reinstall=False):
    return _pm.install_multiple(packages, index_url, force_reinstall)

def install_version(package, version, index_url=None, force_reinstall=False):
    return _pm.install_version(package, version, index_url, force_reinstall)

def is_installed(package):
    return _pm.is_installed(package)

def get_package_info(package):
    return _pm.get_package_info(package)

def get_installed_version(package):
    return _pm.get_installed_version(package)

def install_or_update(package, index_url=None, force_reinstall=False):
    return _pm.install_or_update(package, index_url, force_reinstall)

def uninstall(package):
    return _pm.uninstall(package)

def uninstall_multiple(packages):
    return _pm.uninstall_multiple(packages)

def install_or_update_multiple(package, index_url=None, force_reinstall=False):
    return _pm.install_or_update_multiple(package,index_url, force_reinstall)

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
    if results:
        print(f"Successfully installed {packages}.")
    else:
        print(f"Failed to install {packages}.")
