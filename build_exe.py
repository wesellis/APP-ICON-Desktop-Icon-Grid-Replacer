#!/usr/bin/env python3
"""
Build script for creating standalone ICON executable
Requires: pip install pyinstaller
"""

import os
import subprocess
import sys
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent

# Build configuration
APP_NAME = "ICON"
VERSION = "1.0.0"
ICON_FILE = PROJECT_ROOT / "assets" / "blank.ico"

def build_exe():
    """Build standalone executable with PyInstaller"""

    print(f"\n{'='*60}")
    print(f"Building {APP_NAME} v{VERSION} Standalone Executable")
    print(f"{'='*60}\n")

    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("Error: PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--onefile",  # Single executable
        "--console",  # Console application
        "--clean",
        f"--icon={ICON_FILE}",
        "--add-data", f"{PROJECT_ROOT / 'src'};src",  # Include src folder
        "--hidden-import", "win32com.client",
        "--hidden-import", "pythoncom",
        "--hidden-import", "aiohttp",
        "--hidden-import", "PIL",
        "--collect-all", "pywin32",
        str(PROJECT_ROOT / "icon_replacer.py")
    ]

    # Run PyInstaller
    print("Running PyInstaller...")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)

    if result.returncode == 0:
        print(f"\n{'='*60}")
        print(f"✓ Build successful!")
        print(f"{'='*60}")
        print(f"\nExecutable location: {PROJECT_ROOT / 'dist' / f'{APP_NAME}.exe'}")
        print(f"Size: {(PROJECT_ROOT / 'dist' / f'{APP_NAME}.exe').stat().st_size / (1024*1024):.1f} MB")
    else:
        print("\n✗ Build failed!")
        sys.exit(1)

if __name__ == "__main__":
    build_exe()
