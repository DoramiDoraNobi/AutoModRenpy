# AutoModRenpy - Quick Reference Guide

## 🎮 What is AutoModRenpy?

AutoModRenpy automatically installs mods into Android-ported Renpy games. It handles all the complex tasks:
- Extracts APK files
- Finds game folder (supports various Android port formats)
- Detects and resolves conflicts between mods
- Intelligently merges script files
- Repackages and signs APK
- Creates backups automatically

---

## 🚀 Getting Started (3 Steps)

### Step 1: Install
```bash
# Install Python dependencies
pip install -r requirements.txt

# Download APKTool (see SETUP.md)
# Place in tools/ folder
```

### Step 2: Launch
**Windows:** Double-click `AutoModRenpy.bat`  
**Command Line:** `python main.py`

### Step 3: Use
1. Select your game's APK
2. Add mod folders (drag to reorder priority)
3. Click "Install Mods to APK"
4. Wait for completion
5. Install the new APK (uninstall original first!)

---

## 📋 Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    1. SELECT APK                            │
│  Browse and select your Android Renpy game APK file        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 2. DETECT GAME LOCATION                     │
│  Automatically finds 'game/' folder in APK                  │
│  • Searches: assets/game/, assets/x-game/, etc.           │
│  • Caches result for next time                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    3. ADD MODS                              │
│  Select mod folders (can add multiple)                     │
│  • Auto-detects if mod has 'game/' subfolder              │
│  • Drag to reorder priority (bottom = highest)            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              4. CONFLICT DETECTION                          │
│  Scans all mods and detects file conflicts                 │
│  • Shows which files are modified by multiple mods        │
│  • Highlights script files that need merging              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           5. CHOOSE RESOLUTION STRATEGY                     │
│  🟢 Load as New File (Recommended)                         │
│     Creates z01_filename.rpy alongside original            │
│  🟡 Replace                                                 │
│     Overwrites original file with mod version              │
│  🔴 Skip                                                    │
│     Don't install this conflicting file                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              6. SCRIPT VALIDATION                           │
│  Checks .rpy files for basic syntax errors                 │
│  • Indentation check (4 spaces)                           │
│  • Block structure validation                             │
│  • Warnings don't block installation                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 7. INSTALL MODS                             │
│  Copies all mod files to game folder                       │
│  • Respects priority order (z01_, z02_, z03_)            │
│  • Applies conflict strategies                            │
│  • Validates successful installation                      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│             8. SIGNATURE BYPASS                             │
│  Prepares APK for installation over original               │
│  • Removes META-INF/ folder                               │
│  • Adds android:debuggable="true"                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           9. REPACKAGE & SIGN APK                           │
│  Creates final modded APK                                  │
│  • Rebuilds APK with apktool                              │
│  • Signs with debug keystore (or custom)                  │
│  • Optimizes with zipalign                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    ✅ COMPLETE!                             │
│  Your modded APK is ready                                  │
│  • Backup of original saved automatically                 │
│  • Uninstall original game before installing              │
│  • Transfer to Android device and install                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Load Order Example

**How Renpy loads files alphabetically:**

```
Original Game Files:        Mod Files Added:              Load Order:
├── script.rpy             ├── z01_mod1_script.rpy       1. script.rpy (original)
├── scenes.rpy             ├── z02_mod2_script.rpy       2. scenes.rpy (original)
├── images/                ├── z01_new_content.rpy       3. z01_mod1_script.rpy
└── audio/                 └── images/                    4. z01_new_content.rpy
                                                          5. z02_mod2_script.rpy

Result: Mods load AFTER original, can override functions
```

**Multiple Mods Example:**
```
Priority 1: Translation Mod    → z01_*.rpy
Priority 2: UI Improvements    → z02_*.rpy
Priority 3: Custom Content     → z03_*.rpy

Higher numbers load last = highest priority
```

---

## 🔧 Conflict Resolution Guide

### Scenario: Two mods modify `script.rpy`

**Option 1: Load as New File (🟢 Recommended)**
```
game/
├── script.rpy          # Original untouched
├── z01_script.rpy      # Mod 1 changes
└── z02_script.rpy      # Mod 2 changes

✓ All changes preserved
✓ Game loads in order: original → mod1 → mod2
✓ Safest option
```

**Option 2: Replace (🟡 Risky)**
```
game/
└── script.rpy          # Overwritten with Mod 2

⚠️ Only Mod 2 changes applied
⚠️ Mod 1 and original lost
⚠️ Game updates will break
```

**Option 3: Skip (🔴 Incomplete)**
```
game/
└── script.rpy          # Original unchanged

⚠️ Mod changes not applied
⚠️ May cause mod to not work
⚠️ Use only if you know what you're doing
```

