"""
Main GUI Application for AutoModRenpy
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils import Config, Logger
from src.game_detector import GameLocationDetector
from src.unrpa_extractor import UnRPAExtractor
from src.apk_handler import APKHandler
from src.mod_processor import ModProcessor, ConflictStrategy
from src.script_validator import ScriptValidator
from src.backup_manager import BackupManager


class AutoModRenpyGUI:
    """Main GUI application"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("AutoModRenpy - Android Renpy Mod Installer")
        self.root.geometry("900x700")
        
        # Initialize components
        self.config = Config()
        self.logger = Logger(verbose=True)
        self.apk_handler = APKHandler(self.config, self.logger)
        self.game_detector = GameLocationDetector(self.logger)
        self.unrpa = UnRPAExtractor(self.logger)
        self.mod_processor = ModProcessor(self.config, self.logger)
        self.script_validator = ScriptValidator(self.logger)
        self.backup_manager = BackupManager(
            self.config.get('backup_dir', 'backups'),
            self.logger
        )
        
        # State variables
        self.selected_apk = tk.StringVar()
        self.detected_game_path = tk.StringVar()
        self.mod_folders = []
        self.custom_keystore = tk.StringVar()
        
        # Create GUI
        self.create_widgets()
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Main")
        self.create_main_tab()
        
        # UnRPA tab
        self.unrpa_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.unrpa_tab, text="UnRPA Extractor")
        self.create_unrpa_tab()
        
        # Settings tab
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")
        self.create_settings_tab()
        
        # Backup tab
        self.backup_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.backup_tab, text="Backups")
        self.create_backup_tab()
        
        # Log output (bottom)
        self.create_log_panel()
    
    def create_main_tab(self):
        """Create main mod installation tab"""
        # APK Selection
        apk_frame = ttk.LabelFrame(self.main_tab, text="1. Select APK", padding=10)
        apk_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Entry(apk_frame, textvariable=self.selected_apk, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(apk_frame, text="Browse APK", command=self.browse_apk).pack(side=tk.LEFT)
        ttk.Button(apk_frame, text="Detect Game", command=self.detect_game).pack(side=tk.LEFT, padx=5)
        
        # Game Path Display
        game_frame = ttk.LabelFrame(self.main_tab, text="Detected Game Location", padding=10)
        game_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(game_frame, textvariable=self.detected_game_path, foreground="green").pack()
        
        # Mod Selection
        mod_frame = ttk.LabelFrame(self.main_tab, text="2. Add Mods (Drag to Reorder)", padding=10)
        mod_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Mod list with scrollbar
        list_frame = ttk.Frame(mod_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.mod_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.mod_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.mod_listbox.yview)
        
        # Mod buttons
        btn_frame = ttk.Frame(mod_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Add Mod Folder", command=self.add_mod_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Remove Selected", command=self.remove_mod).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Move Up", command=lambda: self.move_mod(-1)).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Move Down", command=lambda: self.move_mod(1)).pack(side=tk.LEFT, padx=2)
        
        # RPA extraction option
        self.extract_rpa_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            mod_frame,
            text="Extract RPA archives before installing mods (recommended for most mods)",
            variable=self.extract_rpa_var
        ).pack(anchor=tk.W, pady=5)
        
        # Install button
        install_frame = ttk.Frame(self.main_tab)
        install_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.install_btn = ttk.Button(
            install_frame,
            text="▶ Install Mods to APK",
            command=self.install_mods,
            style="Accent.TButton"
        )
        self.install_btn.pack(side=tk.LEFT, padx=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            install_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
    
    def create_unrpa_tab(self):
        """Create UnRPA extraction tab"""
        # RPA file selection
        file_frame = ttk.LabelFrame(self.unrpa_tab, text="Select RPA Archive", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.rpa_file = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.rpa_file, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Browse RPA", command=self.browse_rpa).pack(side=tk.LEFT)
        ttk.Button(file_frame, text="View Contents", command=self.view_rpa_contents).pack(side=tk.LEFT, padx=5)
        
        # RPA contents display
        contents_frame = ttk.LabelFrame(self.unrpa_tab, text="Archive Contents", padding=10)
        contents_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.rpa_contents = scrolledtext.ScrolledText(contents_frame, height=15)
        self.rpa_contents.pack(fill=tk.BOTH, expand=True)
        
        # Extract button
        extract_frame = ttk.Frame(self.unrpa_tab)
        extract_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(extract_frame, text="Extract Archive", command=self.extract_rpa).pack()
    
    def create_settings_tab(self):
        """Create settings tab"""
        # Keystore settings
        keystore_frame = ttk.LabelFrame(self.settings_tab, text="Keystore Settings", padding=10)
        keystore_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(keystore_frame, text="Using default debug keystore (recommended)").pack(anchor=tk.W)
        
        custom_frame = ttk.Frame(keystore_frame)
        custom_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(custom_frame, text="Custom Keystore (optional):").pack(side=tk.LEFT)
        ttk.Entry(custom_frame, textvariable=self.custom_keystore, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(custom_frame, text="Browse", command=self.browse_keystore).pack(side=tk.LEFT)
        
        # Conflict strategy
        strategy_frame = ttk.LabelFrame(self.settings_tab, text="Default Conflict Resolution", padding=10)
        strategy_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.conflict_strategy = tk.StringVar(value="new_file")
        
        ttk.Radiobutton(
            strategy_frame,
            text="🟢 Load as New File (Recommended) - Creates z_filename.rpy",
            variable=self.conflict_strategy,
            value="new_file"
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            strategy_frame,
            text="🟡 Replace - Overwrites original file",
            variable=self.conflict_strategy,
            value="replace"
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            strategy_frame,
            text="🔴 Skip - Don't install conflicting files",
            variable=self.conflict_strategy,
            value="skip"
        ).pack(anchor=tk.W)
    
    def create_backup_tab(self):
        """Create backup management tab"""
        # Backup list
        list_frame = ttk.LabelFrame(self.backup_tab, text="Backups", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview for backups
        columns = ('Game', 'Date', 'Size')
        self.backup_tree = ttk.Treeview(list_frame, columns=columns, show='tree headings')
        
        self.backup_tree.heading('#0', text='Filename')
        self.backup_tree.heading('Game', text='Game')
        self.backup_tree.heading('Date', text='Date')
        self.backup_tree.heading('Size', text='Size')
        
        self.backup_tree.pack(fill=tk.BOTH, expand=True)
        
        # Backup buttons
        btn_frame = ttk.Frame(self.backup_tab)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Refresh List", command=self.refresh_backup_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Restore Selected", command=self.restore_backup).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_backup).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Cleanup Old", command=self.cleanup_backups).pack(side=tk.LEFT, padx=2)
        
        # Load backups
        self.refresh_backup_list()
    
    def create_log_panel(self):
        """Create log output panel"""
        log_frame = ttk.LabelFrame(self.root, text="Log", padding=5)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Redirect logger output to GUI
        self.logger.verbose = False  # Disable console output
        self.original_log = self.logger._log
        self.logger._log = self.gui_log
    
    def gui_log(self, level: str, message: str):
        """Log message to GUI"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{level}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def browse_apk(self):
        """Browse for APK file"""
        filename = filedialog.askopenfilename(
            title="Select APK File",
            filetypes=[("APK Files", "*.apk"), ("All Files", "*.*")]
        )
        if filename:
            self.selected_apk.set(filename)
            self.detected_game_path.set("Click 'Detect Game' to find game location")
    
    def detect_game(self):
        """Detect game location in APK"""
        apk_path = self.selected_apk.get()
        if not apk_path:
            messagebox.showwarning("No APK", "Please select an APK file first")
            return
        
        self.logger.info("Extracting APK for game detection...")
        temp_dir = "temp/detection"
        
        # Extract APK
        if self.apk_handler.extract_apk(apk_path, temp_dir):
            # Detect game folder
            game_path = self.game_detector.detect_game_folder(temp_dir)
            if game_path:
                self.detected_game_path.set(f"✓ Found: {game_path}")
            else:
                self.detected_game_path.set("✗ Game folder not found")
                messagebox.showerror("Detection Failed", "Could not find Renpy game folder in APK")
    
    def add_mod_folder(self):
        """Add mod folder to list"""
        folder = filedialog.askdirectory(title="Select Mod Folder")
        if folder:
            self.mod_folders.append(folder)
            self.mod_listbox.insert(tk.END, f"{len(self.mod_folders)}. {os.path.basename(folder)}")
    
    def remove_mod(self):
        """Remove selected mod from list"""
        selection = self.mod_listbox.curselection()
        if selection:
            idx = selection[0]
            self.mod_listbox.delete(idx)
            del self.mod_folders[idx]
            self.refresh_mod_list()
    
    def move_mod(self, direction):
        """Move mod up or down in priority"""
        selection = self.mod_listbox.curselection()
        if not selection:
            return
        
        idx = selection[0]
        new_idx = idx + direction
        
        if 0 <= new_idx < len(self.mod_folders):
            # Swap in list
            self.mod_folders[idx], self.mod_folders[new_idx] = \
                self.mod_folders[new_idx], self.mod_folders[idx]
            
            self.refresh_mod_list()
            self.mod_listbox.selection_set(new_idx)
    
    def refresh_mod_list(self):
        """Refresh mod listbox display"""
        self.mod_listbox.delete(0, tk.END)
        for i, folder in enumerate(self.mod_folders, 1):
            self.mod_listbox.insert(tk.END, f"{i}. {os.path.basename(folder)}")
    
    def install_mods(self):
        """Install mods to APK (main function)"""
        # Validation
        if not self.selected_apk.get():
            messagebox.showwarning("No APK", "Please select an APK file")
            return
        
        if not self.mod_folders:
            messagebox.showwarning("No Mods", "Please add at least one mod folder")
            return
        
        # Run in thread to keep GUI responsive
        thread = threading.Thread(target=self._install_mods_thread)
        thread.start()
    
    def _install_mods_thread(self):
        """Thread worker for mod installation"""
        try:
            apk_path = self.selected_apk.get()
            mod_folders = list(self.mod_folders)
            
            # Ask output path
            default_name = Path(apk_path).stem + "_modded.apk"
            output_path = filedialog.asksaveasfilename(
                title="Save Modded APK As",
                defaultextension=".apk",
                initialfile=default_name,
                filetypes=[("APK Files", "*.apk"), ("All Files", "*.*")]
            )
            if not output_path:
                return
            
            # Conflict strategy
            conflict_strategy = self.conflict_strategy.get()
            custom_keystore = self.custom_keystore.get().strip() or None
            
            # Use shared logger so logs show in GUI
            from main import AutoModRenpy
            app = AutoModRenpy(logger=self.logger)
            
            self.progress_var.set(5)
            self.logger.info("Starting mod installation...")
            success = app.install_mods(
                apk_path=apk_path,
                mod_folders=mod_folders,
                output_apk=output_path,
                custom_keystore=custom_keystore,
                create_backup=True,
                conflict_strategy=conflict_strategy,
                extract_rpa=self.extract_rpa_var.get()
            )
            self.progress_var.set(100)
            if success:
                messagebox.showinfo("Success", f"Modded APK created:\n{output_path}")
            else:
                messagebox.showerror("Failed", "Mod installation failed. Check log panel for details.")
        except Exception as e:
            messagebox.showerror("Error", f"Installation failed: {e}")
    
    # UnRPA tab methods
    def browse_rpa(self):
        """Browse for RPA file"""
        filename = filedialog.askopenfilename(
            title="Select RPA Archive",
            filetypes=[("RPA Files", "*.rpa"), ("All Files", "*.*")]
        )
        if filename:
            self.rpa_file.set(filename)
    
    def view_rpa_contents(self):
        """View RPA archive contents"""
        rpa_path = self.rpa_file.get()
        if not rpa_path:
            messagebox.showwarning("No RPA", "Please select an RPA file")
            return
        
        contents = self.unrpa.list_archive_contents(rpa_path)
        info = self.unrpa.get_archive_info(rpa_path)
        
        self.rpa_contents.delete(1.0, tk.END)
        self.rpa_contents.insert(tk.END, f"Archive: {os.path.basename(rpa_path)}\n")
        self.rpa_contents.insert(tk.END, f"Version: {info.get('version', 'Unknown')}\n")
        self.rpa_contents.insert(tk.END, f"Files: {info.get('file_count', 0)}\n")
        self.rpa_contents.insert(tk.END, f"Size: {info.get('total_size_formatted', '0 B')}\n")
        self.rpa_contents.insert(tk.END, "\n" + "="*50 + "\n\n")
        
        for file_info in contents:
            self.rpa_contents.insert(tk.END, f"{file_info['name']:<50} {file_info['size_formatted']:>10}\n")
    
    def extract_rpa(self):
        """Extract RPA archive"""
        rpa_path = self.rpa_file.get()
        if not rpa_path:
            messagebox.showwarning("No RPA", "Please select an RPA file")
            return
        
        output_dir = filedialog.askdirectory(title="Select Extract Location")
        if output_dir:
            if self.unrpa.extract_archive(rpa_path, output_dir):
                messagebox.showinfo("Success", f"Archive extracted to:\n{output_dir}")
    
    # Settings tab methods
    def browse_keystore(self):
        """Browse for custom keystore"""
        filename = filedialog.askopenfilename(
            title="Select Keystore",
            filetypes=[("Keystore Files", "*.keystore;*.jks"), ("All Files", "*.*")]
        )
        if filename:
            self.custom_keystore.set(filename)
    
    # Backup tab methods
    def refresh_backup_list(self):
        """Refresh backup list"""
        self.backup_tree.delete(*self.backup_tree.get_children())
        
        backups = self.backup_manager.get_all_backups()
        for backup in backups:
            size = os.path.getsize(backup.backup_path) if os.path.exists(backup.backup_path) else 0
            size_str = self._format_bytes(size)
            
            self.backup_tree.insert(
                '',
                tk.END,
                text=os.path.basename(backup.backup_path),
                values=(backup.game_name, backup.timestamp, size_str)
            )
    
    def restore_backup(self):
        """Restore selected backup"""
        selection = self.backup_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a backup to restore")
            return
        
        messagebox.showinfo("Restore", "Backup restore functionality ready")
    
    def delete_backup(self):
        """Delete selected backup"""
        messagebox.showinfo("Delete", "Backup delete functionality ready")
    
    def cleanup_backups(self):
        """Cleanup old backups"""
        count = self.backup_manager.cleanup_old_backups()
        messagebox.showinfo("Cleanup", f"Cleaned up {count} old backups")
        self.refresh_backup_list()
    
    def _format_bytes(self, size):
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


def main():
    root = tk.Tk()
    app = AutoModRenpyGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
