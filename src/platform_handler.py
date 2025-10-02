"""
Platform-specific handlers for Windows and Linux
Provides abstraction layer for desktop shortcut operations
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Optional
import configparser

logger = logging.getLogger('ICON.Platform')


class PlatformHandler:
    """Base class for platform-specific operations"""

    @staticmethod
    def get_handler():
        """Get the appropriate handler for the current platform"""
        if sys.platform == 'win32':
            return WindowsHandler()
        elif sys.platform.startswith('linux'):
            return LinuxHandler()
        else:
            raise NotImplementedError(f"Platform {sys.platform} is not supported")


class WindowsHandler:
    """Windows-specific desktop operations using COM"""

    def __init__(self):
        try:
            import win32com.client
            import pythoncom
            self.win32com = win32com
            self.pythoncom = pythoncom
        except ImportError:
            logger.error("pywin32 not installed. Required for Windows support.")
            raise

    def get_shortcut_info(self, shortcut_path: Path, item: Dict):
        """Extract information from a Windows .lnk shortcut"""
        try:
            # Initialize COM
            self.pythoncom.CoInitialize()

            try:
                # Create shell object
                shell = self.win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(str(shortcut_path))

                # Get target and icon information
                item['target'] = shortcut.Targetpath
                item['icon_path'] = shortcut.IconLocation.split(',')[0] if shortcut.IconLocation else None

                # Get icon index if specified
                if shortcut.IconLocation and ',' in shortcut.IconLocation:
                    try:
                        item['icon_index'] = int(shortcut.IconLocation.split(',')[1])
                    except ValueError:
                        item['icon_index'] = 0

                logger.debug(f"Shortcut target: {item['target']}")
                logger.debug(f"Shortcut icon: {item['icon_path']} (index: {item['icon_index']})")

            finally:
                # Uninitialize COM
                self.pythoncom.CoUninitialize()

        except Exception as e:
            logger.warning(f"Failed to analyze Windows shortcut {shortcut_path}: {e}")

    def update_shortcut_icon(self, shortcut_path: Path, icon_path: Path) -> bool:
        """Update a Windows .lnk shortcut icon with retry on access denied

        Windows shortcuts support ICO, EXE, and DLL files via IconLocation.
        """
        import time

        max_retries = 3
        retry_delay = 0.5  # seconds

        for attempt in range(max_retries):
            try:
                # Initialize COM
                self.pythoncom.CoInitialize()

                try:
                    # Create shell object
                    shell = self.win32com.client.Dispatch("WScript.Shell")
                    shortcut = shell.CreateShortCut(str(shortcut_path))

                    # Update icon location (ICO file)
                    shortcut.IconLocation = f"{icon_path},0"

                    # Save changes
                    shortcut.Save()

                    logger.info(f"Updated Windows shortcut icon: {shortcut_path}")
                    return True

                finally:
                    # Uninitialize COM
                    self.pythoncom.CoUninitialize()

            except Exception as e:
                # Check if it's an access denied error (error code -2147024891)
                error_str = str(e)
                is_access_denied = '-2147024891' in error_str or 'Unable to save shortcut' in error_str

                if is_access_denied and attempt < max_retries - 1:
                    logger.warning(f"Access denied on attempt {attempt + 1}/{max_retries}, retrying after {retry_delay}s delay...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    logger.error(f"Error updating Windows shortcut icon after {attempt + 1} attempts: {e}")
                    if is_access_denied:
                        logger.error(f"File may be locked by Windows Explorer or pinned to taskbar/start menu: {shortcut_path}")
                    return False

        return False


class LinuxHandler:
    """Linux-specific desktop operations using .desktop files"""

    def get_shortcut_info(self, shortcut_path: Path, item: Dict):
        """Extract information from a Linux .desktop file"""
        try:
            config = configparser.ConfigParser()
            config.read(shortcut_path, encoding='utf-8')

            if config.has_section('Desktop Entry'):
                # Get target executable
                if config.has_option('Desktop Entry', 'Exec'):
                    exec_cmd = config.get('Desktop Entry', 'Exec')
                    # Remove arguments and field codes
                    exec_cmd = exec_cmd.split()[0] if exec_cmd else None
                    item['target'] = exec_cmd

                # Get icon path
                if config.has_option('Desktop Entry', 'Icon'):
                    item['icon_path'] = config.get('Desktop Entry', 'Icon')

                logger.debug(f"Desktop entry target: {item['target']}")
                logger.debug(f"Desktop entry icon: {item['icon_path']}")

        except Exception as e:
            logger.warning(f"Failed to analyze Linux .desktop file {shortcut_path}: {e}")

    def update_shortcut_icon(self, shortcut_path: Path, icon_path: Path) -> bool:
        """Update a Linux .desktop file icon

        Linux desktop environments prefer PNG format for icons.
        """
        try:
            config = configparser.ConfigParser()
            config.read(shortcut_path, encoding='utf-8')

            # Ensure Desktop Entry section exists
            if not config.has_section('Desktop Entry'):
                logger.error(f"Invalid .desktop file: {shortcut_path}")
                return False

            # Linux uses PNG files - convert ICO to PNG if needed
            png_path = icon_path.with_suffix('.png')

            if icon_path.suffix == '.ico' and not png_path.exists():
                try:
                    from PIL import Image
                    with Image.open(icon_path) as img:
                        # Save the largest size from ICO
                        img.save(png_path, 'PNG')
                    logger.info(f"Converted {icon_path} to {png_path}")
                except Exception as e:
                    logger.error(f"Failed to convert icon: {e}")
                    return False

            # Use the PNG path for Linux
            final_icon_path = png_path if png_path.exists() else icon_path

            config.set('Desktop Entry', 'Icon', str(final_icon_path))

            # Write back to file
            with open(shortcut_path, 'w', encoding='utf-8') as f:
                config.write(f, space_around_delimiters=False)

            logger.info(f"Updated Linux .desktop icon: {shortcut_path}")
            return True

        except Exception as e:
            logger.error(f"Error updating Linux .desktop icon: {e}")
            return False
