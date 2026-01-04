"""
Example script demonstrating AutoModRenpy usage
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from main import AutoModRenpy


def example_basic_usage():
    """Basic example: Install single mod"""
    app = AutoModRenpy()
    
    success = app.install_mods(
        apk_path="example_game.apk",
        mod_folders=["mods/my_mod/"],
        output_apk="modded_game.apk",
        create_backup=True,
        conflict_strategy="new_file"
    )
    
    if success:
        print("✓ Mod installation successful!")
    else:
        print("✗ Mod installation failed!")


def example_multiple_mods():
    """Install multiple mods with priority order"""
    app = AutoModRenpy()
    
    # Mods will be installed in this order (priority 1, 2, 3)
    # Higher priority mods load later and can override earlier ones
    mod_folders = [
        "mods/base_translation/",
        "mods/ui_improvements/",
        "mods/custom_content/"
    ]
    
    success = app.install_mods(
        apk_path="game.apk",
        mod_folders=mod_folders,
        output_apk="game_modded.apk",
        conflict_strategy="new_file"  # Create z01_, z02_, z03_ files
    )
    
    return success


def example_custom_keystore():
    """Use custom keystore for signing"""
    app = AutoModRenpy()
    
    success = app.install_mods(
        apk_path="game.apk",
        mod_folders=["mods/my_mod/"],
        output_apk="game_signed.apk",
        custom_keystore="path/to/custom.keystore",
        conflict_strategy="replace"  # Overwrite conflicting files
    )
    
    return success


def example_no_backup():
    """Skip backup creation (faster but less safe)"""
    app = AutoModRenpy()
    
    success = app.install_mods(
        apk_path="game.apk",
        mod_folders=["mods/quick_test/"],
        output_apk="game_test.apk",
        create_backup=False,  # Skip backup
        conflict_strategy="skip"  # Skip conflicting files
    )
    
    return success


def example_working_with_backups():
    """Manage backups programmatically"""
    app = AutoModRenpy()
    
    # Create backup manually
    backup_entry = app.backup_manager.create_backup(
        "original_game.apk",
        game_name="My Favorite Game",
        notes="Before installing gameplay mod"
    )
    
    # Install mods
    app.install_mods(
        apk_path="original_game.apk",
        mod_folders=["mods/gameplay_mod/"],
        output_apk="modded_game.apk",
        create_backup=False  # Already created manually
    )
    
    # Later: restore from backup if needed
    if backup_entry:
        app.backup_manager.restore_backup(backup_entry, "restored_game.apk")
    
    # List all backups
    all_backups = app.backup_manager.get_all_backups()
    for backup in all_backups:
        print(f"Backup: {backup.game_name} - {backup.timestamp}")
    
    # Cleanup old backups (keep 5 most recent per game)
    cleaned = app.backup_manager.cleanup_old_backups(max_backups_per_game=5)
    print(f"Cleaned up {cleaned} old backups")


def example_unrpa_extraction():
    """Extract RPA archives"""
    app = AutoModRenpy()
    
    # List RPA contents
    contents = app.unrpa.list_archive_contents("game/archive.rpa")
    for file_info in contents:
        print(f"{file_info['name']} - {file_info['size_formatted']}")
    
    # Get archive info
    info = app.unrpa.get_archive_info("game/archive.rpa")
    print(f"Archive version: {info['version']}")
    print(f"Total files: {info['file_count']}")
    print(f"Total size: {info['total_size_formatted']}")
    
    # Extract archive
    success = app.unrpa.extract_archive(
        "game/archive.rpa",
        "extracted_files/"
    )
    
    # Extract specific files only
    success = app.unrpa.extract_archive(
        "game/archive.rpa",
        "extracted_files/",
        file_list=["images/bg_room.png", "scripts/day1.rpy"]
    )


def example_script_validation():
    """Validate Renpy scripts before installation"""
    app = AutoModRenpy()
    
    # Validate single script
    is_valid, issues = app.script_validator.validate_script("mod/script.rpy")
    
    if is_valid:
        print("✓ Script is valid")
    else:
        print("✗ Script has errors:")
        for issue in issues:
            print(f"  {issue}")
    
    # Validate multiple scripts
    script_files = [
        "mod/script1.rpy",
        "mod/script2.rpy",
        "mod/init.rpy"
    ]
    
    results = app.script_validator.validate_multiple_scripts(script_files)
    summary = app.script_validator.get_validation_summary(results)
    
    print(f"Validated {summary['total_files']} files")
    print(f"Valid: {summary['valid_files']}")
    print(f"Errors: {summary['total_errors']}")
    print(f"Warnings: {summary['total_warnings']}")


if __name__ == "__main__":
    print("AutoModRenpy Examples")
    print("=" * 60)
    print("\nThese are example functions demonstrating API usage.")
    print("Uncomment the example you want to run.\n")
    
    # Uncomment to run:
    # example_basic_usage()
    # example_multiple_mods()
    # example_custom_keystore()
    # example_no_backup()
    # example_working_with_backups()
    # example_unrpa_extraction()
    # example_script_validation()
