# AutoModRenpy - Project Summary

## 🎉 Implementation Complete!

AutoModRenpy is a powerful tool for automatically installing mods into Android-ported Renpy games. The complete implementation includes all requested features with smart merging, conflict resolution, and signature bypass capabilities.

---

## 📁 Project Structure

```
AutoModRenpy/
├── 📄 main.py                    # Main CLI application
├── 📄 gui.py                     # GUI application (Tkinter)
├── 📄 config.json                # Configuration file
├── 📄 requirements.txt           # Python dependencies
├── 📄 examples.py                # Usage examples
├── 📄 test_suite.py              # Unit tests
├── 📄 AutoModRenpy.bat          # Windows launcher
├── 📄 README.md                  # Main documentation
├── 📄 SETUP.md                   # Setup instructions
├── 📄 LICENSE                    # MIT License
├── 📄 .gitignore                # Git ignore rules
│
├── 📁 src/                       # Source modules
│   ├── __init__.py              # Package initialization
│   ├── utils.py                 # Utilities (Config, Logger, Cache)
│   ├── game_detector.py         # Flexible game location finder
│   ├── unrpa_extractor.py       # RPA extraction (dual-mode)
│   ├── apk_handler.py           # APK operations & signing
│   ├── mod_processor.py         # Mod processing & conflicts
│   ├── script_validator.py      # Script validation
│   └── backup_manager.py        # Backup management
│
└── 📁 tools/                     # External tools (user adds)
    ├── README.md                # Tool installation guide
    ├── apktool.jar              # (Download required)
    ├── apktool.bat              # (Download required)
    └── debug.keystore           # (Auto-created)
```

---

## ✨ Implemented Features

### Core Features ✓
- ✅ **APK Extraction & Repackaging** - Full APK manipulation using apktool
- ✅ **Flexible Game Detection** - Recursive search for Renpy games in various Android port formats
- ✅ **Smart Mod Structure Detection** - Auto-detects `game/` subfolder with fallback
- ✅ **Dual-Mode UnRPA** - User-facing extraction tool + internal analysis
- ✅ **Multi-Mod Support** - Install multiple mods with priority ordering
- ✅ **Drag-and-Drop Reordering** - GUI for controlling mod load order

### Advanced Features ✓
- ✅ **Script Conflict Detection** - Identifies when mods modify same files
- ✅ **3-Strategy Conflict Resolution**:
  - 🟢 **Load as New File** (Recommended) - Creates `z01_filename.rpy` loaded last
  - 🟡 **Replace** - Overwrites original file
  - 🔴 **Skip** - Excludes conflicting file
- ✅ **Lightweight Script Validation** - Indentation & syntax checks with warnings
- ✅ **Signature Bypass** - META-INF stripping + AndroidManifest debuggable flag
- ✅ **Dual Keystore Support** - Default debug keystore + custom option
- ✅ **Automatic Backup System** - Tracks and restores original APKs
- ✅ **Location Caching** - Remembers game paths for faster re-processing

### User Interface ✓
- ✅ **GUI Mode** - Full-featured Tkinter interface with 4 tabs:
  - Main: APK selection, mod management, installation
  - UnRPA: Archive extraction and browsing
  - Settings: Keystore and conflict strategy configuration
  - Backups: Backup management and restoration
- ✅ **CLI Mode** - Command-line interface for automation
- ✅ **Real-time Logging** - Detailed progress display in GUI and logs
- ✅ **Progress Bar** - Visual feedback during installation

---

## 🚀 Quick Start

### Windows (Easiest)
1. Double-click **`AutoModRenpy.bat`**
2. GUI will launch automatically

### CLI Usage
```bash
# Basic usage
python main.py --apk game.apk --mod mod_folder/ --output modded.apk

# Multiple mods (priority order)
python main.py --apk game.apk --mod mod1/ mod2/ mod3/ --output modded.apk

# Custom keystore
python main.py --apk game.apk --mod mod/ --output modded.apk --keystore custom.jks
```

### GUI Launch
```bash
python main.py
# or
python gui.py
```

---

## 🔧 Setup Requirements

### 1. Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. External Tools
- **Java JDK 8+** - Required for apktool and signing
- **APKTool** - Download from https://ibotpeaches.github.io/Apktool/
- Place in `tools/` folder

### 3. First Run
- Debug keystore will be auto-created
- Directories created automatically: `temp/`, `backups/`, `cache/`, `logs/`

---

## 📊 Technical Architecture

### Workflow Overview
```
1. APK Selection → 2. Extract APK → 3. Detect Game Location (cached)
         ↓
4. Add Mods → 5. Detect Structure → 6. Scan Files → 7. Conflict Detection
         ↓
8. Validate Scripts → 9. User Chooses Strategy → 10. Install Mods
         ↓
11. Signature Bypass → 12. Repackage APK → 13. Sign APK → ✓ Done
```

### Key Components

**GameLocationDetector**
- Recursive search from `assets/` root
- Finds `options.rpyc`, `script.rpyc`, or `screens.rpyc`
- Supports: `assets/game/`, `assets/x-game/`, custom paths
- Caches results by APK hash

**ModProcessor**
- Auto-detects mod structure (`game/` subfolder)
- Scans all files and detects conflicts
- Applies conflict strategies with filename prefixes
- Supports drag-drop priority reordering

