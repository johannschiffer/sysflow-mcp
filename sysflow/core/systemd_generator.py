"""
Systemd Unit Generator & Validator (SysFlow Pro Core).
Creates validated .service and .timer units for background tasks and automated cron schedules.
"""
from typing import Dict, Any, Optional

class SystemdGenerator:
    @staticmethod
    def generate_unit(service_name: str, exec_start: str, cwd: Optional[str] = None, 
                      timer_schedule: Optional[str] = None, restart_policy: str = "no") -> Dict[str, Any]:
        """
        Generates service and timer configuration strings.
        timer_schedule can be OnCalendar format (e.g. '*-*-* 00,06,12,18:00:00' or 'hourly', 'daily')
        or interval format (e.g. '6h', '10min').
        """
        clean_name = service_name.replace(".service", "").replace(".timer", "")
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
            if any(unit in timer_schedule for unit in ["min", "h", "s"]):
                timer_directive = f"OnUnitActiveSec={timer_schedule}"
            else:
                timer_directive = f"OnCalendar={timer_schedule}"

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
            "install_path_user": f"~/.config/systemd/user/{clean_name}.service"
        }
