#!/usr/bin/env python
"""
PipMaster CLI: The Ultimate Python Package Warrior
Enhanced with ASCIIColors Rich UI Components
"""

import argparse
import sys
from pathlib import Path
import pipmaster as pm
from ascii_colors import ASCIIColors, rich

# Emoji constants for consistent visual language
EMOJI = {
    "forge": "🔨",
    "equip": "📦",
    "banish": "🗑️",
    "scout": "🔍",
    "scan": "🛡️",
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "package": "📦",
    "python": "🐍",
    "star": "⭐",
    "rocket": "🚀",
    "sparkles": "✨",
    "gear": "⚙️",
    "shield": "🛡️",
    "trash": "🗑️",
    "mag": "🔍",
    "check": "✓",
    "cross": "✗",
    "arrow": "➜",
    "bullet": "•",
    "fire": "🔥",
}

def get_target_pm(env_path):
    """Helper to get the correct PackageManager based on env path."""
    if env_path == "." or env_path is None:
        return pm.get_pip_manager()
    
    path = Path(env_path)
    try:
        return pm.PackageManager(venv_path=str(path))
    except Exception as e:
        ASCIIColors.panel(
            f"[bold red]{EMOJI['error']} Failed to load environment at {env_path}:[/bold red]\n{e}",
            title=f"[bold red]{EMOJI['error']} Error[/bold red]",
            border_style="red",
            box="round"
        )
        sys.exit(1)

def print_header():
    """Print the beautiful PipMaster header."""
    header_content = (
        f"[bold cyan]{EMOJI['rocket']} PipMaster[/bold cyan] [dim]v1.1.0[/dim]\n"
        f"[white]The Ultimate Python Package Warrior[/white] {EMOJI['star']}\n"
        f"[dim]Your packages, your way, with style {EMOJI['sparkles']}[/dim]"
    )
    
    ASCIIColors.panel(
        header_content,
        border_style="bold cyan",
        box="double",
        padding=(1, 2)
    )
    print()

