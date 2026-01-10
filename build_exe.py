import PyInstaller.__main__
import os
import shutil

def build_exe():
    print("Building AutoModRenpy.exe...")

    # Clean dist/build folders
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")

    PyInstaller.__main__.run([
        'gui.py',
        '--name=AutoModRenpy',
        '--onefile',
        '--windowed',
        '--icon=NONE', # We don't have an icon yet
        '--add-data=src:src', # Include source code
        '--hidden-import=PIL',
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=lxml',
        '--hidden-import=tkinter',
        '--clean',
    ])

    print("Build complete.")

    # Create distribution folder
    dist_dir = "dist/AutoModRenpy_Release"
    os.makedirs(dist_dir, exist_ok=True)

    # Copy Exe
    shutil.copy("dist/AutoModRenpy.exe", dist_dir)

    # Copy Tools folder
    if os.path.exists("tools"):
        shutil.copytree("tools", os.path.join(dist_dir, "tools"))
    else:
        print("Warning: tools folder not found. Please add apktool/apksigner manually.")
        os.makedirs(os.path.join(dist_dir, "tools"))

    # Copy README
    if os.path.exists("README.md"):
        shutil.copy("README.md", dist_dir)

    print(f"Distribution ready at: {dist_dir}")

if __name__ == "__main__":
    build_exe()
