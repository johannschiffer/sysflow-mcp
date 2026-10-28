"""
Safe Log File Reader & Tailer.
Enforces path containment, blocks sensitive dotfiles/credentials, guards against binary files,
and reads recent matching lines from the end of large files.
"""

import os
import re
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

_DENIED_BASENAMES = {
    ".env",
    "shadow",
    "gshadow",
    "passwd",
    "sudoers",
    "id_rsa",
    "id_ed25519",
    "id_ecdsa",
    "authorized_keys",
    "known_hosts",
    "credentials",
    "cookies.sqlite",
}
_DENIED_PARTS = {".ssh", ".gnupg", ".aws", ".kube", ".docker"}


def _allowed_roots() -> List[Path]:
    raw = os.getenv("SYSFLOW_LOG_DIRS", "")
    if raw.strip():
        roots = [Path(p).resolve() for p in raw.split(os.pathsep) if p.strip()]
    else:
        roots = [
            Path("/var/log").resolve(),
            Path("/tmp").resolve(),
            Path(tempfile.gettempdir()).resolve(),
            Path(os.getcwd()).resolve(),
        ]
    return roots


def _is_path_allowed(resolved: Path) -> Tuple[bool, str]:  # type: ignore[name-defined]
    name_lower = resolved.name.lower()
    if name_lower in _DENIED_BASENAMES or name_lower.startswith(".env."):
        return False, f"Access denied to sensitive file: '{resolved.name}'"
    parts_set = {p.lower() for p in resolved.parts}
    if parts_set & _DENIED_PARTS:
        return False, "Access denied to protected credential directory."
    if len(resolved.parts) >= 2 and resolved.parts[-2] == ".git" and resolved.name == "config":
        return False, "Access denied to .git/config."

    for root in _allowed_roots():
        try:
            if resolved.is_relative_to(root):
                return True, ""
        except ValueError:
            continue
    return False, f"File path '{resolved}' is outside allowed log directories (configure SYSFLOW_LOG_DIRS)."


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
    def tail(
        cls,
        filepath: str,
        lines: int = 50,
        pattern: Optional[str] = None,
        max_lines: int = 500,
    ) -> Dict[str, Any]:
        if not filepath or not str(filepath).strip():
            return {"success": False, "error": "Empty filepath provided."}

        resolved = Path(filepath).resolve()
        target_path = str(resolved)

        allowed, reason = _is_path_allowed(resolved)
        if not allowed:
            return {"success": False, "error": reason}

        if not resolved.is_file():
            return {
                "success": False,
                "error": f"File does not exist or is not a regular file: '{target_path}'",
            }

        if cls.is_binary_file(target_path):
            return {
                "success": False,
                "error": f"Target file appears to be a binary file: '{target_path}'",
            }

        regex = None
        if pattern:
            if len(pattern) > 256:
                return {"success": False, "error": "Regex pattern exceeds 256-character safety bound."}
            try:
                regex = re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                return {"success": False, "error": f"Invalid regex pattern: {str(e)}"}

        capped_lines = min(max_lines, max(1, int(lines)))
        file_size = os.path.getsize(target_path)
        chunk_size = 8192
        max_scan_bytes = 2 * 1024 * 1024

        try:
            with open(target_path, "rb") as f:
                pos = file_size
                scanned = 0
                buffer = b""
                matched: List[str] = []

                while pos > 0 and len(matched) < capped_lines and scanned < max_scan_bytes:
                    read_len = min(chunk_size, pos)
                    pos -= read_len
                    scanned += read_len
                    f.seek(pos)
                    buffer = f.read(read_len) + buffer
                    parts = buffer.split(b"\n")
                    if pos > 0:
                        buffer = parts[0]
                        complete = parts[1:]
                    else:
                        buffer = b""
                        complete = parts

                    # Drop trailing empty line from final newline
                    if complete and complete[-1] == b"" and scanned == read_len:
                        complete = complete[:-1]

                    for raw_line in reversed(complete):
                        decoded = raw_line.decode("utf-8", errors="replace").rstrip("\r")
                        if regex is None or regex.search(decoded):
                            matched.append(decoded)
                            if len(matched) >= capped_lines:
                                break

                clean_lines = list(reversed(matched))
        except Exception as e:
            return {"success": False, "error": f"Error reading log file: {str(e)}"}

        return {
            "success": True,
            "filepath": target_path,
            "file_size_bytes": file_size,
            "lines_returned": len(clean_lines),
            "lines": clean_lines,
        }