def handle_forge(args):
    """Handle the 'forge' command (Create Env with specific Python)."""
    # Create immersive panel with emoji
    forge_content = (
        f"[bold cyan]{EMOJI['forge']} Forging New Python Environment[/bold cyan]\n\n"
        f"{EMOJI['python']} [bold]Version:[/bold] [green]{args.python}[/green]\n"
        f"{EMOJI['package']} [bold]Location:[/bold] [blue]{args.path}[/blue]\n"
        f"{EMOJI['gear']} [bold]Status:[/bold] [yellow]Initializing...[/yellow]"
    )
    
    ASCIIColors.panel(
        forge_content,
        title=f"[bold]{EMOJI['forge']} FORGE[/bold]",
        border_style="cyan",
        box="round",
        padding=(1, 2)
    )
    
    try:
        # Use an elegant moon spinner for the download phase
        with ASCIIColors.status(
            f"[bold cyan]{EMOJI['rocket']} Summoning portable Python {args.python}...[/bold cyan]",
            spinner="moon",
            spinner_style="bold cyan"
        ) as status:
            pm_instance = pm.get_pip_manager_for_version(args.python, args.path)
            status.update(f"[bold green]{EMOJI['check']} Python {args.python} ready![/bold green]")
        
        # Success panel with rich details
        success_content = (
            f"[bold green]{EMOJI['success']} Environment Forged Successfully![/bold green]\n\n"
            f"{EMOJI['python']} [dim]Interpreter:[/dim] [white]{pm_instance.target_python_executable}[/white]\n"
            f"{EMOJI['check']} [dim]Status:[/dim] [green]Ready for action[/green] {EMOJI['fire']}"
        )
        
        ASCIIColors.panel(
            success_content,
            title=f"[bold green]{EMOJI['success']} Success[/bold green]",
            border_style="green",
            box="round",
            padding=(1, 2)
        )
        
        if args.packages:
            # Package installation panel
            pkg_content = (
                f"[bold blue]{EMOJI['package']} Initial Package Manifest[/bold blue]\n\n"
                + "\n".join([f"  {EMOJI['bullet']} [cyan]{pkg}[/cyan]" for pkg in args.packages])
            )
            
            ASCIIColors.panel(
                pkg_content,
                title=f"[bold]{EMOJI['package']} Packages[/bold]",
                border_style="blue",
                box="round"
            )
            
            # Live display for installation progress
            with ASCIIColors.live(
                f"[dim]{EMOJI['gear']} Preparing installation sequence...[/dim]"
            ) as live:
                total = len(args.packages)
                for i, pkg in enumerate(args.packages, 1):
                    live.update(rich.Text.from_markup(
                        f"[bold cyan]{EMOJI['rocket']} Installing {i}/{total}:[/bold cyan] "
                        f"[white]{pkg}[/white] {EMOJI['gear']}"
                    ))
                    # Small delay for visual effect
                    import time
                    time.sleep(0.1)
                
                live.update(rich.Text.from_markup(
                    f"[bold green]{EMOJI['success']} All packages installed![/bold green]"
                ))
            
            success = pm_instance.install_multiple(args.packages, verbose=False)
            if not success:
                ASCIIColors.panel(
                    f"[bold red]{EMOJI['cross']} Failed to install some packages[/bold red]\n"
                    f"{EMOJI['info']} Check the logs for details.",
                    title=f"[bold red]{EMOJI['error']} Error[/bold red]",
                    border_style="red",
                    box="double"
                )
                sys.exit(1)
            
            # Final success with package count
            ASCIIColors.panel(
                f"[bold green]{EMOJI['success']} Installed {len(args.packages)} package(s)[/bold green]",
                border_style="green",
                box="round"
            )
            
    except Exception as e:
        ASCIIColors.panel(
            f"[bold red]{EMOJI['error']} Forge Failed[/bold red]\n\n"
            f"[red]{e}[/red]\n\n"
            f"[dim]{EMOJI['info']} Try a different Python version or check your connection.[/dim]",
            title=f"[bold red]{EMOJI['error']} Critical Error[/bold red]",
            border_style="bold red",
            box="double",
            padding=(1, 2)
        )
        sys.exit(1)

def handle_equip(args):
    """Handle the 'equip' command (Install)."""
    env_label = "current environment" if args.env == "." else args.env
    
    # Beautiful package table
    pkg_rows = [[f"{EMOJI['package']} [cyan]{pkg}[/cyan]", "[green]Install/Update[/green]"] 
                for pkg in args.packages]
    
    pkg_table = ASCIIColors.table(
        f"{EMOJI['package']} Package", f"{EMOJI['gear']} Action",
        rows=pkg_rows,
        title=f"[dim]Target: {env_label}[/dim]",
        box="round",
        show_lines=True,
        border_style="cyan"
    )
    
    # Header panel
    ASCIIColors.panel(
        f"[bold green]{EMOJI['equip']} EQUIP — Arming Your Environment[/bold green]",
        border_style="green",
        box="round",
        padding=(0, 2)
    )
    rich.print(pkg_table)
    
    if args.dry_run:
        ASCIIColors.panel(
            f"[bold yellow]{EMOJI['warning']} Dry Run Mode[/bold yellow]\n"
            f"[dim]No changes will be made — simulation only[/dim]",
            border_style="yellow",
            box="round"
        )
    
    manager = get_target_pm(args.env)
    
    # Animated installation with star spinner
    with ASCIIColors.status(
        f"[bold green]{EMOJI['rocket']} Equipping {len(args.packages)} package(s) into {env_label}...[/bold green]",
        spinner="star",
        spinner_style="bold green"
    ) as status:
        success = manager.install_multiple(
            args.packages, 
            dry_run=args.dry_run, 
            verbose=False
        )
        if success:
            status.update(f"[bold green]{EMOJI['check']} Installation complete![/bold green]")
    
    if success:
        # Celebration panel
        success_content = (
            f"[bold green]{EMOJI['success']} Successfully Equipped![/bold green]\n\n"
            f"{EMOJI['package']} [white]{len(args.packages)}[/white] package(s) ready for action\n"
            f"{EMOJI['sparkles']} Your environment is now more powerful!"
        )
        
        ASCIIColors.panel(
            success_content,
            title=f"[bold green]{EMOJI['check']} Complete[/bold green]",
            border_style="green",
            box="round",
            padding=(1, 2)
        )
    else:
        ASCIIColors.panel(
            f"[bold red]{EMOJI['cross']} Failed to equip some packages[/bold red]\n\n"
            f"[dim]{EMOJI['info']} Check logs for details. Common fixes:[/dim]\n"
            f"  {EMOJI['bullet']} Check your internet connection\n"
            f"  {EMOJI['bullet']} Verify package names are correct\n"
            f"  {EMOJI['bullet']} Try with --verbose for more details",
            title=f"[bold red]{EMOJI['error']} Error[/bold red]",
            border_style="red",
            box="double"
        )
        sys.exit(1)

