import pipmaster as pm
import platform
import ascii_colors as logging

# Setup logging for the example
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("--- Starting PipMaster Advanced Usage Example ---")

# --- Example 1: Conditional Installation based on platform and needs ---
logger.info("\n--- Example 1: Conditional Installation ---")

cuda_index = "https://download.pytorch.org/whl/cu121" # Use your relevant CUDA version index

# Define base requirements, potentially with version specifiers
# Using dict allows associating metadata like index_url or custom args
required_packages_dict = {
    "torch": {"index_url": cuda_index, "specifier": ">=2.0.0"}, # Require minimum torch version
    "torchvision": {"index_url": cuda_index},
    "torchaudio": {"index_url": cuda_index},
    "transformers": {"specifier": ">=4.30.0"}, # Require minimum transformers version
    "datasets": {},
    "accelerate": {},
    "peft": {},
    "trl": {},
    "bitsandbytes": {}, # May need specific handling/checks on Windows/CPU
    "scipy": {},
    "protobuf": {},
    "huggingface_hub": {},
    "requests": {"specifier": ">=2.25.0,<3.0.0"}, # Range specifier
    "packaging": {}, # Dependency of pipmaster itself now
}

# Platform specific additions
if platform.system() != "Darwin":
    logger.info("Non-macOS detected, adding xformers requirement.")
    required_packages_dict["xformers"] = {"index_url": cuda_index}
else:
    logger.info("macOS detected, skipping xformers.")

# Check existing packages and install/update if needed
all_ok = True
packages_to_install_or_update = {} # Group by index URL

for pkg_name, details in required_packages_dict.items():
    index_url = details.get("index_url")
    specifier = details.get("specifier")
    is_pkg_installed = pm.is_installed(pkg_name)
    install_reason = ""

    if not is_pkg_installed:
        install_reason = "Not installed"
    elif specifier and not pm.is_version_compatible(pkg_name, specifier):
         installed_version = pm.get_installed_version(pkg_name)
         install_reason = f"Installed version {installed_version} does not meet specifier '{specifier}'"
    # Add more conditions if needed (e.g., always_update flag)

    if install_reason:
        logger.warning(f"Package '{pkg_name}' needs installation/update: {install_reason}")
        pkg_string = f"{pkg_name}{specifier}" if specifier else pkg_name # Construct install string
        if index_url not in packages_to_install_or_update:
            packages_to_install_or_update[index_url] = []
        packages_to_install_or_update[index_url].append(pkg_string)
    else:
        logger.info(f"Package '{pkg_name}' is installed and meets requirements.")


# Perform installations/updates grouped by index
if packages_to_install_or_update:
    logger.info("\n--- Performing required installations/updates ---")
    for index_url, pkgs_to_install in packages_to_install_or_update.items():
        logger.info(f"Installing/Updating for index '{index_url or 'PyPI'}': {', '.join(pkgs_to_install)}")
        # Use install_or_update_multiple which handles both install and upgrade
        success = pm.install_or_update_multiple(pkgs_to_install, index_url=index_url)
        if not success:
            logger.error(f"Failed to install/update packages for index '{index_url or 'PyPI'}'")
            all_ok = False
else:
    logger.info("\nAll required packages are already installed and meet version specifications.")


# --- Example 2: Using install_multiple_if_not_installed (Simpler Scenario) ---
logger.info("\n--- Example 2: Install Multiple If Not Installed ---")

# Scenario: Install basic data science stack if missing, using default PyPI
data_science_stack = ["numpy", "pandas", "matplotlib", "scikit-learn"]
logger.info(f"Checking and installing basic data science stack (if missing): {', '.join(data_science_stack)}")
success_ds = pm.install_multiple_if_not_installed(data_science_stack)
if success_ds:
     logger.info("Data science stack checked/installed successfully.")
else:
     logger.error("Failed to install some packages from the data science stack.")
     all_ok = False


# --- Example 3: Get Package Info ---
logger.info("\n--- Example 3: Get Package Information ---")
if pm.is_installed("packaging"):
    info = pm.get_package_info("packaging")
    if info:
        logger.info("--- packaging package info ---")
        print(info) # Print raw output from 'pip show'
        logger.info("----------------------------")
    else:
        logger.error("Could not get info for 'packaging'.")
else:
    logger.warning("'packaging' is not installed, cannot get info.")


# --- Final Status ---
logger.info("\n--- PipMaster Advanced Usage Example Finished ---")
if all_ok:
    logger.info("All operations concluded successfully.")
else:
    logger.warning("Some operations encountered issues. Check logs above.")