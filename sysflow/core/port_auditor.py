"""
Listening Port and Socket Conflict Auditor.
Scans active listening network ports via ss or /proc/net/tcp{,6} without root.
"""

import ipaddress
import os
import subprocess
from typing import List, Dict, Any


def _decode_proc_ip(hex_ip: str, is_ipv6: bool) -> str:
    try:
        if not is_ipv6 and len(hex_ip) == 8:
            raw = bytes.fromhex(hex_ip)[::-1]
            return str(ipaddress.IPv4Address(raw))
        if is_ipv6 and len(hex_ip) == 32:
            words = [bytes.fromhex(hex_ip[i : i + 8])[::-1] for i in range(0, 32, 8)]
            return f"[{ipaddress.IPv6Address(b''.join(words))}]"
    except Exception:
        pass
    return "[::]" if is_ipv6 else "0.0.0.0"


class PortAuditor:
    @staticmethod
    def audit_listening_ports() -> Dict[str, Any]:
        """Audits local TCP listening ports using ss or /proc/net/tcp{,6}."""
        ports: List[Dict[str, Any]] = []

        try:
            res = subprocess.run(
                ["ss", "-tlnH"],
                capture_output=True,
                text=True,
                timeout=4,
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
                            ports.append(
                                {
                                    "state": state,
                                    "address": local_addr,
                                    "port": port_num,
                                }
                            )
                        except ValueError:
                            continue
                return {
                    "success": True,
                    "count": len(ports),
                    "listening_ports": ports,
                }
        except Exception:
            pass

        proc_root = os.getenv("SYSFLOW_PROC_DIR") or ("/host-proc" if os.path.isdir("/host-proc/net") else "/proc")
        proc_targets = [
            (os.path.join(proc_root, "net", "tcp"), False),
            (os.path.join(proc_root, "net", "tcp6"), True),
        ]
        found_any = False
        try:
            for tcp_path, is_v6 in proc_targets:
                if not os.path.exists(tcp_path):
                    continue
                found_any = True
                with open(tcp_path, "r", encoding="utf-8", errors="replace") as f:
                    for line in f.readlines()[1:]:
                        parts = line.strip().split()
                        if len(parts) >= 4 and parts[3] == "0A":
                            ip_hex, port_hex = parts[1].split(":", 1)
                            port_num = int(port_hex, 16)
                            host_str = _decode_proc_ip(ip_hex, is_v6)
                            ports.append(
                                {
                                    "state": "LISTEN",
                                    "address": f"{host_str}:{port_num}",
                                    "port": port_num,
                                }
                            )
            if found_any:
                return {
                    "success": True,
                    "count": len(ports),
                    "listening_ports": ports,
                }
        except Exception as e:
            return {"success": False, "error": f"Error auditing ports: {str(e)}"}

        return {"success": True, "count": 0, "listening_ports": []}
