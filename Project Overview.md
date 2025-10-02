# Project Overview: ICON - Desktop Icon Grid Replacer

## Purpose
Automatically replace Windows desktop icons with high-quality 512x512 or 1024x1024 square grid artwork from SteamGridDB.com

## Inspiration
Based on the VAPOR (Visual Artwork Processing & Organization Resource) Steam Grid Artwork Manager, this tool brings the same beautiful artwork to your Windows desktop icons.

## Key Features

### Core Functionality
1. **Desktop Scanning** - Automatically finds all shortcuts and executables on desktop
2. **Intelligent Name Matching** - Cleans up shortcut names for better search results
3. **SteamGridDB Integration** - Searches for high-quality square grid artwork
4. **Automatic Icon Replacement** - Downloads, converts, and applies new icons
5. **Backup System** - Creates automatic backups before making changes

### Technical Features
- **Caching** - Reduces API calls by caching search results and artwork lists
- **Connection Pooling** - Efficient HTTP connection reuse
- **Async Operations** - Fast concurrent downloads
- **Error Handling** - Robust retry logic and error recovery
- **Image Processing** - Converts artwork to proper Windows .ico format with multiple resolutions

## Architecture

### Main Components

1. **icon_replacer.py** - Main application entry point
   - CLI argument parsing
   - Setup wizard
   - Application orchestration

2. **steamgrid_api.py** - SteamGridDB API integration
   - Game search by name
   - Icon/grid artwork retrieval
   - Download handling
   - Caching layer

3. **desktop_scanner.py** - Desktop scanning logic
   - Finds .lnk, .exe, .url files
   - Extracts shortcut information
   - Cleans names for better matching

4. **icon_updater.py** - Icon processing and replacement
   - Downloads artwork
   - Converts to .ico format
   - Updates Windows shortcuts
   - Manages backups

### Data Flow

```
Desktop → Scanner → API Search → Download → Convert → Update → Backup
```

1. Scanner finds all desktop shortcuts
2. For each shortcut:
   - Clean the name
   - Search SteamGridDB by name
   - Find highest-rated square grid
   - Download artwork
   - Convert to .ico format
   - Update shortcut icon path
3. Create backup of original settings

## File Structure

```
APP-ICON-Desktop-Icon-Grid-Replacer/
├── icon_replacer.py          # Main application
├── requirements.txt          # Dependencies
├── README.md                 # Full documentation
├── QUICKSTART.md            # Quick start guide
├── LICENSE                   # MIT License
├── .gitignore               # Git ignore rules
├── Project Overview.md       # This file
├── src/
│   ├── steamgrid_api.py     # SteamGridDB API client
│   ├── desktop_scanner.py    # Desktop item scanner
│   └── icon_updater.py       # Icon processor/updater
├── assets/                   # Screenshots (future)
├── config/                   # Config templates (future)
└── docs/                     # Additional docs (future)
```

## User Data Storage

```
~/.icon_replacer/
├── config.json              # User configuration
├── icons/                   # Downloaded and converted icons
│   ├── GameName.ico
│   └── ...
├── backups/                 # Backup files
│   ├── backup_20231201_143022.json
│   └── ...
└── icon_replacer.log        # Application log
```

## Dependencies

- **requests** - HTTP client for API calls
- **Pillow (PIL)** - Image processing and .ico conversion
- **pywin32** - Windows COM objects for shortcut manipulation

## API Integration

### SteamGridDB API Endpoints Used

1. `GET /search/autocomplete/{term}` - Search for games by name
2. `GET /icons/game/{id}` - Get icon artwork for a game
3. `GET /grids/game/{id}` - Get grid artwork for a game (preferred for square icons)

### API Features
- Bearer token authentication
- Dimension filtering (512x512, 1024x1024)
- Score/vote sorting for best results
- Rate limiting with retry logic

## Workflow

### Setup Flow
1. User runs `--setup`
2. Prompts for SteamGridDB API key
3. Prompts for preferences (size, backup)
4. Saves config to `~/.icon_replacer/config.json`

