"""
Listening Port and Socket Conflict Auditor.
Scans active listening network ports to diagnose binding conflicts and unauthorized listeners without root.
"""
import os
import subprocess
from typing import List, Dict, Any

class PortAuditor:
    @staticmethod
    def audit_listening_ports() -> Dict[str, Any]:
        """Audits local TCP listening ports using ss or /proc/net/tcp."""
        ports: List[Dict[str, Any]] = []

        # Attempt standard ss command first
        try:
            res = subprocess.run(
                ["ss", "-tlnH"],
                capture_output=True,
                text=True,
                timeout=4
            )
            if res.returncode == 0:
                for line in res.stdout.strip().split("\n"):
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if len(parts) >= 4:
                        state = parts[0]
                        local_addr = parts[3]
                        port_str = local_addr.rsplit(":", 1)[-1]
                        try:
                            port_num = int(port_str)
                            ports.append({
                                "state": state,
                                "address": local_addr,
                                "port": port_num
                            })
                        except ValueError:
                            continue
                return {
                    "success": True,
                    "count": len(ports),
                    "listening_ports": ports
                }
        except Exception:
            pass

        # Fallback to parsing /proc/net/tcp
        if os.path.exists("/proc/net/tcp"):
            try:
                with open("/proc/net/tcp", "r") as f:
                    lines = f.readlines()[1:]  # Skip header
                    for line in lines:
                        parts = line.strip().split()
                        if len(parts) >= 4:
                            state = parts[3]
                            # 0A is TCP_LISTEN in hex
                            if state == "0A":
                                local_hex = parts[1]
                                port_hex = local_hex.split(":")[1]
                                port_num = int(port_hex, 16)
                                ports.append({
                                    "state": "LISTEN",
                                    "address": f"0.0.0.0:{port_num}",
                                    "port": port_num
                                })
                return {
                    "success": True,
                    "count": len(ports),
                    "listening_ports": ports
                }
            except Exception as e:
                return {"success": False, "error": f"Error auditing ports: {str(e)}"}

        return {"success": True, "count": 0, "listening_ports": []}
