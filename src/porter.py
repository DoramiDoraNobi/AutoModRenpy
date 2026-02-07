import os
import shutil
import lxml.etree as ET
from pathlib import Path
from src.apk_handler import APKHandler
from src.image_optimizer import ImageOptimizer
from src.android_features import AndroidFeatures
from src.mod_processor import ModProcessor, ConflictStrategy

class PortingEngine:
    """
    Handles the PC to Android porting process.
    """

    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger
        self.apk_handler = APKHandler(config, logger)
        self.optimizer = ImageOptimizer(logger)
        self.features = AndroidFeatures(logger)
        self.mod_processor = ModProcessor(config, logger)
        self.temp_dir = config.get('temp_dir', 'temp')

    def port_game(self,
                  pc_game_dir: str,
                  base_apk_path: str,
                  output_apk_path: str,
                  app_name: str = None,
                  package_name: str = None,
                  icon_path: str = None,
                  resize: bool = False,
                  webp: bool = False,
                  hotkeys: bool = False,
                  mod_folders: list = None,
                  conflict_strategy: str = "new_file") -> bool:

        self.logger.info(f"Starting porting process for: {pc_game_dir}")

        # 1. Extract Base APK
        extract_dir = os.path.join(self.temp_dir, "port_base")
        if not self.apk_handler.extract_apk(base_apk_path, extract_dir):
            return False

        # 2. Locate Assets Directory in APK
        # Usually assets/x-game or assets/game
        assets_dir = os.path.join(extract_dir, 'assets')
        target_game_dir = None

        # Heuristic to find where to put the game files
        # RAPT usually uses 'x-game' for the private files
        potential_dirs = ['x-game', 'game']
        for d in potential_dirs:
            p = os.path.join(assets_dir, d)
            if os.path.exists(p):
                target_game_dir = p
                break

        if not target_game_dir:
            # Create x-game if not found
            target_game_dir = os.path.join(assets_dir, 'x-game')
            os.makedirs(target_game_dir, exist_ok=True)
            self.logger.info(f"Created target directory: {target_game_dir}")
        else:
            # Clean existing game files in base APK to avoid conflicts
            self.logger.info(f"Cleaning existing game files in base APK: {target_game_dir}")
            for item in os.listdir(target_game_dir):
                item_path = os.path.join(target_game_dir, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)

        # 3. Copy PC Game Files
        # We need to copy the contents of the PC game folder (game/, renpy/, etc usually?)
        # Actually, for RAPT, we usually copy the 'game' folder into 'x-game'
        # But wait, PC builds have:
        # /game
        # /renpy (engine)
        # /lib (binaries)
        # executable.exe

        # The Android APK already has the engine (librenpy.so) and python files in it.
        # We only need to inject the 'game' folder (assets + scripts).
        # We should NOT copy 'renpy', 'lib', etc.

        source_game_folder = os.path.join(pc_game_dir, 'game')
        if not os.path.exists(source_game_folder):
            self.logger.error(f"Could not find 'game' folder in {pc_game_dir}")
            return False

        dest_game_folder = os.path.join(target_game_dir, 'game')

        self.logger.info(f"Copying game files to {dest_game_folder}...")
        try:
            # Ignore common unnecessary files to save space
            ignore_pattern = shutil.ignore_patterns(
                'cache', 'saves', '.git*', '*.bak', '*.tmp',
                'thumbs.db', '.DS_Store', '__pycache__'
            )
            shutil.copytree(source_game_folder, dest_game_folder, ignore=ignore_pattern)
        except Exception as e:
            self.logger.error(f"Failed to copy files: {e}")
            return False

        # 4. Install Mods (if provided)
        if mod_folders:
            self.logger.info(f"Installing {len(mod_folders)} mods into ported game...")

            # Use mod processor
            # Note: dest_game_folder is likely .../x-game/game
            # But mod_processor usually expects the root of the game folder to scan for 'game/' subfolder
            # However, prepare_multiple_mods takes game_target_dir as the *destination* for files

            # Map strategy string to enum
            strategy_map = {
                "new_file": ConflictStrategy.NEW_FILE,
                "replace": ConflictStrategy.REPLACE,
                "skip": ConflictStrategy.SKIP
            }
            strategy = strategy_map.get(conflict_strategy, ConflictStrategy.NEW_FILE)

            # Prepare mods
            # game_target_dir should be dest_game_folder because that's where 'game/script.rpy' lives
            all_mods = self.mod_processor.prepare_multiple_mods(mod_folders, dest_game_folder)

            # Install mods
            for priority, mod_files in all_mods:
                self.logger.info(f"Installing Mod {priority}...")
                self.mod_processor.install_mod_files(mod_files, priority, strategy)

        # 5. Apply Modifications (Resize, WebP, Hotkeys)
        if not resize and not webp:
            self.logger.warning("Optimization flags (resize/webp) are disabled. APK size will likely remain large.")
            self.logger.warning("Use --resize or --webp to reduce APK size.")

        if resize:
            self.optimizer.resize_images(dest_game_folder, target_height=720)

        if webp:
            self.optimizer.convert_to_webp(dest_game_folder)

        if hotkeys:
            self.features.inject_hotkeys(dest_game_folder)

        # 6. Modify Manifest (Package Name, App Name)
        self._update_manifest(extract_dir, app_name, package_name)

        # 7. Update Icon
        if icon_path:
            self._update_icon(extract_dir, icon_path)

        # 8. Repackage
        if not self.apk_handler.repackage_apk(extract_dir, output_apk_path):
            return False

        # 9. Zipalign
        if not self.apk_handler.zipalign_apk(output_apk_path):
            self.logger.warning("Zipalign failed - APK might not install on some devices")

        # 10. Sign
        if not self.apk_handler.sign_apk(output_apk_path):
            return False

        self.logger.success(f"Porting complete! APK saved to: {output_apk_path}")
        return True

    def _update_manifest(self, extract_dir, app_name, package_name):
        """
        Updates AndroidManifest.xml and strings.xml
        """
        manifest_path = os.path.join(extract_dir, 'AndroidManifest.xml')
        if not os.path.exists(manifest_path):
            self.logger.warning("AndroidManifest.xml not found (ZIP extraction used?). Cannot update manifest.")
            return

        try:
            # Note: apktool decodes XML to readable text.
            # If ZIP extraction was used, this is binary XML and we can't edit it easily with lxml.
            # Assuming apktool was used if we are here (or text file).
            # We can check if it looks like XML.

            with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                head = f.read(100)

            if '\x00' in head:
                self.logger.warning("Binary XML detected. Cannot edit manifest without Apktool.")
                return

            tree = ET.parse(manifest_path)
            root = tree.getroot()

            # Update Package Name
            if package_name:
                self.logger.info(f"Setting package name to: {package_name}")
                if 'package' in root.attrib:
                    root.attrib['package'] = package_name
                else:
                    # Sometimes it's namespaced
                    root.set('package', package_name)

            tree.write(manifest_path, encoding='utf-8', xml_declaration=True)

            # Update App Name (usually in res/values/strings.xml)
            if app_name:
                self._update_app_name(extract_dir, app_name)

        except Exception as e:
            self.logger.error(f"Failed to update manifest: {e}")

    def _update_app_name(self, extract_dir, app_name):
        """
        Updates app_name in strings.xml
        """
        strings_path = os.path.join(extract_dir, 'res', 'values', 'strings.xml')
        if not os.path.exists(strings_path):
            self.logger.warning("strings.xml not found")
            return

        try:
            tree = ET.parse(strings_path)
            root = tree.getroot()

            # Find string name="app_name"
            found = False
            for string in root.findall('string'):
                if string.get('name') == 'app_name':
                    string.text = app_name
                    found = True
                    break

            if not found:
                # Add it
                elem = ET.SubElement(root, 'string', name='app_name')
                elem.text = app_name

            tree.write(strings_path, encoding='utf-8', xml_declaration=True)
            self.logger.info(f"Updated app name to: {app_name}")

        except Exception as e:
            self.logger.error(f"Failed to update app name: {e}")

    def _update_icon(self, extract_dir, icon_path):
        """
        Replaces the app icon.
        Searches for ic_launcher.png in res/mipmap-* or res/drawable-*
        """
        self.logger.info("Updating app icon...")

        # Load new icon
        try:
            new_icon = Image.open(icon_path)
        except Exception as e:
            self.logger.error(f"Failed to open new icon: {e}")
            return

        # Find all ic_launcher.png files
        res_dir = os.path.join(extract_dir, 'res')
        if not os.path.exists(res_dir):
            return

        count = 0
        for root, dirs, files in os.walk(res_dir):
            for file in files:
                if file == 'ic_launcher.png':
                    target_path = os.path.join(root, file)
                    # Get target size
                    try:
                        with Image.open(target_path) as old:
                            size = old.size
                        # Resize and save
                        resized = new_icon.resize(size, Image.Resampling.LANCZOS)
                        resized.save(target_path)
                        count += 1
                    except Exception as e:
                        self.logger.warning(f"Failed to replace icon at {target_path}: {e}")

        self.logger.info(f"Replaced {count} icon files.")