def handle_banish(args):
    """Handle the 'banish' command (Uninstall)."""
    env_label = "current environment" if args.env == "." else args.env
    
    # Dramatic warning panel with package list
    pkg_list = "\n".join([f"  {EMOJI['cross']} [red]{pkg}[/red]" for pkg in args.packages])
    
    banish_content = (
        f"[bold red]{EMOJI['banish']} BANISH — Package Removal[/bold red]\n\n"
        f"The following packages will be [bold red]permanently removed[/bold red] from:\n"
        f"[dim]{env_label}[/dim]\n\n"
        f"{pkg_list}\n\n"
        f"[yellow]{EMOJI['warning']} This action cannot be undone.[/yellow]"
    )
    
    ASCIIColors.panel(
        banish_content,
        title=f"[bold red]{EMOJI['warning']} Confirm Removal[/bold red]",
        border_style="bold red",
        box="double",
        padding=(1, 2)
    )
    
    manager = get_target_pm(args.env)
    
    # Pulse spinner for removal (more intense)
    with ASCIIColors.status(
        f"[bold red]{EMOJI['trash']} Banishing packages...[/bold red]",
        spinner="pulse",
        spinner_style="bold red"
    ) as status:
        success = manager.uninstall_multiple(
            args.packages,
            verbose=False
        )
        if success:
            status.update(f"[bold green]{EMOJI['check']} Banishment complete![/bold green]")
    
    if success:
        ASCIIColors.panel(
            f"[bold green]{EMOJI['success']} Successfully Banished[/bold green]\n\n"
            f"[white]{len(args.packages)}[/white] package(s) removed from your realm.",
            title=f"[bold green]{EMOJI['trash']} Banished[/bold green]",
            border_style="green",
            box="round"
        )
    else:
        ASCIIColors.panel(
            f"[bold red]{EMOJI['cross']} Failed to banish some packages[/bold red]",
            title=f"[bold red]{EMOJI['error']} Error[/bold red]",
            border_style="red",
            box="round"
        )
        sys.exit(1)

