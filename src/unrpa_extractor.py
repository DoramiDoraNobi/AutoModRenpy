"""
UnRPA Extraction Module
Handles extraction and analysis of Renpy RPA archives
"""
import os
import pickle
import zlib
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class UnRPAExtractor:
    """Extract and analyze Renpy RPA archives"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.supported_versions = [2, 3, 4]  # RPA-2.0, RPA-3.0, RPA-4.0
    
    def extract_archive(self, rpa_path: str, output_dir: str, file_list: Optional[List[str]] = None) -> bool:
        """
        Extract RPA archive to output directory
        
        Args:
            rpa_path: Path to RPA file
            output_dir: Directory to extract files to
            file_list: Optional list of specific files to extract (None = extract all)
            
        Returns:
            True if extraction successful
        """
        try:
            self._log_info(f"Extracting RPA archive: {os.path.basename(rpa_path)}")
            
            # Read archive index
            version, index = self._read_archive_index(rpa_path)
            
            if not index:
                self._log_error(f"Failed to read archive index")
                return False
            
            self._log_info(f"Archive version: RPA-{version}.0")
            self._log_info(f"Total files in archive: {len(index)}")
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Extract files
            extracted_count = 0
            with open(rpa_path, 'rb') as archive:
                for filename, file_data in index.items():
                    # Check if we should extract this file
                    if file_list is not None and filename not in file_list:
                        continue
                    
                    # Extract file
                    if self._extract_file(archive, filename, file_data, output_dir):
                        extracted_count += 1
            
            self._log_success(f"Extracted {extracted_count} files to {output_dir}")
            return True
        
        except Exception as e:
            self._log_error(f"Error extracting archive: {e}")
            return False
    
    def list_archive_contents(self, rpa_path: str) -> List[Dict[str, any]]:
        """
        List contents of RPA archive without extracting
        
        Args:
            rpa_path: Path to RPA file
            
        Returns:
            List of file info dictionaries
        """
        try:
            version, index = self._read_archive_index(rpa_path)
            
            if not index:
                return []
            
            file_list = []
            for filename, file_data in index.items():
                offset, length = file_data[0], file_data[1]
                
                file_info = {
                    'name': filename,
                    'size': length,
                    'offset': offset,
                    'size_formatted': self._format_bytes(length)
                }
                file_list.append(file_info)
            
            # Sort by filename
            file_list.sort(key=lambda x: x['name'])
            
            return file_list
        
        except Exception as e:
            self._log_error(f"Error listing archive contents: {e}")
            return []
    
    def get_archive_info(self, rpa_path: str) -> Dict[str, any]:
        """
        Get information about RPA archive
        
        Args:
            rpa_path: Path to RPA file
            
        Returns:
            Dictionary with archive information
        """
        try:
            version, index = self._read_archive_index(rpa_path)
            
            if not index:
                return {}
            
            total_size = sum(file_data[1] for file_data in index.values())
            
            # Categorize files by type
            file_types = {}
            for filename in index.keys():
                ext = Path(filename).suffix.lower()
                if not ext:
                    ext = 'no_extension'
                file_types[ext] = file_types.get(ext, 0) + 1
            
            return {
                'version': f"RPA-{version}.0",
                'file_count': len(index),
                'total_size': total_size,
                'total_size_formatted': self._format_bytes(total_size),
                'file_types': file_types,
                'archive_size': os.path.getsize(rpa_path),
                'archive_size_formatted': self._format_bytes(os.path.getsize(rpa_path))
            }
        
        except Exception as e:
            self._log_error(f"Error getting archive info: {e}")
            return {}
    
    def _read_archive_index(self, rpa_path: str) -> Tuple[int, Optional[Dict]]:
        """
        Read RPA archive index
        
        Args:
            rpa_path: Path to RPA file
            
        Returns:
            Tuple of (version, index_dict) or (0, None) if failed
        """
        try:
            with open(rpa_path, 'rb') as f:
                # Read header
                header = f.read(34)  # "RPA-3.0 " is 8 bytes, followed by hex offset
                
                # Detect version
                if header.startswith(b'RPA-4.0 '):
                    version = 4
                    offset_str = header[8:].split(b'\n')[0]
                    index_offset = int(offset_str, 16)
                elif header.startswith(b'RPA-3.0 '):
                    version = 3
                    offset_str = header[8:].split(b'\n')[0]
                    index_offset = int(offset_str, 16)
                elif header.startswith(b'RPA-2.0 '):
                    version = 2
                    offset_str = header[8:].split(b'\n')[0]
                    index_offset = int(offset_str, 16)
                else:
                    self._log_error(f"Unsupported RPA version or corrupted file")
                    return 0, None
                
                # Read index
                f.seek(index_offset)
                index_data = f.read()
                
                # Decompress and unpickle index
                try:
                    index = pickle.loads(zlib.decompress(index_data))
                except:
                    # Try without decompression (some versions)
                    index = pickle.loads(index_data)
                
                return version, index
        
        except Exception as e:
            self._log_error(f"Error reading archive index: {e}")
            return 0, None
    
    def _extract_file(self, archive, filename: str, file_data: tuple, output_dir: str) -> bool:
        """
        Extract single file from archive
        
        Args:
            archive: Open file object for RPA archive
            filename: Name of file to extract
            file_data: Tuple of (offset, length, prefix) from index
            output_dir: Directory to extract to
            
        Returns:
            True if extraction successful
        """
        try:
            offset, length = file_data[0], file_data[1]
            prefix = file_data[2] if len(file_data) > 2 else b''
            
            # Read file data
            archive.seek(offset)
            file_content = archive.read(length)
            
            # Decode with prefix if present (obfuscation)
            if prefix:
                # XOR deobfuscation with prefix
                file_content = bytes(b ^ prefix[i % len(prefix)] for i, b in enumerate(file_content))
            
            # Create output path
            output_path = os.path.join(output_dir, filename.replace('/', os.sep))
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write file
            with open(output_path, 'wb') as out_file:
                out_file.write(file_content)
            
            return True
        
        except Exception as e:
            self._log_error(f"Error extracting file {filename}: {e}")
            return False
    
    def _format_bytes(self, bytes_size: int) -> str:
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"
    
    def _log_info(self, message: str):
        """Log info message"""
        if self.logger:
            self.logger.info(message)
    
    def _log_success(self, message: str):
        """Log success message"""
        if self.logger:
            self.logger.success(message)
    
    def _log_error(self, message: str):
        """Log error message"""
        if self.logger:
            self.logger.error(message)
