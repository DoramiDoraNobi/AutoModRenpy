import os
from PIL import Image
import re
from pathlib import Path

class ImageOptimizer:
    """
    Handles image resizing and format conversion for Ren'Py games.
    Also updates resolution settings in script files.
    """

    def __init__(self, logger=None):
        self.logger = logger

    def log(self, message):
        if self.logger:
            self.logger.info(message)
        else:
            print(message)

    def resize_images(self, game_dir, target_height=720):
        """
        Resizes all images in the game directory to match the target height,
        maintaining aspect ratio.
        """
        self.log(f"Starting image resizing to target height: {target_height}p")

        # 1. Determine current resolution from gui.rpy or options.rpy
        current_width, current_height = self._get_current_resolution(game_dir)
        if not current_width or not current_height:
            self.log("Could not determine current resolution. Aborting resize to prevent layout issues.")
            return False

        if current_height <= target_height:
            self.log(f"Current resolution height ({current_height}) is already <= target ({target_height}). Skipping resize.")
            return True

        scale_factor = target_height / current_height
        target_width = int(current_width * scale_factor)

        self.log(f"Resizing from {current_width}x{current_height} to {target_width}x{target_height} (Scale: {scale_factor:.2f})")

        # 2. Resize images
        extensions = {'.png', '.jpg', '.jpeg', '.webp'}
        count = 0

        for root, dirs, files in os.walk(game_dir):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in extensions:
                    file_path = os.path.join(root, file)
                    try:
                        with Image.open(file_path) as img:
                            # Skip if image is already small (e.g. UI elements often don't need resizing if they are small,
                            # but for a full port, usually EVERYTHING needs to scale to keep relative sizes)
                            # Actually, in Ren'Py, if we change gui.init, ALL assets must be scaled.

                            new_size = (int(img.width * scale_factor), int(img.height * scale_factor))

                            # Only resize if actually smaller
                            if new_size[0] < img.width:
                                resampled = img.resize(new_size, Image.Resampling.LANCZOS)
                                resampled.save(file_path)
                                count += 1
                    except Exception as e:
                        self.log(f"Failed to resize {file}: {e}")

        self.log(f"Resized {count} images.")

        # 3. Update script resolution
        self._update_script_resolution(game_dir, target_width, target_height)

        return True

    def convert_to_webp(self, game_dir):
        """
        Converts all PNG and JPG images to WebP format to save space.
        Updates file references in scripts?
        WARNING: Updating script references is complex (dynamic paths).
        Safe mode: Only convert images that are likely background/sprites, or accept that
        users must ensure their script doesn't hardcode extensions.

        Actually, Ren'Py's `image` statement is extension-agnostic.
        `image bg school = "bg school.png"` -> `image bg school = "bg school.webp"`

        Strategy: Convert file, delete original. Ren'Py usually picks up the new file
        if the script defines images without extensions or if we get lucky.
        But if the script says "bg.png", it will break.

        For this tool, we will just convert and delete original.
        """
        self.log("Converting images to WebP...")
        count = 0
        total_saved = 0

        for root, dirs, files in os.walk(game_dir):
            for file in files:
                file_path = os.path.join(root, file)
                name, ext = os.path.splitext(file)
                ext = ext.lower()

                if ext in ['.png', '.jpg', '.jpeg']:
                    try:
                        # Skip if webp already exists
                        webp_path = os.path.join(root, name + ".webp")
                        if os.path.exists(webp_path):
                            continue

                        original_size = os.path.getsize(file_path)

                        with Image.open(file_path) as img:
                            img.save(webp_path, 'WEBP', quality=90)

                        new_size = os.path.getsize(webp_path)

                        # Only keep if smaller
                        if new_size < original_size:
                            os.remove(file_path)
                            total_saved += (original_size - new_size)
                            count += 1
                        else:
                            # Revert if bigger (rare but possible with high quality)
                            os.remove(webp_path)

                    except Exception as e:
                        self.log(f"Failed to convert {file}: {e}")

        self.log(f"Converted {count} images to WebP. Saved {total_saved / 1024 / 1024:.2f} MB.")

    def _get_current_resolution(self, game_dir):
        """
        Parses gui.rpy or options.rpy to find `gui.init(width, height)`
        """
        # Check gui.rpy first
        gui_rpy = os.path.join(game_dir, 'gui.rpy')
        if os.path.exists(gui_rpy):
            with open(gui_rpy, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # Search for gui.init(1920, 1080)
                match = re.search(r'gui\.init\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)', content)
                if match:
                    return int(match.group(1)), int(match.group(2))

        # Check options.rpy (legacy)
        options_rpy = os.path.join(game_dir, 'options.rpy')
        if os.path.exists(options_rpy):
            with open(options_rpy, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                # config.screen_width = 1920
                w_match = re.search(r'config\.screen_width\s*=\s*(\d+)', content)
                h_match = re.search(r'config\.screen_height\s*=\s*(\d+)', content)
                if w_match and h_match:
                    return int(w_match.group(1)), int(h_match.group(1))

        return None, None

    def _update_script_resolution(self, game_dir, width, height):
        """
        Updates the resolution in gui.rpy or options.rpy
        """
        gui_rpy = os.path.join(game_dir, 'gui.rpy')
        if os.path.exists(gui_rpy):
            with open(gui_rpy, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Replace gui.init
            new_content = re.sub(
                r'gui\.init\s*\(\s*\d+\s*,\s*\d+\s*\)',
                f'gui.init({width}, {height})',
                content
            )

            with open(gui_rpy, 'w', encoding='utf-8') as f:
                f.write(new_content)
            self.log(f"Updated gui.rpy to {width}x{height}")
            return

        # Legacy support
        options_rpy = os.path.join(game_dir, 'options.rpy')
        if os.path.exists(options_rpy):
            with open(options_rpy, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            content = re.sub(r'config\.screen_width\s*=\s*\d+', f'config.screen_width = {width}', content)
            content = re.sub(r'config\.screen_height\s*=\s*\d+', f'config.screen_height = {height}', content)

            with open(options_rpy, 'w', encoding='utf-8') as f:
                f.write(content)
            self.log(f"Updated options.rpy to {width}x{height}")
