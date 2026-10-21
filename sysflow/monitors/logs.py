"""
Safe Log File Reader & Tailer.
Tails recent log entries efficiently, filters by regex patterns, and guards against binary files.
"""
import os
import re
from typing import Dict, Any, List, Optional

class LogTailer:
    @staticmethod
    def is_binary_file(filepath: str, check_bytes: int = 1024) -> bool:
        """Heuristic check to prevent reading binary files."""
        try:
            with open(filepath, "rb") as f:
                chunk = f.read(check_bytes)
                return b"\x00" in chunk
        except Exception:
            return True

    @classmethod
    def tail(cls, filepath: str, lines: int = 50, pattern: Optional[str] = None, max_lines: int = 500) -> Dict[str, Any]:
        target_path = os.path.abspath(filepath)
        if not os.path.isfile(target_path):
            return {
                "success": False,
                "error": f"File does not exist or is not a regular file: '{target_path}'"
            }

        if cls.is_binary_file(target_path):
            return {
                "success": False,
                "error": f"Target file appears to be a binary file: '{target_path}'"
            }

        capped_lines = min(max_lines, max(1, lines))
        file_size = os.path.getsize(target_path)

        # Efficiently read from end of file for large files
        chunk_size = 8192
        collected_lines: List[str] = []

        try:
            with open(target_path, "r", encoding="utf-8", errors="replace") as f:
                if file_size < 100 * 1024:  # Under 100KB, read directly
                    all_lines = f.readlines()
                    collected_lines = all_lines[-capped_lines:]
                else:
                    # Seek backwards from end
                    f.seek(max(0, file_size - (capped_lines * 500)))
                    f.readline()  # Discard partial line
                    collected_lines = f.readlines()[-capped_lines:]
        except Exception as e:
            return {"success": False, "error": f"Error reading log file: {str(e)}"}

        clean_lines = [l.rstrip("\r\n") for l in collected_lines]

        # Optional regex filter
        if pattern:
            try:
                regex = re.compile(pattern, re.IGNORECASE)
                clean_lines = [l for l in clean_lines if regex.search(l)]
            except re.error as e:
                return {"success": False, "error": f"Invalid regex pattern: {str(e)}"}

        return {
            "success": True,
            "filepath": target_path,
            "file_size_bytes": file_size,
            "lines_returned": len(clean_lines),
            "lines": clean_lines
        }
