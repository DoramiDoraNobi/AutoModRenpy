# AutoModRenpy - Android Ren'Py Mod Installer

A powerful tool to install mods into Android Ren'Py games by modifying and repackaging APK files. Supports multiple mods, conflict resolution, script validation, and RPA archive extraction.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

## Features

✨ **Core Features:**
- 📦 Extract and repackage APK files with ZIP fallback
- 🎮 Auto-detect Ren'Py game folders in APK
- 🔧 Install multiple mods with conflict resolution
- 📝 Validate Python/Ren'Py scripts before installation
- 💾 Automatic backup of original APK
- 🔐 Sign APK with debug keystore
- 📚 Extract RPA archives before mod installation
- ⚙️ CLI and GUI interfaces

✅ **Conflict Resolution:**
- **Overwrite**: Replace original files with mod files
- **New File**: Add mod files with prefix (z_filename.rpy)
- **Skip**: Skip conflicting files

🔒 **Safety:**
- Pre-installation backup of original APK
- Script validation with detailed error reports
- Conflict detection and reporting
- Reversible modifications

## Installation

### Requirements

- **Python 3.10+**
- **Java 11+** (for keytool - optional, will be auto-detected)
- **Android SDK** (optional, for apktool - defaults to ZIP extraction)

### Setup

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd AutoModRenpy
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Optional: Setup Android SDK**
   - Download Android SDK (API 34+)
   - Extract to `tools/` folder
   - Required files: `apksigner.bat`, `zipalign.exe`

## Usage

### GUI Mode (Recommended)

```bash
python gui.py
```

**Steps:**
1. **Select APK** → Click "Browse APK" to choose game APK
2. **Detect Game** → Auto-detect game folder location (optional)
3. **Add Mods** → Drag mod folders to list, reorder as needed
4. **Configure RPA** → Check "Extract RPA archives..." if mods depend on extracted files
5. **Install** → Click "Install Mods to APK" and choose output location

### CLI Mode

```bash
python main.py --apk path/to/game.apk --mods mod1/ mod2/ mod3/ --output modded.apk
```

**Options:**
```
--apk PATH              Path to original APK file (required)
--mods MOD_PATH...      Paths to mod folders (required, multiple)
--output PATH           Output APK path (default: game_modded.apk)
--keystore PATH         Custom keystore path
--strategy STRATEGY     Conflict strategy: overwrite|new_file|skip (default: overwrite)
--extract-rpa          Extract RPA archives before installation (default: true)
--no-backup            Skip backup creation
```

**Example:**
```bash
python main.py --apk AboveTheClouds-v0.8.apk --mods mods/outfit_pack/ mods/extra_scenes/ --output AboveTheClouds-modded.apk
```

### UnRPA Tab (Standalone)

Extract RPA archives separately:
1. Go to "UnRPA Extractor" tab
2. Select RPA file
3. Choose output folder
4. Extract

## Configuration

Edit `config.json` to customize behavior:

```json
{
  "apktool_path": "tools/apktool.bat",
  "apksigner_path": "tools/apksigner.bat",
  "zipalign_path": "tools/zipalign.exe",
  "conflict_strategy": "overwrite",
  "extract_rpa_before_mod": true,
  "mod_prefix": "z",
  "default_keystore": "tools/debug.keystore",
  "keystore_password": "android",
  "validation": {
    "check_indentation": true,
    "warn_on_errors": true,
    "block_on_errors": false
  }
}
```

### Key Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `conflict_strategy` | How to handle file conflicts | `overwrite` |
| `extract_rpa_before_mod` | Auto-extract RPA before mod installation | `true` |
| `mod_prefix` | Prefix for new mod files (if strategy=new_file) | `z` |
| `check_indentation` | Validate script indentation | `true` |
| `block_on_errors` | Block installation if script errors found | `false` |

## Installation to Android Phone

1. **Prepare APK**
   - Use AutoModRenpy to create modded APK
   - Output will be in `mods/` folder

2. **Transfer to Phone**
   - Connect phone via USB or use cloud storage
   - Transfer `*_modded.apk` file to phone

3. **Install APK**
   - Open file manager on phone
   - Locate APK file
   - Tap to install
   - If prompted: "Settings" → "Unknown sources" → Enable

4. **Run Game**
   - Mods should be active
   - Check game logs if mods not loading

## Mod Installation Guide

### How to Create Mods

Mods should follow Ren'Py game structure:

```
my_mod/
├── game/
│   ├── script.rpy          (modified game script)
│   ├── screens.rpyc        (modified screens)
│   ├── images/
│   │   └── character.png
│   └── audio/
│       └── bgm_custom.ogg
└── mod_info.txt            (optional metadata)
```

### Installation Methods

**Method 1: GUI (Easiest)**
- Drag mod folder to GUI
- Click Install

**Method 2: CLI**
```bash
python main.py --apk game.apk --mods ./my_mod --output game_modded.apk
```

**Method 3: UnRPA → Manual**
1. Extract RPA archives using UnRPA tab
2. Copy mod files to extracted game folder
3. Repackage manually

## Troubleshooting

### APK Extraction Hangs

**Problem:** Apktool extraction takes very long (>5 min)

**Solution:**
- App uses ZIP extraction fallback automatically
- Can disable apktool to force faster ZIP method
- Check disk space (needs 2x APK size temporarily)

### Mods Not Loading in Game

**Problem:** Installed mods not visible in-game

**Causes:**
- RPA archives not extracted (enable "Extract RPA archives")
- File conflicts not resolved correctly
- Game loading from RPA instead of loose files
- Script errors preventing load

