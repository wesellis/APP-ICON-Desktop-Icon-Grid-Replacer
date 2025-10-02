# ICON - Desktop Icon Grid Replacer

A tool to replace desktop icons with 1:1 grid artwork from SteamGridDB.

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Linux-lightgrey?style=flat-square)](README.md)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen?style=flat-square)](README.md)
[![Coverage](https://img.shields.io/badge/Coverage-80%25+-brightgreen?style=flat-square)](README.md)
[![Stars](https://img.shields.io/github/stars/wesellis/APP-ICON-Desktop-Icon-Grid-Replacer?style=flat-square)](https://github.com/wesellis/APP-ICON-Desktop-Icon-Grid-Replacer/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/wesellis/APP-ICON-Desktop-Icon-Grid-Replacer?style=flat-square)](https://github.com/wesellis/APP-ICON-Desktop-Icon-Grid-Replacer/commits)

ICON scans your Windows or Linux desktop for shortcuts, searches for matching artwork on SteamGridDB, and replaces the icons with 512x512 or 1024x1024 square grid images.

## What's New in v2.0

- **Linux Support** - Cross-platform compatibility for both Windows and Linux
- **Async Architecture** - Concurrent downloads using aiohttp
- **Test Coverage** - 80%+ code coverage with pytest
- **Backup/Restore** - Restore icons from any backup with `--restore`
- **Modern Packaging** - pip installation with setup.py and pyproject.toml
- **CI/CD** - Automated testing with GitHub Actions
- **Error Handling** - Informative error messages and recovery

## Features

- **Automatic Desktop Scanning** - Finds all shortcuts on your desktop (Windows & Linux)
- **High-Quality Icons** - Downloads 512x512 or 1024x1024 square grid artwork
- **Smart Matching** - Cleans up names for better search results
- **Backup & Restore** - Automatically backs up original icons and restore anytime
- **Async Downloads** - Concurrent downloads with caching and connection pooling
- **Selective Application** - Choose which icons to replace (or auto-apply all)
- **Overlay Removal** - Optional removal of UAC shields and shortcut arrows (Windows)
- **Cross-Platform** - Works on both Windows (.lnk) and Linux (.desktop)

## Installation

### Windows Standalone (Easiest - No Python Required)

1. **Download** `ICON.exe` from [Releases](https://github.com/wesellis/APP-ICON-Desktop-Icon-Grid-Replacer/releases)
2. **Run** the executable (no installation needed)
3. **Get API Key** from https://www.steamgriddb.com/profile/preferences/api
4. **Follow** the setup wizard

The standalone .exe includes all dependencies and works on Windows 10+.

### Python Installation (Cross-Platform)

**Prerequisites:**
- Python 3.8 or higher
- Windows or Linux operating system
- SteamGridDB API key (free at https://www.steamgriddb.com/profile/preferences/api)

**Quick Install (Recommended):**

```bash
# Clone the repository
git clone https://github.com/wesellis/APP-ICON-Desktop-Icon-Grid-Replacer.git
cd APP-ICON-Desktop-Icon-Grid-Replacer

# Install with pip (includes all dependencies)
pip install -e .

# Or install for development (includes test tools)
pip install -e ".[dev]"
```

### Manual Install (Python)

1. Clone or download this repository:
```bash
git clone https://github.com/wesellis/icon-replacer.git
cd icon-replacer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the setup wizard:
```bash
python icon_replacer.py --setup
```

## Usage

### Quick Start

```bash
# Run with interactive mode (choose which icons to replace)
python icon_replacer.py

# Auto-apply all icons without confirmation
python icon_replacer.py --auto

# Just list what's on your desktop
python icon_replacer.py --list
```

### Command-Line Options

```bash
python icon_replacer.py [OPTIONS]

Options:
  --setup                Run interactive setup wizard
  --list                 List desktop items without making changes
  --restore BACKUP       Restore icons from backup (use 'latest' for most recent)
  --remove-overlays      Remove UAC shields and shortcut arrows (Windows only)
  --restore-overlays     Restore default UAC/shortcut overlays (Windows only)
  --api-key KEY          SteamGridDB API key
  --size SIZE            Icon size: 512 or 1024 (default: 1024)
  --desktop-path PATH    Custom desktop path (default: ~/Desktop)
  --auto                 Auto-apply without confirmation
  --no-backup            Skip backup creation
  --verbose, -v          Verbose output
```

### Examples

```bash
# Use specific API key and icon size
python icon_replacer.py --api-key YOUR_KEY --size 512

# Custom desktop path
python icon_replacer.py --desktop-path "C:\Users\YourName\Desktop"

# Auto mode with no backup (use with caution!)
python icon_replacer.py --auto --no-backup

# Restore from latest backup
python icon_replacer.py --restore latest

# Restore from specific backup
python icon_replacer.py --restore backup_20231201_143022.json

# Remove UAC shields and shortcut arrows (Windows)
python icon_replacer.py --remove-overlays

# Restore default overlays (Windows)
python icon_replacer.py --restore-overlays
```

### Overlay Removal Feature

ICON includes a feature to remove the UAC shield and shortcut arrow overlays from your desktop icons:

**What it removes:**
- UAC shield overlays (on administrator shortcuts)
- Shortcut arrow overlays (on all shortcuts)

**How to use:**
```bash
# During setup wizard
python icon_replacer.py --setup
# Answer "yes" when prompted about overlay removal

# Or run separately
python icon_replacer.py --remove-overlays
```

**Important notes:**
- Requires administrator privileges to modify registry
- Places a `blank.ico` file in your Documents folder
- **Do NOT delete blank.ico** or overlays will reappear
- Can be restored anytime with `--restore-overlays`

**How it works:**
- Copies a blank icon file to Documents folder
- Modifies Windows registry to use blank icon for overlays
- Restarts Windows Explorer to apply changes
```

## How It Works

1. **Scans Desktop** - Finds all `.lnk` shortcuts, `.exe` files, and `.url` links
2. **Cleans Names** - Removes "- Shortcut", numbers, and other junk from names
3. **Searches SteamGridDB** - Looks for matching games/apps with square grid artwork
4. **Downloads Icons** - Gets the highest-rated 1:1 grid artwork
5. **Converts Format** - Converts to Windows `.ico` format with multiple resolutions
6. **Updates Shortcuts** - Changes the icon path in the Windows shortcut

## Configuration

After running `--setup`, your configuration is saved to:
```
~/.icon_replacer/config.json
```

Configuration includes:
- SteamGridDB API key
- Preferred icon size (512 or 1024)
- Auto-backup preference
- Icons directory path

## File Locations

```
~/.icon_replacer/
├── config.json           # Your configuration
├── icons/                # Downloaded and converted icons
├── backups/              # Backup files (JSON)
└── icon_replacer.log     # Application log
```

## Backup & Restore

ICON automatically creates backups before making changes. Backups are stored as JSON files with timestamps:

```
~/.icon_replacer/backups/backup_20231201_143022.json
```

To restore from a backup, you can manually edit the shortcuts or use the backup file to reference original icon paths.

## Supported File Types

### Windows
- ✅ `.lnk` - Windows shortcuts (fully supported)
- ⚠️ `.exe` - Executables (read-only, cannot change embedded icons)
- ⚠️ `.url` - Internet shortcuts (limited support)

### Linux
- ✅ `.desktop` - Desktop entry files (fully supported)

**Note**: Only shortcut files (`.lnk` on Windows, `.desktop` on Linux) can have their icons replaced. Executables have embedded icons that cannot be changed without recompiling.

## Troubleshooting

### "No icon found on SteamGridDB"
- The app name might not match anything in the database
- Try renaming the shortcut to match the game/app name exactly
- Not all apps are in SteamGridDB (it's primarily for games)

### "Failed to update icon"
- Ensure you have write permissions to the desktop
- The shortcut file might be in use or locked
- Try running as administrator

### Icons not appearing after update
- Refresh your desktop (F5)
- Restart Windows Explorer (Ctrl+Shift+Esc → File → Restart Explorer)
- Windows icon cache might need clearing

### Clear Windows Icon Cache
```cmd
ie4uinit.exe -show
ie4uinit.exe -ClearIconCache
```

## API Rate Limits

SteamGridDB has rate limits on their API. ICON uses:
- **Caching** - Reduces duplicate API calls
- **Connection pooling** - Reuses connections efficiently
- **Retry logic** - Handles temporary failures gracefully

If you hit rate limits, wait a few minutes before trying again.

## Project Structure

```
APP-ICON-Desktop-Icon-Grid-Replacer/
├── icon_replacer.py          # Main application
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── src/
│   ├── steamgrid_api.py     # SteamGridDB API integration
│   ├── desktop_scanner.py    # Desktop scanning logic
│   └── icon_updater.py       # Icon download and update logic
├── assets/                   # Screenshots and media
├── config/                   # Configuration templates
└── docs/                     # Additional documentation
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_steamgrid_api.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 src/

# Type check with mypy
mypy src/

# Security scan with bandit
bandit -r src/
```

## Contributing

Contributions welcome! Please feel free to submit issues or pull requests.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Standards

- Follow PEP 8 style guidelines
- Use black for code formatting
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting PR

## Related Projects

- [VAPOR](https://github.com/wesellis/VAPOR) - Steam Grid Artwork Manager (the inspiration for this tool)

## License

MIT License - see LICENSE file for details

## Credits

- **Author**: Wesley Ellis (wes@wesellis.com)
- **SteamGridDB**: https://www.steamgriddb.com/
- **Icons**: All artwork belongs to their respective creators on SteamGridDB

## Disclaimer

This tool modifies Windows shortcuts on your desktop. While it creates backups automatically, use at your own risk. Always ensure you have backups of important data.

---

## Project Status & Roadmap

**Completion: 100%** - Production Ready

### What Works

**Core Features:**
- ✅ Desktop scanning (Windows .lnk and Linux .desktop files)
- ✅ SteamGridDB API integration with caching
- ✅ Async icon downloads with aiohttp
- ✅ Icon conversion to .ico format (multiple resolutions)
- ✅ Shortcut icon replacement
- ✅ **Automatic backup creation**
- ✅ **One-click restore** (`--restore latest` or specify backup file)
- ✅ Cross-platform support (Windows and Linux)
- ✅ UAC shield and shortcut arrow overlay removal (Windows)
- ✅ Test suite with pytest (80%+ coverage)
- ✅ CI/CD with GitHub Actions
- ✅ Proper packaging (setup.py, pyproject.toml)
- ✅ Command-line interface with multiple options
- ✅ Configuration management
- ✅ Error handling and logging
- ✅ Modular architecture (well-organized source files)

### Platform-Specific Features

**Windows:**
- ✅ .lnk shortcut icon replacement
- ✅ UAC shield overlay removal/restoration
- ✅ Shortcut arrow removal/restoration
- ✅ Multi-resolution .ico generation (16x16 to 256x256)
- ✅ COM-based shortcut manipulation

**Linux:**
- ✅ .desktop file icon replacement
- ✅ XDG desktop entry standard compliance
- ✅ PNG/SVG icon support
- ✅ Automatic desktop refresh

### Known Limitations

**Platform Limitations (Not Fixable):**
- ⚠️ **.exe Icon Replacement**: Cannot replace embedded icons in executables (requires recompiling)
- ⚠️ **.url File Support**: Limited icon support for internet shortcuts

**Optional Enhancements (Nice-to-Have):**
- GUI interface (currently command-line only)
- Icon preview before applying
- Custom icon upload support
- Folder icon replacement

### Linux Usage Examples

**Basic usage on Linux:**
```bash
# Run ICON on Linux
python3 icon_replacer.py

# Auto-apply all icons
python3 icon_replacer.py --auto

# Restore from latest backup
python3 icon_replacer.py --restore latest

# List desktop items
python3 icon_replacer.py --list
```

**Linux .desktop file locations:**
- User desktop: `~/Desktop/`
- System applications: `/usr/share/applications/`
- User applications: `~/.local/share/applications/`

### Current Status

This project is **production-ready and feature-complete**. All core functionality works reliably:
- Automatic icon replacement with SteamGridDB artwork
- Cross-platform support (Windows and Linux)
- Full backup and restore functionality
- Comprehensive error handling and logging
- Well-tested codebase (80%+ coverage)

The tool does exactly what it claims with no critical missing features. Optional enhancements like GUI and preview are nice-to-have but not essential for core functionality.

---

**Created by Wesley Ellis**

Found a bug? Have a feature request? Open an issue on GitHub!
