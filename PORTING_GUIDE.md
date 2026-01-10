# PC to Android Porting Guide

AutoModRenpy allows you to port PC Ren'Py games to Android using the "Base APK Injection" method. This guide explains how it works and how to get the necessary files.

## What is a "Base APK"?

A **Base APK** is essentially an empty Ren'Py game compiled for Android. It acts as a container or "engine" that can run Ren'Py scripts on a mobile device.

- It contains the **Java/Kotlin** code to bridge Android and Python.
- It contains the **Native Libraries** (`librenpy.so`).
- It serves as a template where we inject the PC game's assets.

### Why use a Base APK?
Building an APK from scratch using the official Ren'Py SDK (RAPT) requires installing Java JDK, Android SDK, and configuring complex paths. Using a Base APK allows us to skip all that setup and simply "copy-paste" the game files into a pre-built engine.

## How to Get a Base APK

You have two main options:

### Option 1: Create Your Own (Recommended)
This is the safest method as you control the exact version.

1. Download the **Ren'Py SDK** for PC from the official website.
2. Open Ren'Py and click **"Create New Project"**.
3. Name it "Base7" or "Base8" (depending on the version).
4. Go to **"Android"** (you may need to install the Android support libraries inside Ren'Py).
5. Click **"Build Package"** -> **"Build Universal APK"**.
6. The resulting file (`Base7-release.apk`) is your **Base APK**. Keep it safe!

### Option 2: Download Universal Loaders
Search online communities (Lemma Soft, F95zone, etc.) for "Ren'Py Universal Android Loader". Ensure the version matches your target game.

## Ren'Py 7 vs Ren'Py 8 (Critical!)

There are two major eras of Ren'Py games, and they are **NOT compatible**:

| Feature | Ren'Py 7.x | Ren'Py 8.x |
|---------|------------|------------|
| **Python Version** | Python 2.7 | Python 3.9+ |
| **Status** | Legacy (but very common) | Modern standard |
| **Base APK** | Must use Ren'Py 7 Base | Must use Ren'Py 8 Base |

**How to check a game's version:**
1. Look at the game files.
2. If you see `renpy/common/00action_file.rpy` (or similar), open it with a text editor.
3. Or check the `renpy.exe` properties.
4. **Rule of Thumb**:
   - Games released before mid-2022 are likely Ren'Py 7.
   - Newer games are likely Ren'Py 8.

**What happens if I mix them?**
The game will crash immediately on launch (black screen then close).

## Features Explanation

### Image Resizing (720p)
- **Why?** PC games are often 1080p (1920x1080) or 4K. This makes the APK huge (2GB+) and can cause "Out of Memory" crashes on phones.
- **What it does:** Resizes all images to 1280x720 and updates the code (`gui.rpy`) to tell the engine the new resolution.
- **Result:** APK size reduced by ~40-60%, smoother performance.

### WebP Conversion
- Converts PNG/JPG images to WebP format.
- Further reduces size with minimal quality loss.

### Android Hotkeys
PC games rely on keyboard/mouse (Right Click to menu, 'H' to hide UI). Android phones don't have these.
Enabling this feature adds transparent buttons to the screen:
- **Skip**: Fast forwards text.
- **Menu**: Opens the Save/Load menu.
- **Hide**: Hides the text box to see the art.

## Step-by-Step Porting

1. **Clean the PC Game**:
   - Delete the `cache/` folder inside `game/`.
   - Delete any `.rpa` files if you have extracted them (optional, but loose files are easier to optimize).

2. **Open AutoModRenpy**:
   - Go to "PC to Android".
   - Select the PC Game folder.
   - Select your Base APK (make sure versions match!).

3. **Configure**:
   - App Name: "My Ported Game"
   - Package Name: `com.myname.mygame` (Must be unique!)
   - Check "Resize Images" (Recommended).
   - Check "Add Hotkeys".

4. **Build**:
   - Wait for the process to finish.
   - Install the APK on your phone.

5. **Uninstall First**:
   - If you are updating a previous version, uninstall it first unless you signed it with the exact same keystore.
