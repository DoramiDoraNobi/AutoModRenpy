# AutoModRenpy - Android Ren'Py Mod Installer & Porter

A powerful tool to install mods into Android Ren'Py games and port PC Ren'Py games to Android.

![Version](https://img.shields.io/badge/version-1.1.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows-blue)

## Features

✨ **Core Features:**
- 📦 Extract and repackage APK files with ZIP fallback
- 🎮 Auto-detect Ren'Py game folders in APK
- 🔧 Install multiple mods with conflict resolution
- 📱 **PC to Android Porting** (New!)
- 🖼️ **Image Optimization** (Resize to 720p, WebP)
- ⌨️ **Android Hotkeys** (Overlay buttons)
- 📝 Validate Python/Ren'Py scripts before installation
- 💾 Automatic backup of original APK
- 🔐 Sign APK with debug keystore
- 📚 Extract RPA archives
- ⚙️ CLI and GUI interfaces

## Installation

### Requirements

- **Python 3.10+**
- **Java 11+** (for keytool - optional, will be auto-detected)
- **Android SDK** (optional, for apktool - defaults to ZIP extraction)

### Quick Start (Windows)

1. Download the latest release (`AutoModRenpy_Windows.zip`).
2. Extract the zip file.
3. Run `AutoModRenpy.exe`.

### Developer Setup

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd AutoModRenpy
   ```
2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run GUI**
   ```bash
   python gui.py
   ```

## PC to Android Porting (New!)

Turn any PC Ren'Py game into an Android APK easily.

1. **Go to "PC to Android" Tab** in the GUI.
2. **Select PC Game Directory**: The folder containing the game (look for the `game/` folder inside it).
3. **Select Base APK**: An empty/template Ren'Py APK (see [Porting Guide](PORTING_GUIDE.md)).
4. **Configure Options**:
   - **Resize to 720p**: Highly recommended to reduce size and improve performance.
   - **Hotkeys**: Adds on-screen Skip/Menu buttons.
5. **Click Build**: The tool will create a signed APK ready to install.

👉 **Read the full [Porting Guide](PORTING_GUIDE.md) for details on Base APKs.**

## Mod Installation Usage

### GUI Mode
1. **Select APK** → Click "Browse APK" to choose game APK
2. **Detect Game** → Auto-detect game folder location
3. **Add Mods** → Drag mod folders to list
4. **Install** → Click "Install Mods to APK"

### CLI Mode

```bash
# Install Mods
python main.py --apk game.apk --mods mod1/ mod2/ --output modded.apk

# Port PC Game
python main.py --port --pc-game "C:/Games/MyGame" --base-apk "base.apk" --output "MyGame.apk" --resize --hotkeys
```

## Configuration

Edit `config.json` to customize behavior:

```json
{
  "apktool_path": "tools/apktool.bat",
  "conflict_strategy": "new_file",
  "mod_prefix": "z",
  "default_keystore": "tools/debug.keystore"
}
```

## Troubleshooting

### Porting Crashes on Launch
- **Cause**: Mismatched Ren'Py versions.
- **Fix**: Ensure your Base APK matches the game's Ren'Py version (Ren'Py 7 vs 8). See [Porting Guide](PORTING_GUIDE.md).

### APK Extraction Hangs
- **Cause**: Large APKs or apktool issues.
- **Fix**: The tool will automatically fallback to ZIP extraction mode.

## License

MIT License - See [LICENSE](LICENSE) file