---

## 📱 Installing on Android

### Preparation
1. ✅ Modded APK created successfully
2. ✅ Transfer APK to Android device
3. ✅ **Uninstall original game** (very important!)
4. ✅ Enable "Install from Unknown Sources" in Settings

### Installation Steps
1. Open file manager on Android
2. Navigate to modded APK
3. Tap to install
4. Grant permissions if prompted
5. Launch and play!

### Troubleshooting
- **"App not installed"** → Uninstall original game first
- **"Invalid APK"** → APK may be corrupted, check file size
- **"Parse error"** → Re-sign APK or use different signing method
- **Game crashes** → Check logs, may be mod incompatibility

---

## 🛠️ CLI Quick Reference

```bash
# Basic usage
python main.py --apk game.apk --mod mod_folder/ --output modded.apk

# Multiple mods (order matters!)
python main.py --apk game.apk \
  --mod translation/ ui_mod/ content_mod/ \
  --output game_modded.apk

# Skip backup (faster)
python main.py --apk game.apk --mod mod/ --output out.apk --no-backup

# Custom keystore
python main.py --apk game.apk --mod mod/ --output out.apk \
  --keystore my_keystore.jks

# Replace strategy
python main.py --apk game.apk --mod mod/ --output out.apk \
  --strategy replace

# Skip conflicts
python main.py --apk game.apk --mod mod/ --output out.apk \
  --strategy skip
```

---

## 📊 Understanding the GUI

### Main Tab
- **APK Selection**: Choose your game
- **Game Detection**: Auto-finds game folder
- **Mod List**: Your mods in priority order (drag to reorder)
- **Progress Bar**: Shows installation status
- **Log Output**: Detailed progress messages

### UnRPA Tab
- **Browse RPA**: Select .rpa archive from game
- **View Contents**: See all files in archive
- **Extract**: Save files to folder
- Use this to inspect game before modding!

### Settings Tab
- **Keystore**: Default debug or custom
- **Conflict Strategy**: Choose default behavior
- Changes apply to next installation

### Backups Tab
- **View Backups**: All saved original APKs
- **Restore**: Get back to original
- **Cleanup**: Remove old backups

---

## 💡 Pro Tips

### For Best Results
1. **Test mods individually first** - Add one at a time to find issues
2. **Keep backups** - Original APKs are precious!
3. **Check mod compatibility** - Read mod descriptions for conflicts
4. **Use "Load as New File"** - Safest conflict resolution
5. **Validate scripts** - Check warnings before installing

### Performance
- **Use cache** - Game detection is cached, second runs are faster
- **Cleanup backups** - Old backups take disk space
- **Small mods first** - Large texture packs as last priority

### Debugging
- **Check logs** - `logs/automodrenpy.log` has detailed info
- **Test APK** - Try modded APK on emulator first
- **Renpy console** - Press Shift+O in game for console access

---

## ⚠️ Common Mistakes

### ❌ Don't Do This:
- Install modded APK over original (will fail)
- Mix incompatible mods
- Ignore conflict warnings
- Delete backups immediately
- Use debug keystore for distribution

### ✅ Do This Instead:
- Uninstall original first
- Check mod compatibility
- Review conflicts and choose strategy
- Keep backups for 1-2 weeks
- Create custom keystore for sharing

---

## 🎓 Advanced Usage

### Custom Mod Priority
Manually rename mod files:
```
game/
├── z01_init.rpy       # Loads first
├── z50_midgame.rpy    # Loads in middle
└── z99_endgame.rpy    # Loads last
```

### Script Inspection
Use UnRPA to extract game scripts:
1. Go to UnRPA tab
2. Select `archive.rpa` from extracted APK
3. Extract to folder
4. Study script structure before modding

### Batch Processing
Create script for multiple games:
```python
from main import AutoModRenpy

app = AutoModRenpy()

games = [
    ('game1.apk', ['mod1/', 'mod2/'], 'game1_modded.apk'),
    ('game2.apk', ['mod1/'], 'game2_modded.apk'),
]

for apk, mods, output in games:
    app.install_mods(apk, mods, output)
```

---

## 📞 Getting Help

1. **Read SETUP.md** - Detailed installation guide
2. **Check examples.py** - Code examples for all features
3. **Run test_suite.py** - Verify installation
4. **Review logs** - Check `logs/automodrenpy.log`
5. **Test simple mod first** - Verify setup works

---

## ✨ You're Ready!

AutoModRenpy handles all the complexity. Just:
1. Select APK
2. Add mods
3. Click install
4. Transfer to Android
5. Play!

**Happy Modding! 🎮**