def handle_scout(args):
    """Handle the 'scout' command (Info)."""
    manager = get_target_pm(args.env)
    
    # Scout header
    ASCIIColors.panel(
        f"[bold blue]{EMOJI['scout']} SCOUT — Reconnaissance Mission[/bold blue]\n"
        f"Investigating: [cyan]{args.package}[/cyan]",
        border_style="blue",
        box="round",
        padding=(1, 2)
    )
    
    if not manager.is_installed(args.package):
        ASCIIColors.panel(
            f"Package '[bold]{args.package}[/bold]' is [bold red]NOT installed[/bold red] {EMOJI['cross']}\n\n"
            f"[dim]{EMOJI['info']} Use 'pipmaster equip {args.package}' to install it.[/dim]",
            title=f"[bold red]{EMOJI['error']} Not Found[/bold red]",
            border_style="red",
            box="round"
        )
        return

    version = manager.get_installed_version(args.package)
    info = manager.get_package_info(args.package)
    
    # Parse info into a beautiful table
    if info:
        info_lines = [line.strip() for line in info.strip().split('\n') 
                     if line.strip() and ':' in line]
        info_rows = []
        
        # Priority fields first
        priority_fields = ['Name', 'Version', 'Summary', 'Home-page', 'Author', 
                          'License', 'Location', 'Requires']
        
        for field in priority_fields:
            for line in info_lines:
                if line.startswith(field + ':'):
                    key, val = line.split(':', 1)
                    info_rows.append([
                        f"[bold cyan]{EMOJI['bullet']} {key}:[/bold cyan]", 
                        f"[white]{val.strip()[:60]}[/white]"
                    ])
                    break
        
        # Add remaining fields
        for line in info_lines:
            if ':' in line:
                key, val = line.split(':', 1)
                if key not in priority_fields:
                    info_rows.append([
                        f"[dim]{EMOJI['bullet']} {key}:[/dim]", 
                        f"[dim]{val.strip()[:50]}[/dim]"
                    ])
        
        info_table = ASCIIColors.table(
            f"{EMOJI['mag']} Property", f"{EMOJI['info']} Value",
            rows=info_rows[:12],  # Limit to prevent overflow
            box="round",
            show_lines=False,
            border_style="cyan"
        )
    else:
        info_table = f"[dim]{EMOJI['info']} No detailed intelligence available[/dim]"
    
    # Success panel with full intel
    ASCIIColors.panel(
        info_table,
        title=f"[bold green]{EMOJI['success']} {args.package} v{version}[/bold green]",
        border_style="green",
        box="round",
        padding=(1, 2)
    )

def handle_scan(args):
    """Handle the 'scan' command (Vulnerabilities)."""
    manager = get_target_pm(args.env)
    
    # Security scan header
    ASCIIColors.panel(
        f"[bold yellow]{EMOJI['scan']} SECURITY SCAN[/bold yellow]\n"
        f"{EMOJI['shield']} Scanning for vulnerabilities and security threats...",
        border_style="yellow",
        box="round",
        padding=(1, 2)
    )
    
    # Star spinner for security scan (dramatic effect)
    with ASCIIColors.status(
        f"[bold yellow]{EMOJI['shield']} Analyzing package security...[/bold yellow]",
        spinner="star",
        spinner_style="bold yellow"
    ) as status:
        found, report = manager.check_vulnerabilities()
        if not found:
            status.update(f"[bold green]{EMOJI['check']} Scan complete — all clear![/bold green]")
    
    if found:
        # Parse report into manageable chunks
        report_lines = report.split('\n')[:25]
        
        ASCIIColors.panel(
            f"[bold red]{EMOJI['warning']} VULNERABILITIES DETECTED![/bold red]\n\n"
            f"[dim]{chr(10).join(report_lines)}[/dim]"
            f"\n\n[bold red]{EMOJI['fire']} Immediate action recommended:[/bold red]\n"
            f"  {EMOJI['bullet']} Update affected packages with 'pipmaster equip <package> --upgrade'\n"
            f"  {EMOJI['bullet']} Review the full security advisory\n"
            f"  {EMOJI['bullet']} Consider alternative packages if unmaintained",
            title=f"[bold red]{EMOJI['shield']} Security Alert[/bold red]",
            border_style="bold red",
            box="double",
            padding=(1, 2)
        )
        sys.exit(1)
    else:
        ASCIIColors.panel(
            f"[bold green]{EMOJI['success']} No Vulnerabilities Found[/bold green]\n\n"
            f"{EMOJI['shield']} Your environment is secure and protected.\n"
            f"[dim]{EMOJI['sparkles']} Keep your packages updated for continued safety.[/dim]",
            title=f"[bold green]{EMOJI['shield']} Secure[/bold green]",
            border_style="green",
            box="round",
            padding=(1, 2)
        )

