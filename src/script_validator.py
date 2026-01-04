"""
Script Validator Module
Lightweight validation for Renpy .rpy script files
"""
import os
import re
from typing import List, Dict, Tuple


class ValidationIssue:
    """Represents a validation issue in a script"""
    
    def __init__(self, line_number: int, severity: str, message: str):
        self.line_number = line_number
        self.severity = severity  # 'error', 'warning', 'info'
        self.message = message
    
    def __repr__(self):
        return f"Line {self.line_number} [{self.severity.upper()}]: {self.message}"


class ScriptValidator:
    """Lightweight validator for Renpy script files"""
    
    def __init__(self, logger=None):
        self.logger = logger
        self.indent_size = 4  # Standard Python/Renpy indentation
    
    def validate_script(self, script_path: str) -> Tuple[bool, List[ValidationIssue]]:
        """
        Validate a Renpy script file
        
        Args:
            script_path: Path to .rpy file
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        if not os.path.exists(script_path):
            issues.append(ValidationIssue(0, 'error', f"File not found: {script_path}"))
            return False, issues
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Check indentation consistency
            indent_issues = self._check_indentation(lines)
            issues.extend(indent_issues)
            
            # Check basic syntax structure
            structure_issues = self._check_structure(lines)
            issues.extend(structure_issues)
            
            # Check for common mistakes
            common_issues = self._check_common_mistakes(lines)
            issues.extend(common_issues)
            
            # Determine if valid (only warnings/info, no errors)
            has_errors = any(issue.severity == 'error' for issue in issues)
            is_valid = not has_errors
            
            if issues:
                if has_errors:
                    self._log_error(f"Validation failed for {os.path.basename(script_path)}: {len(issues)} issues found")
                else:
                    self._log_warning(f"Validation passed with warnings for {os.path.basename(script_path)}: {len(issues)} issues found")
            else:
                self._log_success(f"Validation passed for {os.path.basename(script_path)}")
            
            return is_valid, issues
        
        except Exception as e:
            issues.append(ValidationIssue(0, 'error', f"Error reading file: {e}"))
            return False, issues
    
    def _check_indentation(self, lines: List[str]) -> List[ValidationIssue]:
        """Check indentation consistency"""
        issues = []
        indent_stack = [0]
        
        for line_num, line in enumerate(lines, start=1):
            # Skip empty lines and comments
            stripped = line.lstrip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # Calculate indentation
            indent = len(line) - len(stripped)
            
            # Check if indentation is multiple of indent_size
            if indent % self.indent_size != 0:
                issues.append(ValidationIssue(
                    line_num,
                    'warning',
                    f"Indentation is {indent} spaces (should be multiple of {self.indent_size})"
                ))
            
            # Check for tabs
            if '\t' in line[:indent]:
                issues.append(ValidationIssue(
                    line_num,
                    'warning',
                    "Contains tabs (should use spaces for indentation)"
                ))
        
        return issues
    
    def _check_structure(self, lines: List[str]) -> List[ValidationIssue]:
        """Check basic code structure"""
        issues = []
        block_stack = []
        
        # Keywords that start blocks
        block_starters = ['label', 'if', 'elif', 'else', 'while', 'for', 'menu', 'init', 'screen', 'style']
        
        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()
            
            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                continue
            
            # Check for block starters
            first_word = stripped.split()[0] if stripped.split() else ''
            
            if first_word in block_starters:
                # Block should end with ':'
                if not stripped.endswith(':'):
                    issues.append(ValidationIssue(
                        line_num,
                        'error',
                        f"Block statement '{first_word}' should end with ':'"
                    ))
                else:
                    block_stack.append((line_num, first_word))
            
            # Check for common Renpy statements
            if first_word in ['jump', 'call'] and len(stripped.split()) < 2:
                issues.append(ValidationIssue(
                    line_num,
                    'error',
                    f"'{first_word}' statement requires a label name"
                ))
        
        return issues
    
    def _check_common_mistakes(self, lines: List[str]) -> List[ValidationIssue]:
        """Check for common mistakes in Renpy scripts"""
        issues = []
        
        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()
            
            # Skip comments
            if stripped.startswith('#'):
                continue
            
            # Check for unclosed strings
            if self._has_unclosed_string(stripped):
                issues.append(ValidationIssue(
                    line_num,
                    'warning',
                    "Possible unclosed string"
                ))
            
            # Check for unclosed parentheses/brackets
            if self._has_unclosed_brackets(stripped):
                issues.append(ValidationIssue(
                    line_num,
                    'warning',
                    "Possible unclosed parentheses or brackets"
                ))
            
            # Check for common typos in Renpy keywords
            if re.search(r'\bjump\s+if\b', stripped):
                issues.append(ValidationIssue(
                    line_num,
                    'warning',
                    "Did you mean 'if' instead of 'jump if'?"
                ))
        
        return issues
    
    def _has_unclosed_string(self, line: str) -> bool:
        """Check if line has unclosed string (simple check)"""
        # Remove escaped quotes
        line = line.replace('\\"', '').replace("\\'", '')
        
        # Count unescaped quotes
        double_quotes = line.count('"')
        single_quotes = line.count("'")
        
        # If odd number of quotes, likely unclosed
        return (double_quotes % 2 != 0) or (single_quotes % 2 != 0)
    
    def _has_unclosed_brackets(self, line: str) -> bool:
        """Check if line has unclosed brackets/parentheses"""
        open_count = line.count('(') + line.count('[') + line.count('{')
        close_count = line.count(')') + line.count(']') + line.count('}')
        
        return open_count != close_count
    
    def validate_multiple_scripts(self, script_paths: List[str]) -> Dict[str, Tuple[bool, List[ValidationIssue]]]:
        """
        Validate multiple script files
        
        Args:
            script_paths: List of paths to .rpy files
            
        Returns:
            Dictionary mapping file paths to validation results
        """
        results = {}
        
        for script_path in script_paths:
            is_valid, issues = self.validate_script(script_path)
            results[script_path] = (is_valid, issues)
        
        return results
    
    def get_validation_summary(self, results: Dict[str, Tuple[bool, List[ValidationIssue]]]) -> Dict[str, int]:
        """
        Get summary statistics from validation results
        
        Args:
            results: Dictionary of validation results
            
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            'total_files': len(results),
            'valid_files': 0,
            'files_with_errors': 0,
            'files_with_warnings': 0,
            'total_errors': 0,
            'total_warnings': 0
        }
        
        for file_path, (is_valid, issues) in results.items():
            if is_valid:
                summary['valid_files'] += 1
            
            has_errors = any(issue.severity == 'error' for issue in issues)
            has_warnings = any(issue.severity == 'warning' for issue in issues)
            
            if has_errors:
                summary['files_with_errors'] += 1
            if has_warnings:
                summary['files_with_warnings'] += 1
            
            summary['total_errors'] += sum(1 for issue in issues if issue.severity == 'error')
            summary['total_warnings'] += sum(1 for issue in issues if issue.severity == 'warning')
        
        return summary
    
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