**Solution:**
1. Check log for errors
2. Verify mod folder structure matches game
3. Try overwriting original files instead of new_file strategy
4. Extract RPA before installation

### Keystore Not Found

**Problem:** `keytool not found` error

**Solution:**
- Install Java JDK 11+
- App auto-detects in common locations
- Or set `JAVA_HOME` environment variable

### Script Validation Errors

**Problem:** Script validation fails

**Solution:**
- Check indentation (4 spaces vs tabs)
- Validate script files manually
- Set `"block_on_errors": false` to skip validation

## Project Structure

```
AutoModRenpy/
├── gui.py                    # GUI interface (Tkinter)
├── main.py                   # Main CLI interface
├── config.json              # Configuration file
├── requirements.txt         # Python dependencies
│
├── src/
│   ├── apk_handler.py      # APK extraction/repackaging
│   ├── game_detector.py    # Detect game folder in APK
│   ├── mod_processor.py    # Process and install mods
│   ├── unrpa_extractor.py  # Extract RPA archives
│   ├── script_validator.py # Validate Python/Ren'Py scripts
│   ├── backup_manager.py   # Manage APK backups
│   └── utils.py            # Utility functions
│
├── tools/                   # External tools
│   ├── apktool.bat
│   ├── apksigner.bat
│   ├── zipalign.exe
│   └── debug.keystore
│
├── backups/                 # APK backups
├── mods/                    # Output modded APKs
└── logs/                    # Application logs
```

## How It Works

### Installation Pipeline

```
1. Backup original APK
   ↓
2. Extract APK (apktool or ZIP)
   ↓
3. Detect game folder (assets/game, assets/x-game, etc)
   ↓
4. Extract RPA archives (if enabled)
   ↓
5. Prepare mods (detect conflicts)
   ↓
6. Validate scripts
   ↓
7. Install mods (copy/overwrite files)
   ↓
8. Modify AndroidManifest (signature bypass)
   ↓
9. Repackage APK (ZIP)
   ↓
10. Sign APK (debug keystore)
   ↓
11. Output modded APK
```

### Conflict Resolution

| Strategy | Behavior | Use Case |
|----------|----------|----------|
| `overwrite` | Replace original files | Most mods |
| `new_file` | Add with z_ prefix | Multiple incompatible versions |
| `skip` | Keep original file | Preserve game files |

## API Usage

```python
from main import AutoModRenpy
from src.utils import Config, Logger

# Initialize
config = Config('config.json')
logger = Logger()
app = AutoModRenpy(config_path='config.json', logger=logger)

# Install mods
success = app.install_mods(
    apk_path='game.apk',
    mod_folders=['mod1/', 'mod2/'],
    output_apk='game_modded.apk',
    extract_rpa=True,
    conflict_strategy='overwrite'
)

if success:
    print("Installation complete!")
else:
    print("Installation failed")
```

## Development

### Adding New Features

1. **New APK Handler Method**: Edit `src/apk_handler.py`
2. **New Mod Processor Logic**: Edit `src/mod_processor.py`
3. **New Validation**: Edit `src/script_validator.py`
4. **GUI Changes**: Edit `gui.py`

### Running Tests

```bash
python test_suite.py
```

## Known Limitations

- ⚠️ **Apktool**: Can hang on large APKs; app falls back to ZIP
- ⚠️ **XML Editing**: ZIP extraction doesn't decode binary XML (no manifest modification)
- ⚠️ **RPA Versions**: Supports RPA-2.0, RPA-3.0, RPA-4.0
- ⚠️ **Multiple Conflicts**: Complex multi-mod conflicts not auto-resolved
- ⚠️ **Rollback**: No automatic rollback; restore from backups manually

## Requirements

```
tkinter-tooltip>=1.8.0
pillow>=10.0.0
lxml>=4.9.0
unrpa>=2.0.2
tqdm>=4.65.0
colorama>=0.4.6
pathlib>=1.0.1
```

## License

MIT License - See [LICENSE](LICENSE) file

## Contributing

Contributions welcome! Please:
1. Fork repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## Support

- 🐛 Report issues on GitHub
- 💬 Discuss in Discussions tab
- 📖 Check QUICK_GUIDE.md for quick start

## Credits

- **Ren'Py**: Game engine https://www.renpy.org/
- **unrpa**: RPA extraction https://github.com/Lattyware/unrpa
- **apktool**: APK decompiling https://ibotpeaches.github.io/Apktool/

## Changelog

### v1.0.0 (Initial Release)
- Full APK mod installation workflow
- GUI and CLI interfaces
- RPA extraction support
- Script validation
- Backup management
- Conflict resolution
- ZIP/Apktool extraction methods

---

**Made with ❤️ for the Ren'Py modding community**
5. **Repackage**: Rebuilds APK with modified content
6. **Sign**: Strips old signature and resigns with debug keystore

## Script Conflict Resolution

When multiple mods modify the same `.rpy` file:
- **Load as New File** (Recommended): Creates `z_filename.rpy` loaded after original
- **Replace**: Overwrites original file (use with caution)
- **Skip**: Excludes conflicting file

## Important Notes

- ⚠️ You must **uninstall the original game** before installing modded version
- ⚠️ Modded APKs use debug signature and won't update from Play Store
- ⚠️ Keep backups of original APKs
- ⚠️ Script validation is basic - Renpy will show runtime errors if syntax is wrong

## License

MIT License - See LICENSE file

## Credits

- UnRPA library for RPA extraction
- Apktool for APK decompilation
- Renpy community for modding knowledge
