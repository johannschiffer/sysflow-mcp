"""
Timeout-Bounded Task Runner.
Executes argv commands without shell interpolation by default, scrubs secret environment
variables, and terminates process groups cleanly upon timeout.
"""

import os
import re
import shlex
import signal
import subprocess
import time
from typing import Dict, Any, Optional

_SECRET_ENV_RE = re.compile(r"(TOKEN|SECRET|PASSWORD|PASSWD|API_KEY|PRIVATE_KEY|CREDENTIAL|ACCESS_KEY)", re.IGNORECASE)
_SHELL_META_RE = re.compile(r"[;&|`$><\n]")


def _scrubbed_env() -> Dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not _SECRET_ENV_RE.search(k)}
    env["PAGER"] = "cat"
    env["DEBIAN_FRONTEND"] = "noninteractive"
    env["TERM"] = "dumb"
    env["GIT_PAGER"] = "cat"
    return env


class TaskRunner:
    @staticmethod
    def run_command(
        command: str,
        timeout_sec: int = 30,
        cwd: Optional[str] = None,
        max_timeout: int = 300,
    ) -> Dict[str, Any]:
        if not isinstance(command, str) or not command.strip():
            return {
                "success": False,
                "exit_code": -1,
                "command": command,
                "error": "Empty command provided.",
                "timed_out": False,
            }

        allow_shell = os.getenv("SYSFLOW_ALLOW_SHELL", "0") == "1"
        if not allow_shell and _SHELL_META_RE.search(command):
            return {
                "success": False,
                "exit_code": -1,
                "command": command,
                "error": "Shell metacharacters and command chaining are disabled by default (set SYSFLOW_ALLOW_SHELL=1 to override).",
                "timed_out": False,
            }

        try:
            cmd_target = command if allow_shell else shlex.split(command)
        except ValueError as parse_err:
            return {
                "success": False,
                "exit_code": -1,
                "command": command,
                "error": f"Invalid command quoting: {parse_err}",
                "timed_out": False,
            }

        if not cmd_target:
            return {
                "success": False,
                "exit_code": -1,
                "command": command,
                "error": "Empty command provided.",
                "timed_out": False,
            }

        timeout = min(max_timeout, max(1, int(timeout_sec)))
        work_dir = cwd if cwd and os.path.isdir(cwd) else os.getcwd()
        env = _scrubbed_env()

        start_time = time.time()
        proc = None
        try:
            proc = subprocess.Popen(
                cmd_target,
                shell=allow_shell,
                cwd=work_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                start_new_session=True,
            )
            stdout, stderr = proc.communicate(timeout=timeout)
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "success": proc.returncode == 0,
                "exit_code": proc.returncode,
                "command": command,
                "stdout": (stdout or "")[:50000],
                "stderr": (stderr or "")[:20000],
                "execution_time_ms": elapsed_ms,
                "timed_out": False,
            }
        except subprocess.TimeoutExpired:
            if proc is not None:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except OSError:
                    proc.kill()
                try:
                    proc.communicate(timeout=2)
                except Exception:
                    pass
            elapsed_ms = round((time.time() - start_time) * 1000, 2)
            return {
                "success": False,
                "exit_code": -1,
                "command": command,
                "error": f"Execution timed out after {timeout} seconds. Process was terminated to prevent terminal freeze.",
                "execution_time_ms": elapsed_ms,
                "timed_out": True,
            }
        except Exception as e:
            return {
                "success": False,
                "exit_code": -1,
                "command": command,
                "error": f"Task execution exception: {str(e)}",
                "timed_out": False,
            }
