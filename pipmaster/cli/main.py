import argparse
import sys
from pathlib import Path
import pipmaster as pm
from ascii_colors import ASCIIColors

def get_target_pm(env_path):
    """Helper to get the correct PackageManager based on env path."""
    if env_path == "." or env_path is None:
        return pm.get_pip_manager()
    
    path = Path(env_path)
    # PackageManager can auto-detect python in a venv path or create it if we were initializing
    # But here we assume we are managing an existing one unless it's 'forge'
    try:
        return pm.PackageManager(venv_path=str(path))
    except Exception as e:
        ASCIIColors.error(f"Failed to load environment at {env_path}: {e}")
        sys.exit(1)

def handle_forge(args):
    """Handle the 'forge' command (Create Env with specific Python)."""
    ASCIIColors.bold(f"ðŸ”¨ FORGE: Forging new realm at '{args.path}' using Python {args.python}...")
    
    try:
        # This leverages the portable python manager to download python if needed
        # and create the venv
        pm_instance = pm.get_pip_manager_for_version(args.python, args.path)
        
        ASCIIColors.success(f"âœ… Realm forged successfully at: {args.path}")
        ASCIIColors.info(f"   Python Executable: {pm_instance.target_python_executable}")
        
        if args.packages:
            ASCIIColors.cyan(f"ðŸ›¡ï¸  Equipping initial inventory: {', '.join(args.packages)}")
            pm_instance.install_multiple(args.packages, verbose=True)
            ASCIIColors.success("âœ… Inventory secured.")
            
    except Exception as e:
        ASCIIColors.error(f"â Œ Forge failed: {e}")
        sys.exit(1)

def handle_equip(args):
    """Handle the 'equip' command (Install)."""
    env_label = "current realm" if args.env == "." else args.env
    ASCIIColors.bold(f"ðŸ›¡ï¸  EQUIP: Installing artifacts into {env_label}...")
    
    manager = get_target_pm(args.env)
    
    success = manager.install_multiple(
        args.packages, 
        dry_run=args.dry_run, 
        verbose=True
    )
    
    if success:
        ASCIIColors.success("âœ… Equipment secured.")
    else:
        ASCIIColors.error("â Œ Failed to equip some items.")
        sys.exit(1)

def handle_banish(args):
    """Handle the 'banish' command (Uninstall)."""
    env_label = "current realm" if args.env == "." else args.env
    ASCIIColors.bold(f"ðŸ”¥ BANISH: Removing artifacts from {env_label}...")
    
    manager = get_target_pm(args.env)
    
    success = manager.uninstall_multiple(
        args.packages,
        verbose=True
    )
    
    if success:
        ASCIIColors.success("âœ… Items banished.")
    else:
        ASCIIColors.error("â Œ Failed to banish some items.")
        sys.exit(1)

def handle_scout(args):
    """Handle the 'scout' command (Info)."""
    manager = get_target_pm(args.env)
    
    ASCIIColors.bold(f"ðŸ”  SCOUT: Investigating artifact '{args.package}'...")
    
    if not manager.is_installed(args.package):
        ASCIIColors.warning(f"âš ï¸  Artifact '{args.package}' is NOT present in the target realm.")
        return

    version = manager.get_installed_version(args.package)
    ASCIIColors.info(f"Artifact: {args.package}")
    ASCIIColors.info(f"Version: {version}")
    
    info = manager.get_package_info(args.package)
    if info:
        print("-" * 40)
        print(info.strip())
        print("-" * 40)

def handle_scan(args):
    """Handle the 'scan' command (Vulnerabilities)."""
    manager = get_target_pm(args.env)
    ASCIIColors.bold("ðŸ§ª SCAN: Detecting magical anomalies (vulnerabilities)...")
    
    found, report = manager.check_vulnerabilities()
    
    if found:
        ASCIIColors.red("âš ï¸  Anomalies Detected!")
        print(report)
        sys.exit(1)
    else:
        ASCIIColors.success("âœ… No anomalies found. The perimeter is secure.")

def main():
    parser = argparse.ArgumentParser(
        description="PipMaster CLI: The Ultimate Python Package Warrior",
        prog="pipmaster",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Choose your action")
    
    # FORGE
    p_forge = subparsers.add_parser("forge", help="Create a new environment with a specific Python version")
    p_forge.add_argument("-p", "--python", required=True, help="Target Python version (e.g. 3.10, 3.12)")
    p_forge.add_argument("-d", "--path", required=True, help="Destination path for the environment")
    p_forge.add_argument("-k", "--packages", nargs="*", help="Initial packages to install")
    
    # EQUIP
    p_equip = subparsers.add_parser("equip", help="Install packages into an environment")
    p_equip.add_argument("packages", nargs="+", help="Packages to install")
    p_equip.add_argument("-e", "--env", default=".", help="Path to environment (default: current)")
    p_equip.add_argument("--dry-run", action="store_true", help="Simulate execution")
    
    # BANISH
    p_banish = subparsers.add_parser("banish", help="Uninstall packages from an environment")
    p_banish.add_argument("packages", nargs="+", help="Packages to uninstall")
    p_banish.add_argument("-e", "--env", default=".", help="Path to environment (default: current)")
    
    # SCOUT
    p_scout = subparsers.add_parser("scout", help="Get info about an installed package")
    p_scout.add_argument("package", help="Package name")
    p_scout.add_argument("-e", "--env", default=".", help="Path to environment (default: current)")
    
    # SCAN
    p_scan = subparsers.add_parser("scan", help="Scan for vulnerabilities")
    p_scan.add_argument("-e", "--env", default=".", help="Path to environment (default: current)")

    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return

    if args.command == "forge":
        handle_forge(args)
    elif args.command == "equip":
        handle_equip(args)
    elif args.command == "banish":
        handle_banish(args)
    elif args.command == "scout":
        handle_scout(args)
    elif args.command == "scan":
        handle_scan(args)

if __name__ == "__main__":
    main()