**ScriptValidator**
- Checks indentation (multiples of 4 spaces)
- Validates block structure (labels, if/while/for)
- Detects unclosed strings and brackets
- Trust-but-verify philosophy (warnings don't block)

**APKHandler**
- Uses apktool for proper decompilation
- Falls back to ZIP extraction if apktool unavailable
- Strips META-INF for signature bypass
- Signs with apksigner or jarsigner (fallback)
- Auto-creates debug keystore if missing

**UnRPAExtractor**
- Supports RPA-2.0, RPA-3.0, RPA-4.0
- Handles pickle + zlib decompression
- XOR deobfuscation for prefixed files
- Dual mode: user tool + internal analysis

---

## 🎯 Smart Features Explained

### Load Order Control
Mods are loaded alphabetically by Renpy. AutoModRenpy uses prefixes:
- `z01_modA.rpy` - Loads first among mods
- `z02_modB.rpy` - Loads second
- `z03_modC.rpy` - Loads third (highest priority, overrides earlier)

### Conflict Resolution Logic
When 2+ mods modify `script.rpy`:
- **New File Strategy**: Creates `z01_script.rpy` alongside original
- **Replace Strategy**: Overwrites `script.rpy` with mod version
- **Skip Strategy**: Doesn't install conflicting mod file

### Signature Bypass Method
- Removes `META-INF/` folder (old signature)
- Sets `android:debuggable="true"` in AndroidManifest
- Resigns with debug/custom keystore
- **User must uninstall original game before installing**

---

## 📝 Configuration Options

Edit **`config.json`**:

```json
{
  "mod_prefix": "z",              // Prefix for new files
  "conflict_strategy": "new_file", // Default strategy
  "indent_size": 4,               // Script indentation
  "max_cache_entries": 100,       // Game location cache
  "validation": {
    "check_indentation": true,    // Enable indent checks
    "warn_on_errors": true,       // Show warnings
    "block_on_errors": false      // Don't block on errors
  }
}
```

---

## 🧪 Testing

Run the test suite:
```bash
python test_suite.py
```

Tests cover:
- Utility functions (Config, Logger, Cache)
- Script validation
- Mod processing and conflict strategies
- Backup management

---

## 📚 Examples

See **`examples.py`** for detailed usage examples:
- Basic single mod installation
- Multiple mods with priority
- Custom keystore usage
- Backup management
- UnRPA extraction
- Script validation

---

## ⚠️ Important Notes

### For Users
1. **Uninstall original game** before installing modded APK (signature mismatch)
2. **Enable "Unknown Sources"** in Android settings
3. **Keep backups** - modded APKs can't be updated from Play Store
4. **Renpy will show errors** if scripts have runtime issues (not validation issues)

### For Developers
- Script validation is intentionally lightweight (trust Renpy's parser)
- Apktool may fail on some APKs (ZIP fallback available)
- Game detection works for standard Renpy ports (manual path option planned)
- Signature bypass requires uninstall (no root/patching needed)

---

## 🔐 Security Considerations

- Debug keystore is **for testing only** (not production)
- Modded APKs won't receive official updates
- Keep original APKs for restoration
- Some games may detect modifications
- Custom keystores provide better security than debug keystore

---

## 🎨 GUI Features

### Main Tab
- APK selection and game detection
- Mod folder management with drag-drop reordering
- Real-time conflict detection
- Installation progress bar
- Detailed logging output

### UnRPA Tab
- Browse and select RPA archives
- View archive contents (version, file count, sizes)
- Extract entire archive or specific files
- File tree display

### Settings Tab
- Default/custom keystore selection
- Conflict resolution strategy selection
- Visual strategy explanations (🟢🟡🔴)

### Backups Tab
- View all backups with metadata
- Restore from backup
- Delete backups
- Automatic cleanup of old backups

---

## 🚧 Future Enhancements (Optional)

Potential features for future versions:
- [ ] Android smali patching for advanced signature bypass
- [ ] RPA repacking (merge mod files into existing archives)
- [ ] Visual diff viewer for conflicting scripts
- [ ] Mod profiles (save mod configurations)
- [ ] Batch processing (multiple APKs)
- [ ] Web-based interface
- [ ] Auto-update checker

---

## 📄 License

MIT License - See LICENSE file

Free to use, modify, and distribute.

---

## 🙏 Credits

- **UnRPA** - Renpy archive extraction techniques
- **Apktool** - APK decompilation/recompilation
- **Renpy Community** - Modding knowledge and best practices
- **Android Open Source Project** - Signing tools

---

## 💬 Support

For issues or questions:
1. Check **SETUP.md** for installation help
2. Review **examples.py** for usage patterns
3. Check logs in `logs/automodrenpy.log`
4. Run **test_suite.py** to verify installation

---

## ✅ Implementation Status

**All planned features implemented:**
- ✅ Project structure and configuration
- ✅ Flexible game location detector
- ✅ Dual-mode UnRPA extractor
- ✅ APK handler with signing
- ✅ Mod processor with conflict resolution
- ✅ Lightweight script validator
- ✅ Backup management system
- ✅ Full-featured GUI
- ✅ CLI interface
- ✅ Documentation and examples
- ✅ Test suite

**Ready for use!** 🚀
