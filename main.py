"""
Main Application Entry Point
Complete mod installation workflow and PC-to-Android porting
"""
import os
import sys
import shutil
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils import Config, Logger, Cache, ensure_dir, clean_temp_dir, calculate_file_hash
from src.game_detector import GameLocationDetector
from src.unrpa_extractor import UnRPAExtractor
from src.apk_handler import APKHandler
from src.mod_processor import ModProcessor, ConflictStrategy
from src.script_validator import ScriptValidator
from src.backup_manager import BackupManager
from src.porter import PortingEngine


class AutoModRenpy:
    """Main application class for mod installation and porting"""
    
    def __init__(self, config_path: str = "config.json", logger: Logger | None = None):
        self.config = Config(config_path)
        # Allow external logger (GUI) to plug in; fall back to file logger
        self.logger = logger or Logger(log_file="logs/automodrenpy.log", verbose=True)
        
        # Initialize components
        self.apk_handler = APKHandler(self.config, self.logger)
        self.game_detector = GameLocationDetector(self.logger)
        self.unrpa_extractor = UnRPAExtractor(self.logger) # Fixed name
        self.mod_processor = ModProcessor(self.config, self.logger)
        self.script_validator = ScriptValidator(self.logger)
        self.backup_manager = BackupManager(
            self.config.get('backup_dir', 'backups'),
            self.logger
        )
        self.porter = PortingEngine(self.config, self.logger)
        
        # Cache for game locations
        cache_file = self.config.get('cache_file', 'cache/game_locations.json')
        max_cache = self.config.get('max_cache_entries', 100)
        self.cache = Cache(cache_file, max_cache)
        
        # Working directories
        self.temp_dir = self.config.get('temp_dir', 'temp')
        ensure_dir(self.temp_dir)
        ensure_dir("logs")
    
    def install_mods(self, apk_path: str, mod_folders: list, output_apk: str,
                     custom_keystore: str = None, create_backup: bool = True,
                     conflict_strategy: str = "new_file", extract_rpa: bool = True) -> bool:
        """
        Complete workflow to install mods into APK
        
        Args:
            apk_path: Path to original APK file
            mod_folders: List of mod folder paths (in priority order)
            output_apk: Path for output modded APK
            custom_keystore: Optional path to custom keystore
            create_backup: Whether to create backup of original APK
            conflict_strategy: Default conflict resolution strategy
            extract_rpa: Whether to extract RPA archives before installing mods
            
        Returns:
            True if installation successful
        """
        try:
            self.logger.info("="*60)
            self.logger.info("Starting AutoModRenpy Installation")
            self.logger.info("="*60)
            
            # Step 1: Validate inputs
            if not os.path.exists(apk_path):
                self.logger.error(f"APK file not found: {apk_path}")
                return False
            
            if not mod_folders:
                self.logger.error("No mod folders provided")
                return False
            
            # Step 2: Create backup
            if create_backup:
                self.logger.info("\n[Step 1/9] Creating backup...")
                game_name = Path(apk_path).stem
                backup_entry = self.backup_manager.create_backup(
                    apk_path,
                    game_name,
                    f"Pre-mod backup for {len(mod_folders)} mods"
                )
                if not backup_entry:
                    self.logger.warning("Backup creation failed, continuing anyway...")
            
            # Step 3: Extract APK
            self.logger.info("\n[Step 2/9] Extracting APK...")
            apk_hash = calculate_file_hash(apk_path)
            extract_dir = os.path.join(self.temp_dir, f"apk_{apk_hash[:8]}")
            
            if not self.apk_handler.extract_apk(apk_path, extract_dir):
                self.logger.error("APK extraction failed")
                return False
            
            # Step 4: Detect game location
            self.logger.info("\n[Step 3/9] Detecting game location...")
            
            # Check cache first
            cached_path = self.cache.get(apk_hash)
            if cached_path:
                self.logger.info(f"Using cached game location: {cached_path}")
                game_path = cached_path
            else:
                game_path = self.game_detector.detect_game_folder(extract_dir)
                if not game_path:
                    self.logger.error("Could not find Renpy game folder in APK")
                    return False
                
                # Cache the detected path
                self.cache.set(apk_hash, game_path)
            
            game_full_path = os.path.join(extract_dir, game_path)
            
            # Get game info
            game_info = self.game_detector.get_game_info(game_full_path)
            self.logger.info(f"Game folder contains: {game_info.get('total_files', 0)} files")
            self.logger.info(f"  - .rpy scripts: {len(game_info.get('rpy_files', []))}")
            self.logger.info(f"  - .rpyc files: {len(game_info.get('rpyc_files', []))}")
            self.logger.info(f"  - .rpa archives: {len(game_info.get('rpa_archives', []))}")
            
            # Step 4: Extract RPA archives if requested
            if extract_rpa and game_info.get('rpa_archives'):
                self.logger.info(f"\n[Step 4/9] Extracting {len(game_info['rpa_archives'])} RPA archive(s)...")
                rpa_extract_count = 0
                for rpa_file in game_info['rpa_archives']:
                    rpa_full_path = os.path.join(game_full_path, rpa_file)
                    self.logger.info(f"Extracting: {rpa_file}")
                    try:
                        if self.unrpa_extractor.extract_archive(rpa_full_path, game_full_path):
                            rpa_extract_count += 1
                        else:
                            self.logger.warning(f"Failed to extract: {rpa_file}")
                    except Exception as e:
                        self.logger.warning(f"Error extracting {rpa_file}: {e}")
                
                if rpa_extract_count > 0:
                    self.logger.success(f"Extracted {rpa_extract_count} RPA archive(s)")
                else:
                    self.logger.warning("No RPA archives were successfully extracted")
            
            # Step 5: Process mods
            self.logger.info(f"\n[Step 5/9] Processing {len(mod_folders)} mod(s)...")
            
            all_mods = self.mod_processor.prepare_multiple_mods(mod_folders, game_full_path)
            
            # Show conflict report
            conflicts = self.mod_processor.get_conflict_report(all_mods)
            if conflicts:
                self.logger.warning(f"Found {len(conflicts)} conflicting files:")
                for filename, mods in conflicts.items():
                    self.logger.warning(f"  - {filename}: {', '.join(mods)}")
            
            # Step 6: Validate scripts
            self.logger.info("\n[Step 6/9] Validating mod scripts...")
            
            # Convert strategy string to enum
            strategy_map = {
                "new_file": ConflictStrategy.NEW_FILE,
                "replace": ConflictStrategy.REPLACE,
                "skip": ConflictStrategy.SKIP
            }
            default_strategy = strategy_map.get(conflict_strategy, ConflictStrategy.NEW_FILE)
            
            # Collect all script files
            script_files = []
            for priority, mod_files in all_mods:
                for mod_file in mod_files:
                    if mod_file.is_script and mod_file.source_path.endswith('.rpy'):
                        script_files.append(mod_file.source_path)
            
            if script_files:
                validation_results = self.script_validator.validate_multiple_scripts(script_files)
                summary = self.script_validator.get_validation_summary(validation_results)
                
                self.logger.info(f"Validated {summary['total_files']} script files")
                if summary['total_errors'] > 0:
                    self.logger.warning(f"Found {summary['total_errors']} errors in scripts")
                    self.logger.warning("Continuing anyway - Renpy will show detailed errors at runtime")
                if summary['total_warnings'] > 0:
                    self.logger.warning(f"Found {summary['total_warnings']} warnings in scripts")
            
            # Step 7: Install mods
            self.logger.info("\n[Step 7/9] Installing mods to game folder...")
            
            total_stats = {
                'installed': 0,
                'skipped': 0,
                'replaced': 0,
                'new_files': 0,
                'errors': 0
            }
            
            for priority, mod_files in all_mods:
                self.logger.info(f"\nInstalling Mod {priority} ({len(mod_files)} files)...")
                
                # Set default strategy for conflicting files
                for mod_file in mod_files:
                    if mod_file.conflicts and not hasattr(mod_file, 'strategy'):
                        mod_file.strategy = default_strategy
                
                stats = self.mod_processor.install_mod_files(mod_files, priority, default_strategy)
                
                # Aggregate stats
                for key in total_stats:
                    total_stats[key] += stats[key]
                
                self.logger.success(f"Mod {priority} installed: {stats['installed']} files")
            
            # Log summary
            self.logger.info("\n" + "="*60)
            self.logger.success(f"Total files installed: {total_stats['installed']}")
            if total_stats['new_files'] > 0:
                self.logger.info(f"  - New files created (conflicts): {total_stats['new_files']}")
            if total_stats['replaced'] > 0:
                self.logger.warning(f"  - Files replaced: {total_stats['replaced']}")
            if total_stats['skipped'] > 0:
                self.logger.info(f"  - Files skipped: {total_stats['skipped']}")
            if total_stats['errors'] > 0:
                self.logger.error(f"  - Errors: {total_stats['errors']}")
            self.logger.info("="*60)
            
            # Step 8: Modify AndroidManifest for signature bypass
            self.logger.info("\n[Step 8/9] Applying signature bypass...")
            if getattr(self.apk_handler, 'used_apktool', False):
                self._apply_signature_bypass(extract_dir)
            else:
                self.logger.warning("Skipping manifest modification (ZIP extraction used)")
                self.logger.warning("Binary XML cannot be safely modified without apktool")
            
            # Step 9: Repackage APK
            self.logger.info("\n[Step 9/9] Repackaging and signing APK...")
            
            if not self.apk_handler.repackage_apk(extract_dir, output_apk):
                self.logger.error("APK repackaging failed")
                return False
            
            # Zipalign APK
            if not self.apk_handler.zipalign_apk(output_apk):
                self.logger.warning("Zipalign failed - APK might not install on some devices")

            # Sign APK
            if not self.apk_handler.sign_apk(output_apk, custom_keystore):
                self.logger.error("APK signing failed")
                return False
            
            # Success!
            self.logger.info("\n" + "="*60)
            self.logger.success("MOD INSTALLATION COMPLETE!")
            self.logger.success(f"Output APK: {output_apk}")
            self.logger.info("="*60)
            self.logger.warning("\n⚠️  IMPORTANT NOTES:")
            self.logger.warning("1. You must UNINSTALL the original game before installing this modded version")
            self.logger.warning("2. This APK uses a debug signature and won't update from Play Store")
            self.logger.warning("3. Keep your backup in case you need to restore the original")
            
            # Cleanup temp directory
            self.logger.info("\nCleaning up temporary files...")
            try:
                shutil.rmtree(extract_dir)
            except:
                pass
            
            return True
        
        except Exception as e:
            self.logger.error(f"Installation failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _apply_signature_bypass(self, apk_dir: str):
        """
        Apply signature bypass by modifying AndroidManifest.xml
        
        Args:
            apk_dir: Directory containing extracted APK
        """
        try:
            manifest_path = os.path.join(apk_dir, 'AndroidManifest.xml')
            
            if not os.path.exists(manifest_path):
                self.logger.warning("AndroidManifest.xml not found, skipping signature bypass")
                return
            
            # Read manifest
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add debuggable flag if not present
            if 'android:debuggable' not in content:
                # Find <application tag
                if '<application' in content:
                    content = content.replace(
                        '<application',
                        '<application\n        android:debuggable="true"',
                        1
                    )
                    
                    # Write back
                    with open(manifest_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.logger.success("Added android:debuggable='true' to AndroidManifest.xml")
            else:
                self.logger.info("AndroidManifest.xml already has debuggable flag")
        
        except Exception as e:
            self.logger.warning(f"Could not modify AndroidManifest.xml: {e}")


def main():
    """Main entry point for CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AutoModRenpy - Android Renpy Game Mod Installer & Porter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Install single mod
  python main.py --apk game.apk --mod mod_folder/ --output modded_game.apk
  
  # Port PC game to Android
  python main.py --port --pc-game path/to/game --base-apk base.apk --output ported.apk
        """
    )
    
    # Common arguments
    parser.add_argument('--gui', action='store_true', help='Launch GUI mode')

    # Porting mode flag
    parser.add_argument('--port', action='store_true', help='Enable PC to Android porting mode')

    # Modding arguments
    parser.add_argument('--apk', help='Path to original APK file (for modding)')
    parser.add_argument('--mod', nargs='+', help='Mod folder(s) (for modding)')
    parser.add_argument('--output', help='Path for output APK')
    parser.add_argument('--keystore', help='Path to custom keystore')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup')
    parser.add_argument('--strategy', choices=['new_file', 'replace', 'skip'], 
                       default='new_file', help='Conflict resolution strategy')

    # Porting arguments
    parser.add_argument('--pc-game', help='Path to PC game directory (for porting)')
    parser.add_argument('--base-apk', help='Path to Base APK (for porting)')
    parser.add_argument('--app-name', help='App Name (for porting)')
    parser.add_argument('--package-name', help='Package Name e.g. com.game (for porting)')
    parser.add_argument('--icon', help='Path to icon PNG (for porting)')
    parser.add_argument('--resize', action='store_true', help='Resize images to 720p')
    parser.add_argument('--webp', action='store_true', help='Convert images to WebP')
    parser.add_argument('--hotkeys', action='store_true', help='Inject Android hotkeys')
    parser.add_argument('--resolution', help='Manually specify resolution (e.g. 1920x1080)')
    
    args = parser.parse_args()
    
    # Launch GUI if requested or no args
    if args.gui or len(sys.argv) == 1:
        from gui import main as gui_main
        gui_main()
        return
    
    app = AutoModRenpy()
    
    if args.port:
        if not args.pc_game or not args.base_apk or not args.output:
            print("Error: --pc-game, --base-apk, and --output are required for porting mode.")
            sys.exit(1)

        success = app.porter.port_game(
            pc_game_dir=args.pc_game,
            base_apk_path=args.base_apk,
            output_apk_path=args.output,
            app_name=args.app_name,
            package_name=args.package_name,
            icon_path=args.icon,
            resize=args.resize,
            webp=args.webp,
            hotkeys=args.hotkeys,
            mod_folders=args.mod,
            conflict_strategy=args.strategy,
            manual_resolution=args.resolution
        )
    else:
        # Modding mode
        if not args.apk or not args.mod or not args.output:
            print("Error: --apk, --mod, and --output are required for modding mode.")
            sys.exit(1)

        success = app.install_mods(
            apk_path=args.apk,
            mod_folders=args.mod,
            output_apk=args.output,
            custom_keystore=args.keystore,
            create_backup=not args.no_backup,
            conflict_strategy=args.strategy
        )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
