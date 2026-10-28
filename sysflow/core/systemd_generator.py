"""
Systemd Unit Generator & Validator.
Creates validated .service and .timer units for background tasks and scheduled jobs.
"""

import re
from typing import Dict, Any, Optional

_SERVICE_NAME_RE = re.compile(r"^[A-Za-z0-9_.@-]{1,128}$")
_INTERVAL_RE = re.compile(
    r"^\d+\s*(us|ms|s|sec|seconds|m|min|minutes|h|hr|hours|d|days|w|weeks)$",
    re.IGNORECASE,
)


def _reject_control_chars(label: str, val: Optional[str]) -> None:
    if val is not None and ("\n" in val or "\r" in val or "\x00" in val):
        raise ValueError(f"Invalid control character in '{label}'.")


class SystemdGenerator:
    @staticmethod
    def generate_unit(
        service_name: str,
        exec_start: str,
        cwd: Optional[str] = None,
        timer_schedule: Optional[str] = None,
        restart_policy: str = "no",
    ) -> Dict[str, Any]:
        _reject_control_chars("service_name", service_name)
        _reject_control_chars("exec_start", exec_start)
        _reject_control_chars("cwd", cwd)
        _reject_control_chars("timer_schedule", timer_schedule)
        _reject_control_chars("restart_policy", restart_policy)

        clean_name = service_name.strip()
        if clean_name.endswith(".service"):
            clean_name = clean_name[: -len(".service")]
        elif clean_name.endswith(".timer"):
            clean_name = clean_name[: -len(".timer")]

        if not _SERVICE_NAME_RE.match(clean_name) or ".." in clean_name:
            raise ValueError(f"Invalid systemd unit name: '{service_name}'")
        if not exec_start or not exec_start.strip():
            raise ValueError("exec_start must not be empty.")

        work_dir = cwd or "/tmp"

        service_content = f"""[Unit]
Description=SysFlow Managed Service - {clean_name}
After=network.target

[Service]
Type=oneshot
WorkingDirectory={work_dir}
ExecStart={exec_start}
Restart={restart_policy}
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
"""

        timer_content = None
        if timer_schedule:
            sched = timer_schedule.strip()
            if _INTERVAL_RE.match(sched):
                timer_directive = f"OnUnitActiveSec={sched}"
            else:
                timer_directive = f"OnCalendar={sched}"

            timer_content = f"""[Unit]
Description=SysFlow Schedule Timer for {clean_name}
RefuseManualStart=no
RefuseManualStop=no

[Timer]
OnBootSec=5min
{timer_directive}
Persistent=true

[Install]
WantedBy=timers.target
"""

        return {
            "service_filename": f"{clean_name}.service",
            "service_content": service_content.strip(),
            "has_timer": bool(timer_content),
            "timer_filename": f"{clean_name}.timer" if timer_content else None,
            "timer_content": timer_content.strip() if timer_content else None,
            "install_path_user": f"~/.config/systemd/user/{clean_name}.service",
        }
