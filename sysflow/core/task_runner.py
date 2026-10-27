"""
Sandboxed Task Runner with Hard Timeouts (SysFlow Pro Core).
Enforces non-interactive execution, captures stdout/stderr, and prevents terminal freezes.
"""
import os
import subprocess
import time
from typing import Dict, Any, Optional

class TaskRunner:
    @staticmethod
    def run_command(command: str, timeout_sec: int = 30, cwd: Optional[str] = None, max_timeout: int = 300) -> Dict[str, Any]:
        timeout = min(max_timeout, max(1, timeout_sec))
        work_dir = cwd if cwd and os.path.isdir(cwd) else os.getcwd()

        # Non-interactive environment to prevent pager locks
        env = os.environ.copy()
        env["PAGER"] = "cat"
        env["DEBIAN_FRONTEND"] = "noninteractive"
        env["TERM"] = "dumb"
        env["GIT_PAGER"] = "cat"

        start_time = time.time()
        try:
            res = subprocess.run(
                command,
                shell=True,
                cwd=work_dir,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "success": res.returncode == 0,
                "exit_code": res.returncode,
                "command": command,
                "stdout": res.stdout[:50000],  # Bound output to 50KB
                "stderr": res.stderr[:20000],
                "execution_time_ms": elapsed_ms,
                "timed_out": False
            }
        except subprocess.TimeoutExpired:
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "success": False,
                "exit_code": -1,
                "command": command,
                "error": f"Execution timed out after {timeout} seconds. Process was terminated to prevent terminal freeze.",
                "execution_time_ms": elapsed_ms,
                "timed_out": True
            }
        except Exception as e:
            return {
                "success": False,
                "exit_code": -1,
                "command": command,
                "error": f"Task execution exception: {str(e)}",
                "timed_out": False
            }
