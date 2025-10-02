"""
Icon Cache Manager
Handles clearing and refreshing icon caches on Windows and Linux
"""

import sys
import logging
import subprocess
import time

logger = logging.getLogger('ICON.Cache')


class IconCacheManager:
    """Manage icon cache operations for the current platform"""

    def __init__(self):
        """Initialize cache manager for current platform"""
        if sys.platform == 'win32':
            self.backend = WindowsIconCache()
        elif sys.platform.startswith('linux'):
            self.backend = LinuxIconCache()
        else:
            logger.warning(f"Icon cache management not implemented for {sys.platform}")
            self.backend = NullIconCache()

    def clear_cache_only(self):
        """Clear icon cache without restarting desktop environment"""
        self.backend.clear_cache_only()

    def refresh_cache_and_restart(self):
        """Clear icon cache and restart desktop environment"""
        self.backend.refresh_cache_and_restart()


class WindowsIconCache:
    """Windows icon cache operations"""

    def clear_cache_only(self):
        """Clear Windows icon cache without restarting Explorer"""
        try:
            print("  [*] Clearing Windows icon cache...")

            # Clear icon cache
            subprocess.run(['ie4uinit.exe', '-show'], capture_output=True)
            subprocess.run(['ie4uinit.exe', '-ClearIconCache'], capture_output=True)
            time.sleep(1)

            print("  [+] Icon cache cleared")

        except Exception as e:
            logger.error(f"Error clearing icon cache: {e}")
            print(f"  [!] Could not clear cache: {e}")

    def refresh_cache_and_restart(self):
        """Clear Windows icon cache and restart Explorer"""
        try:
            # Clear icon cache
            print("  [*] Clearing Windows icon cache...")
            subprocess.run(['ie4uinit.exe', '-show'], capture_output=True)
            subprocess.run(['ie4uinit.exe', '-ClearIconCache'], capture_output=True)
            time.sleep(1)

            # Restart Explorer
            print("  [*] Restarting Windows Explorer...")
            subprocess.run(
                ['powershell', '-Command', 'Stop-Process -Name explorer -Force'],
                capture_output=True,
                timeout=5
            )

            time.sleep(2)

            subprocess.run(
                ['powershell', '-Command', 'Start-Process explorer'],
                capture_output=True,
                timeout=5
            )

            print("  [+] Icon cache cleared and Explorer restarted!")
            print("  [*] Your desktop icons should now show the new artwork!")

        except Exception as e:
            logger.error(f"Error refreshing icon cache: {e}")
            print(f"  [!] Could not auto-refresh. Please:")
            print(f"      1. Press F5 on your desktop")
            print(f"      2. Or restart Windows Explorer manually")


class LinuxIconCache:
    """Linux icon cache operations"""

    def clear_cache_only(self):
        """Clear Linux icon cache without restarting desktop"""
        try:
            print("  [*] Clearing icon cache...")

            # Try GTK icon cache
            try:
                subprocess.run(
                    ['gtk-update-icon-cache', '-f', '-t', '~/.icons'],
                    capture_output=True,
                    timeout=5
                )
            except (FileNotFoundError, subprocess.SubprocessError):
                pass

            # Try clearing XDG cache
            try:
                from pathlib import Path
                import shutil

                cache_dirs = [
                    Path.home() / '.cache' / 'icon-theme.cache',
                    Path.home() / '.cache' / 'thumbnails'
                ]

                for cache_dir in cache_dirs:
                    if cache_dir.exists():
                        if cache_dir.is_file():
                            cache_dir.unlink()
                        elif cache_dir.is_dir():
                            shutil.rmtree(cache_dir, ignore_errors=True)

            except Exception as e:
                logger.debug(f"Could not clear XDG cache: {e}")

            print("  [+] Icon cache cleared")
            print("  [*] You may need to log out and back in to see changes")

        except Exception as e:
            logger.error(f"Error clearing icon cache: {e}")
            print(f"  [!] Could not clear cache: {e}")

    def refresh_cache_and_restart(self):
        """Clear Linux icon cache and suggest desktop restart"""
        self.clear_cache_only()

        print("\n  [*] To see changes immediately, you may need to:")
        print("      1. Press F5 on your desktop, or")
        print("      2. Restart your desktop environment, or")
        print("      3. Log out and back in")


class NullIconCache:
    """No-op cache manager for unsupported platforms"""

    def clear_cache_only(self):
        """No-op"""
        print("  [!] Icon cache clearing not supported on this platform")

    def refresh_cache_and_restart(self):
        """No-op"""
        print("  [!] Icon cache refresh not supported on this platform")
