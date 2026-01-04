"""
APK Handler Module
Handles APK extraction, repackaging, and signing
"""
import os
import shutil
import subprocess
import zipfile
from typing import Optional
from pathlib import Path


class APKHandler:
    """Handle APK extraction, modification, and signing"""
    
    def __init__(self, config, logger=None):
        self.config = config
        self.logger = logger
        # Resolve paths to absolute (in case working directory differs)
        self.apktool_path = self._resolve_path(config.get('apktool_path', 'tools/apktool.bat'))
        self.apksigner_path = self._resolve_path(config.get('apksigner_path', 'tools/apksigner.bat'))
        self.zipalign_path = self._resolve_path(config.get('zipalign_path', 'tools/zipalign.exe'))
        self.temp_dir = config.get('temp_dir', 'temp')
    
    def extract_apk(self, apk_path: str, output_dir: str) -> bool:
        """
        Extract APK using apktool for proper decompilation
        
        Args:
            apk_path: Path to APK file
            output_dir: Directory to extract to
            
        Returns:
            True if extraction successful
        """
        try:
            self._log_info(f"Extracting APK: {os.path.basename(apk_path)}")
            
            # Clean output directory
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
            os.makedirs(output_dir, exist_ok=True)
            
            # Check if apktool exists
            if not self._check_apktool():
                # Fallback to ZIP extraction if apktool not available
                self._log_warning("Apktool not found, using ZIP extraction (limited functionality)")
                return self._extract_apk_as_zip(apk_path, output_dir)
            
            # Use apktool for proper extraction
            try:
                cmd = [
                    self.apktool_path,
                    'd',  # decode
                    apk_path,
                    '-o', output_dir,
                    '-f'  # force overwrite
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    self._log_success(f"APK extracted successfully to: {output_dir}")
                    return True
                else:
                    self._log_error(f"Apktool extraction failed: {result.stderr}")
                    # Fallback to ZIP extraction
                    return self._extract_apk_as_zip(apk_path, output_dir)
            except subprocess.TimeoutExpired:
                self._log_error("Apktool extraction timed out (5 minutes)")
                return self._extract_apk_as_zip(apk_path, output_dir)
        
        except Exception as e:
            self._log_error(f"Error extracting APK: {e}")
            return False
    
    def _extract_apk_as_zip(self, apk_path: str, output_dir: str) -> bool:
        """
        Extract APK as ZIP file (fallback method)
        
        Args:
            apk_path: Path to APK file
            output_dir: Directory to extract to
            
        Returns:
            True if extraction successful
        """
        try:
            self._log_info("Using ZIP extraction method...")
            
            with zipfile.ZipFile(apk_path, 'r') as zip_ref:
                zip_ref.extractall(output_dir)
            
            self._log_success(f"APK extracted as ZIP to: {output_dir}")
            return True
        
        except Exception as e:
            self._log_error(f"ZIP extraction failed: {e}")
            return False
    
    def repackage_apk(self, source_dir: str, output_apk: str) -> bool:
        """
        Repackage directory into APK
        
        Args:
            source_dir: Directory containing modified APK contents
            output_apk: Path for output APK file
            
        Returns:
            True if repackaging successful
        """
        try:
            self._log_info(f"Repackaging APK: {os.path.basename(output_apk)}")
            
            # Check if apktool exists
            if not self._check_apktool():
                # Fallback to ZIP repackaging
                self._log_warning("Apktool not found, using ZIP repackaging")
                return self._repackage_as_zip(source_dir, output_apk)
            
            # Use apktool for proper repackaging
            cmd = [
                self.apktool_path,
                'b',  # build
                source_dir,
                '-o', output_apk,
                '-f'  # force overwrite
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self._log_success(f"APK repackaged successfully")
                return True
            else:
                self._log_error(f"Apktool repackaging failed: {result.stderr}")
                return self._repackage_as_zip(source_dir, output_apk)
        
        except Exception as e:
            self._log_error(f"Error repackaging APK: {e}")
            return False
    
    def _repackage_as_zip(self, source_dir: str, output_apk: str) -> bool:
        """
        Repackage directory as ZIP (fallback method)
        
        Args:
            source_dir: Directory to package
            output_apk: Output APK path
            
        Returns:
            True if successful
        """
        try:
            self._log_info("Using ZIP repackaging method...")
            
            with zipfile.ZipFile(output_apk, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, source_dir)
                        zipf.write(file_path, arcname)
            
            self._log_success(f"APK repackaged as ZIP")
            return True
        
        except Exception as e:
            self._log_error(f"ZIP repackaging failed: {e}")
            return False
    
    def sign_apk(self, apk_path: str, keystore_path: Optional[str] = None, 
                 keystore_password: Optional[str] = None, 
                 key_alias: Optional[str] = None) -> bool:
        """
        Sign APK with keystore
        
        Args:
            apk_path: Path to unsigned APK
            keystore_path: Path to keystore (uses default if None)
            keystore_password: Keystore password (uses default if None)
            key_alias: Key alias (uses default if None)
            
        Returns:
            True if signing successful
        """
        try:
            self._log_info(f"Signing APK: {os.path.basename(apk_path)}")
            
            # Strip old signature first
            self._strip_signature(apk_path)
            
            # Use provided keystore or default
            keystore = keystore_path or self.config.get('default_keystore')
            keystore = self._resolve_path(keystore)  # Resolve to absolute path
            password = keystore_password or self.config.get('keystore_password', 'android')
            alias = key_alias or self.config.get('keystore_alias', 'androiddebugkey')
            
            # Check if keystore exists
            if not os.path.exists(keystore):
                self._log_error(f"Keystore not found: {keystore}")
                self._log_info("Attempting to create default debug keystore...")
                if not self._create_debug_keystore(keystore, password, alias):
                    return False
            
            # Try to use apksigner first (Android SDK tool)
            if self._sign_with_apksigner(apk_path, keystore, password, alias):
                return True
            
            # Fallback to jarsigner
            self._log_warning("apksigner not available, trying jarsigner...")
            return self._sign_with_jarsigner(apk_path, keystore, password, alias)
        
        except Exception as e:
            self._log_error(f"Error signing APK: {e}")
            return False
    
    def _strip_signature(self, apk_path: str):
        """
        Strip old signature from APK by removing META-INF folder
        
        Args:
            apk_path: Path to APK file
        """
        try:
            self._log_info("Stripping old signature (removing META-INF)...")
            
            # Extract APK to temp location
            temp_extract = os.path.join(self.temp_dir, 'sign_temp')
            if os.path.exists(temp_extract):
                shutil.rmtree(temp_extract)
            
            with zipfile.ZipFile(apk_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract)
            
            # Remove META-INF folder
            meta_inf_path = os.path.join(temp_extract, 'META-INF')
            if os.path.exists(meta_inf_path):
                shutil.rmtree(meta_inf_path)
                self._log_info("Removed META-INF folder")
            
            # Repackage without META-INF
            with zipfile.ZipFile(apk_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_extract):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_extract)
                        zipf.write(file_path, arcname)
            
            # Cleanup temp
            shutil.rmtree(temp_extract)
        
        except Exception as e:
            self._log_warning(f"Could not strip signature: {e}")
    
    def _sign_with_apksigner(self, apk_path: str, keystore: str, password: str, alias: str) -> bool:
        """Sign APK using apksigner"""
        try:
            # Check if apksigner exists
            if not os.path.exists(self.apksigner_path):
                # Try to find apksigner in PATH
                if shutil.which('apksigner'):
                    apksigner_cmd = 'apksigner'
                else:
                    return False
            else:
                apksigner_cmd = self.apksigner_path
            
            cmd = [
                apksigner_cmd,
                'sign',
                '--ks', keystore,
                '--ks-pass', f'pass:{password}',
                '--ks-key-alias', alias,
                '--key-pass', f'pass:{password}',
                apk_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self._log_success("APK signed successfully with apksigner")
                return True
            else:
                self._log_error(f"apksigner failed: {result.stderr}")
                return False
        
        except Exception as e:
            self._log_error(f"apksigner error: {e}")
            return False
    
    def _sign_with_jarsigner(self, apk_path: str, keystore: str, password: str, alias: str) -> bool:
        """Sign APK using jarsigner (fallback)"""
        try:
            cmd = [
                'jarsigner',
                '-verbose',
                '-sigalg', 'SHA1withRSA',
                '-digestalg', 'SHA1',
                '-keystore', keystore,
                '-storepass', password,
                '-keypass', password,
                apk_path,
                alias
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self._log_success("APK signed successfully with jarsigner")
                
                # Verify signature
                verify_cmd = ['jarsigner', '-verify', apk_path]
                verify_result = subprocess.run(verify_cmd, capture_output=True, text=True)
                
                if 'jar verified' in verify_result.stdout.lower():
                    self._log_success("APK signature verified")
                    return True
                else:
                    self._log_warning("APK signature verification uncertain")
                    return True
            else:
                self._log_error(f"jarsigner failed: {result.stderr}")
                return False
        
        except Exception as e:
            self._log_error(f"jarsigner error: {e}")
            return False
    
    def _create_debug_keystore(self, keystore_path: str, password: str, alias: str) -> bool:
        """
        Create a debug keystore using keytool
        
        Args:
            keystore_path: Path where keystore should be created
            password: Password for keystore
            alias: Key alias
            
        Returns:
            True if keystore created successfully
        """
        try:
            self._log_info(f"Creating debug keystore: {keystore_path}")
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(keystore_path), exist_ok=True)
            
            # Find keytool - try multiple locations
            keytool_cmd = self._find_keytool()
            if not keytool_cmd:
                self._log_error("keytool not found. Please install Java JDK and add to PATH.")
                return False
            
            cmd = [
                keytool_cmd,
                '-genkeypair',
                '-v',
                '-keystore', keystore_path,
                '-alias', alias,
                '-keyalg', 'RSA',
                '-keysize', '2048',
                '-validity', '10000',
                '-storepass', password,
                '-keypass', password,
                '-dname', 'CN=AutoModRenpy, OU=Development, O=AutoModRenpy, L=Unknown, S=Unknown, C=US'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self._log_success("Debug keystore created successfully")
                return True
            else:
                self._log_error(f"Failed to create keystore: {result.stderr}")
                return False
        
        except Exception as e:
            self._log_error(f"Error creating keystore: {e}")
            return False
    
    def _resolve_path(self, path: str) -> str:
        """
        Resolve relative path to absolute path based on script directory
        
        Args:
            path: Path to resolve (relative or absolute)
            
        Returns:
            Absolute path
        """
        if os.path.isabs(path):
            return path
        
        # If relative, resolve relative to the directory containing this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)  # Go up to repo root
        resolved = os.path.join(parent_dir, path)
        return os.path.abspath(resolved)
    
    def _find_keytool(self) -> Optional[str]:
        """
        Find keytool executable in common Java installation locations
        
        Returns:
            Path to keytool or None if not found
        """
        # Try PATH first
        if shutil.which('keytool'):
            return 'keytool'
        
        # Common Java installation paths on Windows
        common_paths = [
            r"C:\Program Files\Java\jdk-11\bin\keytool.exe",
            r"C:\Program Files\Java\jdk-17\bin\keytool.exe",
            r"C:\Program Files\Java\jdk-21\bin\keytool.exe",
            r"C:\Program Files\Java\jdk1.8.0_*\bin\keytool.exe",
            r"C:\Program Files (x86)\Java\jdk-11\bin\keytool.exe",
        ]
        
        for path_pattern in common_paths:
            if '*' in path_pattern:
                # Handle wildcard patterns
                import glob
                matches = glob.glob(path_pattern)
                if matches and os.path.exists(matches[0]):
                    return matches[0]
            elif os.path.exists(path_pattern):
                return path_pattern
        
        # Last resort: search in Program Files
        for base_dir in [r"C:\Program Files\Java", r"C:\Program Files (x86)\Java"]:
            if os.path.exists(base_dir):
                for root, dirs, files in os.walk(base_dir):
                    if 'keytool.exe' in files:
                        return os.path.join(root, 'keytool.exe')
        
        return None
    
    def _check_apktool(self) -> bool:
        """Check if apktool is available"""
        # Temporarily disabled due to hanging issues - force ZIP extraction
        return False
        # return os.path.exists(self.apktool_path) or shutil.which('apktool') is not None
    
    def _log_info(self, message: str):
        """Log info message"""
        if self.logger:
            self.logger.info(message)
    
    def _log_success(self, message: str):
        """Log success message"""
        if self.logger:
            self.logger.success(message)
    
    def _log_warning(self, message: str):
        """Log warning message"""
        if self.logger:
            self.logger.warning(message)
    
    def _log_error(self, message: str):
        """Log error message"""
        if self.logger:
            self.logger.error(message)
