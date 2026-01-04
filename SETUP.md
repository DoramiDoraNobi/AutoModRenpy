# AutoModRenpy - Setup Guide

## Quick Start

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download External Tools

#### Option A: Automatic (Recommended for Windows)
Download the tools package and extract to the `tools/` directory.

#### Option B: Manual Download

**APKTool:**
1. Download from: https://ibotpeaches.github.io/Apktool/
2. Download both `apktool.jar` and `apktool.bat` (Windows) or wrapper script
3. Place in `tools/` folder

**Java JDK (Required for APKTool and signing):**
1. Download JDK 8 or newer from: https://adoptium.net/
2. Install and ensure `java` is in your PATH
3. Verify: `java -version`

**Android Build Tools (Optional - for apksigner):**
1. Download Android SDK Command-line Tools
2. Install build-tools: `sdkmanager "build-tools;30.0.3"`
3. Or use the bundled jarsigner (comes with Java JDK)

### 3. Create Default Debug Keystore

The app will automatically create a debug keystore on first use, or create manually:

```bash
keytool -genkeypair -v -keystore tools/debug.keystore -alias androiddebugkey -keyalg RSA -keysize 2048 -validity 10000 -storepass android -keypass android -dname "CN=AutoModRenpy, OU=Development, O=AutoModRenpy, L=Unknown, S=Unknown, C=US"
```

### 4. Verify Setup

Test that everything works:

```bash
# Test Python installation
python main.py --help

# Test Java
java -version

# Test keytool
keytool -help
```

## Usage

### GUI Mode (Easiest)

```bash
python main.py
```

or simply double-click `main.py`

### CLI Mode

**Basic usage:**
```bash
python main.py --apk game.apk --mod mod_folder/ --output modded_game.apk
```

**Multiple mods (priority order):**
```bash
python main.py --apk game.apk --mod mod1/ mod2/ mod3/ --output modded.apk
```

**Custom keystore:**
```bash
python main.py --apk game.apk --mod mod/ --output modded.apk --keystore custom.jks
```

**Skip backup:**
```bash
python main.py --apk game.apk --mod mod/ --output modded.apk --no-backup
```

**Conflict strategy:**
```bash
python main.py --apk game.apk --mod mod/ --output modded.apk --strategy replace
```

## Directory Structure

```
AutoModRenpy/
├── main.py              # Main CLI entry point
├── gui.py               # GUI application
├── config.json          # Configuration
├── requirements.txt     # Python dependencies
├── README.md            # Documentation
├── SETUP.md            # This file
├── LICENSE             # MIT License
├── src/                # Source modules
│   ├── __init__.py
│   ├── utils.py        # Utilities
│   ├── game_detector.py    # Game location finder
│   ├── unrpa_extractor.py  # RPA extraction
│   ├── apk_handler.py      # APK operations
│   ├── mod_processor.py    # Mod processing
│   ├── script_validator.py # Script validation
│   └── backup_manager.py   # Backup system
├── tools/              # External tools (create this)
│   ├── apktool.bat
│   ├── apktool.jar
│   ├── apksigner.bat (optional)
│   └── debug.keystore (auto-created)
├── temp/               # Temporary files (auto-created)
├── backups/            # APK backups (auto-created)
├── cache/              # Cache files (auto-created)
└── logs/               # Log files (auto-created)
```

## Troubleshooting

### "apktool not found"
- Download apktool from the link above
- Place `apktool.jar` and `apktool.bat` in `tools/` folder
- Ensure Java is installed: `java -version`

### "Signing failed"
- Ensure Java JDK is installed (not just JRE)
- Verify keytool works: `keytool -help`
- Debug keystore will be auto-created on first run

### "Game folder not found"
- Some APKs use non-standard folder structures
- Try manually checking the APK with UnRPA tab first
- Check logs for detection details

### "Validation warnings"
- Script validation is lightweight and may show false positives
- Warnings won't block installation
- Renpy will show detailed errors when running the game

### "APK won't install"
- Uninstall the original game first (signature mismatch)
- Enable "Install from Unknown Sources" in Android settings
- Check APK file size (shouldn't be 0 bytes)

## Advanced Configuration

Edit `config.json` to customize:

```json
{
  "mod_prefix": "z",              // Prefix for new files (z01_, z02_)
  "conflict_strategy": "new_file", // Default: new_file, replace, skip
  "indent_size": 4,               // Python/Renpy indentation
  "max_cache_entries": 100        // Game location cache size
}
```

## Security Notes

⚠️ **Important:**
- Debug keystore is for testing only
- Modded APKs won't receive official updates
- Always keep backups of original APKs
- Some games may detect modifications

## Getting Help

If you encounter issues:
1. Check the logs in `logs/automodrenpy.log`
2. Enable verbose logging
3. Test with a simple mod first
4. Verify tools are installed correctly

## Credits

- **UnRPA**: Based on Renpy archive extraction techniques
- **Apktool**: APK decompilation/recompilation
- **Renpy Community**: Modding knowledge and tools
