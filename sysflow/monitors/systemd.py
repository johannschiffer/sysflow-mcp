"""
Systemd User Service & Timer Inspector.
Inspects systemd --user units, detects failed services, and monitors timers without root.
"""
import subprocess
from typing import Dict, Any, List

class SystemdInspector:
    @staticmethod
    def list_user_units(failed_only: bool = False) -> Dict[str, Any]:
        cmd = ["systemctl", "--user", "list-units", "--type=service", "--no-pager", "--no-legend"]
        if failed_only:
            cmd.append("--state=failed")

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            units: List[Dict[str, str]] = []

            for line in res.stdout.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                parts = line.split(maxsplit=4)
                if len(parts) >= 4:
                    units.append({
                        "unit": parts[0].replace("●", "").strip(),
                        "load": parts[1],
                        "active": parts[2],
                        "sub": parts[3],
                        "description": parts[4] if len(parts) > 4 else ""
                    })

            return {
                "success": True,
                "count": len(units),
                "failed_only": failed_only,
                "units": units
            }
        except Exception as e:
            return {"success": False, "error": f"Error querying systemctl: {str(e)}"}

    @staticmethod
    def list_user_timers() -> Dict[str, Any]:
        cmd = ["systemctl", "--user", "list-timers", "--no-pager", "--no-legend"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            timers = []
            for line in res.stdout.strip().split("\n"):
                line = line.strip()
                if not line:
                    continue
                timers.append(line)
            return {"success": True, "count": len(timers), "timers": timers}
        except Exception as e:
            return {"success": False, "error": f"Error querying systemd timers: {str(e)}"}