def main():
    parser = argparse.ArgumentParser(
        description="PipMaster CLI: The Ultimate Python Package Warrior",
        prog="pipmaster",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=f"""{EMOJI['sparkles']} Examples:
  {EMOJI['forge']} pipmaster forge -p 3.12 -d ./myenv -k numpy pandas
  {EMOJI['equip']} pipmaster equip requests flask -e ./myenv
  {EMOJI['banish']} pipmaster banish old-package -e ./myenv
  {EMOJI['scout']} pipmaster scout requests
  {EMOJI['scan']} pipmaster scan -e ./myenv"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Choose your action")
    
    # FORGE
    p_forge = subparsers.add_parser(
        "forge", 
        help=f"{EMOJI['forge']} Create a new environment with a specific Python version"
    )
    p_forge.add_argument("-p", "--python", required=True, 
                        help="Target Python version (e.g. 3.10, 3.12)")
    p_forge.add_argument("-d", "--path", required=True, 
                        help="Destination path for the environment")
    p_forge.add_argument("-k", "--packages", nargs="*", 
                        help="Initial packages to install")
    
    # EQUIP
    p_equip = subparsers.add_parser(
        "equip", 
        help=f"{EMOJI['equip']} Install packages into an environment"
    )
    p_equip.add_argument("packages", nargs="+", help="Packages to install")
    p_equip.add_argument("-e", "--env", default=".", 
                        help="Path to environment (default: current)")
    p_equip.add_argument("--dry-run", action="store_true", 
                        help="Simulate execution")
    
    # BANISH
    p_banish = subparsers.add_parser(
        "banish", 
        help=f"{EMOJI['banish']} Uninstall packages from an environment"
    )
    p_banish.add_argument("packages", nargs="+", help="Packages to uninstall")
    p_banish.add_argument("-e", "--env", default=".", 
                         help="Path to environment (default: current)")
    
    # SCOUT
    p_scout = subparsers.add_parser(
        "scout", 
        help=f"{EMOJI['scout']} Get info about an installed package"
    )
    p_scout.add_argument("package", help="Package name")
    p_scout.add_argument("-e", "--env", default=".", 
                        help="Path to environment (default: current)")
    
    # SCAN
    p_scan = subparsers.add_parser(
        "scan", 
        help=f"{EMOJI['scan']} Scan for security vulnerabilities"
    )
    p_scan.add_argument("-e", "--env", default=".", 
                       help="Path to environment (default: current)")

    args = parser.parse_args()
    
    # Print beautiful header
    print_header()
    
    if not args.command:
        # Interactive command showcase
        commands_showcase = (
            f"[bold]Available Commands:[/bold]\n\n"
            f"  {EMOJI['forge']} [cyan]forge[/cyan]   — Create new Python environment\n"
            f"  {EMOJI['equip']} [green]equip[/green]   — Install packages\n"
            f"  {EMOJI['banish']} [red]banish[/red]  — Uninstall packages\n"
            f"  {EMOJI['scout']} [blue]scout[/blue]   — Package information\n"
            f"  {EMOJI['scan']} [yellow]scan[/yellow]    — Security vulnerability scan\n\n"
            f"[dim]Use --help with any command for more details.[/dim]"
        )
        
        ASCIIColors.panel(
            commands_showcase,
            title=f"[bold]{EMOJI['info']} Commands[/bold]",
            border_style="cyan",
            box="round",
            padding=(1, 2)
        )
        parser.print_help()
        return

    # Route to handler with error handling
    try:
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
    except KeyboardInterrupt:
        ASCIIColors.panel(
            f"[bold yellow]{EMOJI['warning']} Interrupted by user[/bold yellow]\n"
            f"[dim]Operation cancelled. No changes were made.[/dim]",
            border_style="yellow",
            box="round"
        )
        sys.exit(130)
    except Exception as e:
        ASCIIColors.panel(
            f"[bold red]{EMOJI['error']} Unexpected Error[/bold red]\n\n"
            f"[red]{e}[/red]\n\n"
            f"[dim]{EMOJI['info']} Please report this issue with the error details.[/dim]",
            title=f"[bold red]{EMOJI['cross']} Fatal Error[/bold red]",
            border_style="bold red",
            box="double"
        )
        sys.exit(1)

if __name__ == "__main__":
    main()
