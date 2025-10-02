# Changelog

All notable changes to ICON - Desktop Icon Grid Replacer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-10-01

### Added
- **Linux Support** 🐧
  - Full cross-platform compatibility for Linux desktop environments
  - Support for `.desktop` files on Linux
  - Platform abstraction layer (`platform_handler.py`)
  - Automatic ICO to PNG conversion for Linux icons

- **Comprehensive Test Suite** ✅
  - Full pytest test suite with >80% code coverage
  - Unit tests for all major components
  - Async test support with pytest-asyncio
  - Test fixtures and mocks for API calls
  - pytest.ini configuration for consistent testing

- **CI/CD Pipeline** 🚀
  - GitHub Actions workflow for automated testing
  - Multi-platform testing (Windows, Linux)
  - Python 3.8-3.12 compatibility testing
  - Code quality checks (black, isort, flake8)
  - Security scanning (bandit, safety)
  - Coverage reporting with Codecov integration

- **Backup Restore Feature** 💾
  - New `--restore` CLI option to restore icons from backup
  - Restore from specific backup file or use `--restore latest`
  - Automatic backup listing and selection

- **Modern Package Installation** 📦
  - `setup.py` for traditional installation
  - `pyproject.toml` for modern Python packaging
  - Proper entry points for console scripts
  - Platform-specific dependencies (pywin32 only on Windows)

### Changed
- **Fully Async API Implementation** ⚡
  - Migrated from `requests` to `aiohttp` for all HTTP operations
  - Proper async context managers for resource management
  - Concurrent downloads for improved performance
  - Better connection pooling and timeout handling

- **Improved Logging** 📝
  - Log files now stored in `~/.icon_replacer/` instead of CWD
  - Consistent log directory creation
  - Better structured logging throughout

- **Enhanced Error Handling** 🛡️
  - Removed all bare `except` clauses
  - Specific exception types for better error messages
  - Improved error recovery and user feedback
  - Better handling of network timeouts and API errors

### Fixed
- Async/sync mixing issues in API calls
- Better handling of special characters in file names
- Improved game name matching algorithm
- Cache key updates for better cache invalidation

### Technical Improvements
- Type hints and mypy compatibility
- Code formatting with black and isort
- Linting with flake8
- Security scanning with bandit
- Better code organization and modularity
- Comprehensive documentation in all modules

### Dependencies
- Replaced `requests` with `aiohttp` (>=3.9.0)
- Added development dependencies for testing and quality assurance
- Made `pywin32` Windows-only with platform markers

## [1.0.0] - 2024-12-01

### Added
- Initial release
- Windows desktop icon replacement
- SteamGridDB API integration
- Automatic backup system
- Interactive and auto modes
- UAC shield and shortcut arrow removal
- Setup wizard
- Comprehensive README and documentation

---

## Upgrade Notes

### Upgrading from 1.x to 2.x

**Breaking Changes:**
- Python 3.8+ is now required (was 3.6+)
- The API is now fully async - if you were importing modules programmatically, you'll need to use async/await

**New Features:**
- Linux support - works on both Windows and Linux now!
- Much faster due to async implementation
- Can restore from backups with `--restore` flag
- Better error messages and logging

**Migration Steps:**
1. Update Python to 3.8+ if needed
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Test with `--list` first to ensure everything works
4. Enjoy improved performance and new features!

## Contributors

- Wesley Ellis ([@wesellis](https://github.com/wesellis)) - Creator and maintainer

## License

MIT License - see [LICENSE](LICENSE) file for details.
