# AutoModRenpy Tools Directory

This directory should contain external tools required by AutoModRenpy.

## Required Files

### APKTool (Required)
Download from: https://ibotpeaches.github.io/Apktool/

Place these files here:
- `apktool.jar`
- `apktool.bat` (Windows) or `apktool.sh` (Linux/Mac)

### Debug Keystore (Auto-created)
- `debug.keystore` - Will be automatically created on first use

### Optional Tools

**APKSigner** (Android SDK Build Tools):
- `apksigner.bat` or `apksigner` command
- Falls back to `jarsigner` if not available

**Zipalign** (Android SDK Build Tools):
- `zipalign.exe` or `zipalign` command
- Optional optimization tool

## Installation Instructions

See SETUP.md in the root directory for detailed installation instructions.

## Verifying Tools

After placing tools here, verify they work:

```bash
# Test APKTool
java -jar apktool.jar --version

# Test signing tools (from Java JDK)
jarsigner -help
keytool -help
```