### Icon Replacement Flow
1. Load configuration
2. Initialize SteamGridDB API client
3. Scan desktop for shortcuts
4. For each shortcut:
   - Clean the name (remove "- Shortcut", numbers, etc.)
   - Search SteamGridDB for matching game
   - Get highest-rated square grid artwork
   - Download artwork
   - Convert to multi-resolution .ico file
   - Update shortcut icon path (COM automation)
5. Create backup of original settings
6. Report results to user

### Backup Format
```json
{
  "timestamp": "20231201_143022",
  "items": [
    {
      "path": "C:\\Users\\Name\\Desktop\\Steam.lnk",
      "name": "Steam",
      "icon_path": "C:\\Program Files\\Steam\\Steam.exe",
      "icon_index": 0
    }
  ]
}
```

## Icon Conversion Process

1. Download source image (PNG, JPG, etc.)
2. Ensure square aspect ratio (crop if needed)
3. Resize to target size (512 or 1024)
4. Convert to RGBA mode
5. Save as .ico with multiple resolutions:
   - 256x256
   - 128x128
   - 64x64
   - 48x48
   - 32x32
   - 16x16

This ensures icons look crisp at all sizes in Windows.

## Error Handling

### API Errors
- Rate limiting: Retry with exponential backoff
- Not found (404): Cache negative result, skip item
- Server errors (5xx): Retry up to 3 times
- Network errors: Log and continue to next item

### File Errors
- Permission denied: Suggest running as admin
- File locked: Skip and report
- Invalid shortcut: Skip and log

### Image Errors
- Invalid format: Try alternative download
- Conversion failure: Skip and report
- Dimension mismatch: Auto-crop to square

## Performance Optimizations

1. **Caching**
   - Game search results cached by name
   - Artwork lists cached by (game_id, type, dimensions)
   - Prevents duplicate API calls

2. **Connection Pooling**
   - Reuses HTTP connections
   - Pool size: 20 connections, max 50
   - Reduces connection overhead

3. **Async Downloads**
   - Concurrent image downloads
   - Non-blocking I/O operations

## Future Enhancements

### Potential Features
- [ ] GUI application (Tkinter/Qt)
- [ ] Custom icon upload
- [ ] Multiple desktop support
- [ ] Schedule automatic icon updates
- [ ] Icon preview before applying
- [ ] Bulk restore from backup
- [ ] Support for other icon databases
- [ ] Folder icon replacement
- [ ] System icon replacement

### Technical Improvements
- [ ] Full async/await implementation
- [ ] Better progress indicators
- [ ] Parallel processing of multiple items
- [ ] Web-based preview interface
- [ ] SQLite database for icon cache
- [ ] Automatic icon cache cleanup

## Testing Checklist

- [ ] Install dependencies on fresh Python environment
- [ ] Run setup wizard with valid API key
- [ ] Scan desktop with various shortcut types
- [ ] Replace icons in interactive mode
- [ ] Replace icons in auto mode
- [ ] Verify backup creation
- [ ] Test with 512x512 and 1024x1024 sizes
- [ ] Test with custom desktop path
- [ ] Verify error handling (invalid API key, network errors)
- [ ] Check icon quality at different Windows zoom levels

## Known Limitations

1. **Windows Only** - Uses Windows COM objects (win32com)
2. **Shortcuts Only** - Can't modify .exe embedded icons
3. **SteamGridDB Focus** - Limited to games/apps in their database
4. **Rate Limits** - API has rate limits (handled with caching)
5. **Icon Cache** - Windows may cache old icons, requiring refresh

## Credits

- **Author**: Wesley Ellis (wes@wesellis.com)
- **Inspired by**: VAPOR Steam Grid Artwork Manager
- **Artwork Source**: SteamGridDB.com and its amazing community
- **Dependencies**: requests, Pillow, pywin32

## License

MIT License - Free to use, modify, and distribute

---

**Version**: 1.0.0
**Created**: December 2024
**Status**: Complete and functional
