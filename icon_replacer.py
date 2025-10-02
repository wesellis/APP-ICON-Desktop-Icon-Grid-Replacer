#!/usr/bin/env python3
"""
ICON - Desktop Icon Grid Replacer
Replace desktop icons with high-quality SteamGridDB artwork

Author: Wesley Ellis
Version: 1.0.0
License: MIT

Automatically scans your desktop for shortcuts and replaces their icons
with beautiful 512x512 or 1024x1024 grid artwork from SteamGridDB.
"""

import sys
import os
import argparse
import asyncio
import logging
from pathlib import Path
from typing import Optional
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configure logging
def setup_logging():
    """Setup logging to ~/.icon_replacer/ directory"""
    log_dir = Path.home() / '.icon_replacer'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'icon_replacer.log'

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger('ICON')

logger = setup_logging()

# ASCII Art Banner
BANNER = """
===============================================
    ICON - Desktop Icon Grid Replacer v1.0
         By Wesley Ellis
===============================================
"""


class IconReplacer:
    """Main Icon Replacer application class"""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize Icon Replacer application"""
        self.config_path = config_path or Path.home() / '.icon_replacer' / 'config.json'
        self.config = self.load_config()
        self.api = None

    def load_config(self) -> dict:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        return {}

    def save_config(self):
        """Save configuration to file"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info("Configuration saved")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    async def run(self, args):
        """Run the Icon Replacer"""
        print(BANNER)

        # Handle restore if requested
        if args.restore:
            self.restore_from_backup(args.restore)
            return

        # Handle overlay removal if requested
        if args.remove_overlays:
            self.remove_overlays()
            return

        # Handle overlay restoration if requested
        if args.restore_overlays:
            self.restore_overlays()
            return

        # Check for API key
        if not args.api_key and not self.config.get('api_key'):
            print("\nError: SteamGridDB API key required!")
            print("Get your API key from: https://www.steamgriddb.com/profile/preferences/api")
            print("\nUsage: icon_replacer --api-key YOUR_KEY")
            print("Or run: icon_replacer --setup")
            print("\nHint: Double-click ICON_Launcher.bat for an interactive menu!")
            input("\nPress Enter to exit...")
            sys.exit(1)

        api_key = args.api_key or self.config['api_key']

        # Import required components
        try:
            from steamgrid_api import SteamGridAPI
            from desktop_scanner import DesktopScanner
            from icon_updater import IconUpdater

            # Use async context manager for API
            async with SteamGridAPI(api_key) as api:
                print("[+] Connected to SteamGridDB")

                # Create scanner and updater
                scanner = DesktopScanner()
                updater = IconUpdater(api, size=args.size)

                # Scan desktop
                print(f"\n[*] Scanning desktop...")
                desktop_items = scanner.scan_desktop(args.desktop_path)
                print(f"[+] Found {len(desktop_items)} items on desktop")

                if not desktop_items:
                    print("No items found on desktop")
                    return

                # Show items found
                if args.list:
                    print("\nDesktop items:")
                    for i, item in enumerate(desktop_items, 1):
                        try:
                            print(f"  {i}. {item['name']} ({item['type']})")
                        except UnicodeEncodeError:
                            # Handle special characters that can't be encoded
                            safe_name = item['name'].encode('ascii', 'replace').decode('ascii')
                            print(f"  {i}. {safe_name} ({item['type']})")
                    return

                # Process items
                print(f"\n[*] Fetching and replacing icons...")
                results = await updater.process_items(
                    desktop_items,
                    auto_apply=args.auto,
                    backup=args.backup
                )

                # Show results
                print(f"\n[+] Processing complete!")
                print(f"  Successful: {results['success']}")
                print(f"  Failed: {results['failed']}")
                print(f"  Skipped: {results['skipped']}")

                if results['backup_path']:
                    print(f"\n[*] Backup created at: {results['backup_path']}")

        except ImportError as e:
            logger.error(f"Dependencies not installed: {e}")
            print(f"\nError: Missing dependencies!")
            print("Install with: pip install -r requirements.txt")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"\nError: {e}")
            sys.exit(1)

    def remove_overlays(self):
        """Remove UAC shields and shortcut overlays"""
        print("\n[*] Overlay Removal Tool")
        print("=" * 50)
        print("\nThis will remove:")
        print("  - UAC shield overlays on administrator shortcuts")
        print("  - Shortcut arrow overlays on all shortcuts")
        print("\n[!] WARNING: This modifies Windows registry settings!")
        print("    You can restore them later with --restore-overlays\n")

        response = input("Do you want to proceed? (yes/no): ").strip().lower()

        if response != 'yes':
            print("  Cancelled.")
            return

        try:
            from overlay_remover import OverlayRemover
            remover = OverlayRemover()

            print("\n[*] Removing overlays...")
            if remover.remove_overlays():
                print("\n[+] Overlay removal complete!")
            else:
                print("\n[-] Overlay removal failed. Check the log for details.")

        except ImportError as e:
            logger.error(f"Failed to import overlay_remover: {e}")
            print("\n[-] Error: overlay_remover module not found!")
        except Exception as e:
            logger.error(f"Error removing overlays: {e}")
            print(f"\n[-] Error: {e}")

    def restore_overlays(self):
        """Restore UAC shields and shortcut overlays to default"""
        print("\n[*] Restoring default overlays...")

        try:
            from overlay_remover import OverlayRemover
            remover = OverlayRemover()

            if remover.restore_overlays():
                print("\n[+] Overlays restored!")
            else:
                print("\n[-] Restore failed. Check the log for details.")

        except ImportError as e:
            logger.error(f"Failed to import overlay_remover: {e}")
            print("\n[-] Error: overlay_remover module not found!")
        except Exception as e:
            logger.error(f"Error restoring overlays: {e}")
            print(f"\n[-] Error: {e}")

    def restore_from_backup(self, backup_path_arg: str):
        """Restore icons from a backup file"""
        try:
            from icon_updater import IconUpdater

            backup_dir = Path.home() / '.icon_replacer' / 'backups'

            # If backup_path_arg is "latest", find the most recent backup
            if backup_path_arg.lower() == 'latest':
                if not backup_dir.exists():
                    print("\n[-] No backups found!")
                    return

                backups = sorted(backup_dir.glob('backup_*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
                if not backups:
                    print("\n[-] No backups found!")
                    return

                backup_path = backups[0]
                print(f"\n[*] Using latest backup: {backup_path.name}")
            else:
                # Use the provided path
                backup_path = Path(backup_path_arg)
                if not backup_path.exists():
                    # Try looking in the backup directory
                    backup_path = backup_dir / backup_path_arg
                    if not backup_path.exists():
                        print(f"\n[-] Backup file not found: {backup_path_arg}")
                        return

            print(f"\n[*] Restoring from backup: {backup_path}")

            # Create a temporary updater instance (no API needed for restore)
            updater = IconUpdater(None)
            success = updater.restore_from_backup(backup_path)

            if success:
                print("\n[+] Icons restored successfully!")
                print("[*] Refreshing icon cache...")
                updater._refresh_icon_cache()
            else:
                print("\n[-] Restore failed. Check the log for details.")

        except ImportError as e:
            logger.error(f"Failed to import icon_updater: {e}")
            print("\n[-] Error: icon_updater module not found!")
        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")
            print(f"\n[-] Error: {e}")

    def setup_wizard(self):
        """Interactive setup wizard"""
        print(BANNER)
        print("Welcome to ICON Setup Wizard!\n")

        # Get API key
        print("You'll need an API key from SteamGridDB:")
        print("https://www.steamgriddb.com/profile/preferences/api\n")

        api_key = input("Enter SteamGridDB API key: ").strip()

        # Get preferences
        size = input("Preferred icon size (512 or 1024) [1024]: ").strip() or "1024"
        auto_backup = input("Automatically backup icons? (y/n) [y]: ").strip().lower() or "y"

        # Ask about overlay removal
        print("\n" + "=" * 50)
        print("Optional: Remove UAC shields and shortcut arrows")
        print("=" * 50)
        print("This will remove the overlay icons from:")
        print("  • UAC shield overlays (administrator shortcuts)")
        print("  • Shortcut arrow overlays (all shortcuts)")
        print("\nNote: This modifies registry and requires admin privileges.")
        print("You can restore them anytime with: icon_replacer --restore-overlays")

        remove_overlays = input("\nRemove overlays now? (yes/no) [no]: ").strip().lower()

        # Save configuration
        self.config = {
            'api_key': api_key,
            'icon_size': int(size),
            'auto_backup': auto_backup == 'y',
            'icons_dir': str(Path.home() / '.icon_replacer' / 'icons')
        }
        self.save_config()

        print("\n[+] Setup complete! Configuration saved.")

        # Handle overlay removal if requested
        if remove_overlays == 'yes':
            print("\n")
            self.remove_overlays()

        print("\n" + "=" * 50)
        print("You can now run:")
        print("  icon_replacer                    - Scan and replace desktop icons")
        print("  icon_replacer --list             - List desktop items")
        print("  icon_replacer --auto             - Auto-apply without confirmation")
        print("  icon_replacer --remove-overlays  - Remove UAC/shortcut overlays")
        print("  icon_replacer --restore-overlays - Restore default overlays")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='ICON - Desktop Icon Grid Replacer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  icon_replacer                        Scan and replace desktop icons
  icon_replacer --list                 List desktop items only
  icon_replacer --auto                 Auto-apply without confirmation
  icon_replacer --setup                Run setup wizard
  icon_replacer --remove-overlays      Remove UAC/shortcut overlays
  icon_replacer --restore-overlays     Restore default overlays

  icon_replacer --api-key YOUR_KEY --size 1024

For more information: https://github.com/wesellis/icon-replacer
        """
    )

    # Mode
    parser.add_argument('--setup', action='store_true', help='Run setup wizard')
    parser.add_argument('--list', action='store_true', help='List desktop items only')
    parser.add_argument('--restore', metavar='BACKUP', help='Restore icons from backup file')
    parser.add_argument('--remove-overlays', action='store_true',
                       help='Remove UAC shields and shortcut arrows')
    parser.add_argument('--restore-overlays', action='store_true',
                       help='Restore default UAC/shortcut overlays')

    # Authentication
    parser.add_argument('--api-key', help='SteamGridDB API key')

    # Options
    parser.add_argument('--size', type=int, choices=[512, 1024], default=1024,
                       help='Icon size (512 or 1024, default: 1024)')
    parser.add_argument('--desktop-path',
                       default=str(Path.home() / 'Desktop'),
                       help='Desktop path (default: ~/Desktop)')
    parser.add_argument('--auto', action='store_true',
                       help='Auto-apply without confirmation')
    parser.add_argument('--no-backup', dest='backup', action='store_false',
                       help='Skip backup creation')
    parser.add_argument('--force', action='store_true',
                       help='Force re-download even if icon exists')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create app instance
    app = IconReplacer()

    # Handle modes
    if args.setup:
        app.setup_wizard()
    else:
        asyncio.run(app.run(args))


if __name__ == '__main__':
    main()
