# Quick Start Guide

Get started with ICON - Desktop Icon Grid Replacer in 5 minutes!

## Step 1: Get Your API Key

1. Go to [SteamGridDB](https://www.steamgriddb.com/)
2. Create a free account or log in
3. Navigate to [API Preferences](https://www.steamgriddb.com/profile/preferences/api)
4. Generate a new API key
5. Copy the API key (you'll need it in a moment)

## Step 2: Install Dependencies

Open a terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

This installs:
- `requests` - For API communication
- `Pillow` - For image processing
- `pywin32` - For Windows COM operations

## Step 3: Run Setup Wizard

```bash
python icon_replacer.py --setup
```

Enter your API key when prompted, choose your preferences, and you're done!

## Step 4: Replace Your Icons!

### Interactive Mode (Recommended for First Use)

```bash
python icon_replacer.py
```

This will:
1. Scan your desktop
2. Show you each found icon
3. Ask for confirmation before replacing

### Auto Mode (Quick & Easy)

```bash
python icon_replacer.py --auto
```

This will automatically replace all icons without asking.

## Example Session

```
$ python icon_replacer.py

██╗ ██████╗ ██████╗ ███╗   ██╗
██║██╔════╝██╔═══██╗████╗  ██║
██║██║     ██║   ██║██╔██╗ ██║
██║██║     ██║   ██║██║╚██╗██║
██║╚██████╗╚██████╔╝██║ ╚████║
╚═╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
   Desktop Icon Grid Replacer v1.0
         By Wesley Ellis

✓ Connected to SteamGridDB

🔍 Scanning desktop...
✓ Found 15 items on desktop

🎨 Fetching and replacing icons...

[1/15] Steam
  ✓ Found: https://cdn2.steamgriddb.com/icon/xxx.png
    Score: 98, Votes: 234
  Apply this icon? (y/n/skip all) [y]: y
  ✅ Icon updated!

[2/15] Discord
  ✓ Found: https://cdn2.steamgriddb.com/icon/yyy.png
    Score: 95, Votes: 189
  Apply this icon? (y/n/skip all) [y]: y
  ✅ Icon updated!

...

✅ Processing complete!
  Successful: 12
  Failed: 1
  Skipped: 2

💾 Backup created at: C:\Users\YourName\.icon_replacer\backups\backup_20231201_143022.json
```

## Tips for Best Results

1. **Rename Shortcuts** - For better matches, rename your shortcuts to match the exact game/app name
   - ❌ "Steam - Shortcut (2)"
   - ✅ "Steam"

2. **Games Work Best** - SteamGridDB is primarily for games, so game icons will have the most options

3. **Check the Preview** - The tool shows you the icon URL and score before applying

4. **Use Backups** - Backups are automatic, but you can disable with `--no-backup` if you're confident

5. **Refresh Desktop** - After replacing icons, hit F5 to refresh your desktop view

## Common Commands Cheat Sheet

```bash
# First time setup
python icon_replacer.py --setup

# Interactive mode (asks before each icon)
python icon_replacer.py

# List desktop items (no changes)
python icon_replacer.py --list

# Auto mode (no confirmation)
python icon_replacer.py --auto

# Use 512x512 icons instead of 1024x1024
python icon_replacer.py --size 512

# Custom desktop path
python icon_replacer.py --desktop-path "D:\MyDesktop"

# Verbose logging
python icon_replacer.py -v

# One-liner with all options
python icon_replacer.py --api-key YOUR_KEY --size 1024 --auto
```

## Troubleshooting

### Icons don't show up after replacement
- Press F5 to refresh desktop
- Restart Windows Explorer (Ctrl+Shift+Esc → Restart Explorer)

### "No icon found" errors
- The app might not be in SteamGridDB
- Try renaming the shortcut to match the exact app/game name
- SteamGridDB is primarily for games, so non-game apps might not have artwork

### Permission errors
- Run as administrator: Right-click → "Run as administrator"
- Check that shortcuts aren't read-only

## What's Next?

- Check out the [full README](README.md) for more details
- Browse [SteamGridDB](https://www.steamgriddb.com/) to see what artwork is available
- Customize your config file at `~/.icon_replacer/config.json`

## Need Help?

- Open an issue on GitHub
- Check the logs at `~/.icon_replacer/icon_replacer.log`
- Read the [README](README.md) for detailed documentation

---

Happy icon replacing! 🎨
