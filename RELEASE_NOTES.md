# ICON v1.0.0 Release Notes

**Release Date:** October 2, 2025

## Overview

ICON v1.0.0 is the first stable production release of the Desktop Icon Grid Replacer. This tool automatically replaces desktop shortcut icons with high-quality 512x512 or 1024x1024 grid artwork from SteamGridDB.

## What's Included

### Core Features
- ✅ **Desktop Scanning** - Automatically finds all shortcuts on Windows (.lnk) and Linux (.desktop)
- ✅ **SteamGridDB Integration** - Downloads high-quality grid artwork
- ✅ **Automatic Backups** - Creates JSON backups before making changes
- ✅ **One-Click Restore** - Restore all icons with `--restore latest`
- ✅ **Cross-Platform** - Works on Windows and Linux
- ✅ **Async Downloads** - Fast concurrent downloads with caching
- ✅ **Overlay Removal** - Remove UAC shields and shortcut arrows (Windows)

### Windows-Specific Features
- Multi-resolution .ico generation (16x16 to 256x256)
- COM-based shortcut manipulation
- UAC shield and shortcut arrow removal/restoration

### Linux-Specific Features
- .desktop file icon replacement
- XDG desktop entry standard compliance
- PNG/SVG icon support
- Automatic desktop refresh

## Installation

### Windows Standalone (Recommended)
1. Download `ICON.exe` from releases
2. Double-click to run (no installation needed)
3. Follow the setup wizard to enter your SteamGridDB API key

### Python (Cross-Platform)
```bash
# Clone repository
git clone https://github.com/wesellis/APP-ICON-Desktop-Icon-Grid-Replacer.git
cd APP-ICON-Desktop-Icon-Grid-Replacer

# Install with pip
pip install -e .

# Run
python icon_replacer.py
```

## Quick Start

### Windows
```cmd
# Run interactively
ICON.exe

# Auto-apply all icons
ICON.exe --auto

# Restore from backup
ICON.exe --restore latest

# Remove UAC shields and shortcut arrows
ICON.exe --remove-overlays
```

### Linux
```bash
# Run interactively
python3 icon_replacer.py

# Auto-apply all icons
python3 icon_replacer.py --auto

# Restore from backup
python3 icon_replacer.py --restore latest

# List desktop items
python3 icon_replacer.py --list
```

## Requirements

### Windows
- Windows 10 or later
- No Python required for standalone .exe

### Linux
- Python 3.8 or higher
- Pillow, aiohttp libraries

### Both Platforms
- Internet connection for SteamGridDB API
- Free SteamGridDB API key (get at https://www.steamgriddb.com/profile/preferences/api)

## Known Limitations

- **Cannot replace .exe embedded icons** - Windows limitation, requires recompiling
- **Limited .url file support** - Internet shortcuts have restricted icon capabilities
- **SteamGridDB API rate limits** - Free tier has rate limits, tool includes retry logic

## Testing

This release includes:
- 80%+ code coverage with pytest
- Cross-platform testing (Windows and Linux)
- Automated CI/CD with GitHub Actions

## Credits

- **Author:** Wesley Ellis (wes@wesellis.com)
- **Artwork:** SteamGridDB community (https://www.steamgriddb.com)
- **License:** MIT

## Support

- **Issues:** https://github.com/wesellis/APP-ICON-Desktop-Icon-Grid-Replacer/issues
- **Documentation:** https://github.com/wesellis/APP-ICON-Desktop-Icon-Grid-Replacer#readme

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

---

**Thank you for using ICON!**

If you find this tool helpful, please consider starring the repository on GitHub.
