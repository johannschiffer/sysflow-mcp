"""
System Resource Monitor.
Gathers CPU load average, RAM utilization, disk usage, and host details without root.
"""
import os
import shutil
import platform
from typing import Dict, Any

class ResourceMonitor:
    @staticmethod
    def get_system_stats() -> Dict[str, Any]:
        # 1. CPU
        cpu_count = os.cpu_count() or 1
        load_1, load_5, load_15 = (0.0, 0.0, 0.0)
        try:
            load_1, load_5, load_15 = os.getloadavg()
        except (AttributeError, OSError):
            pass

        # 2. Disk
        disk_total, disk_used, disk_free = (0, 0, 0)
        disk_pct = 0.0
        try:
            usage = shutil.disk_usage("/")
            disk_total = round(usage.total / (1024 ** 3), 2)  # GB
            disk_used = round(usage.used / (1024 ** 3), 2)
            disk_free = round(usage.free / (1024 ** 3), 2)
            disk_pct = round((usage.used / usage.total) * 100, 1)
        except Exception:
            pass

        # 3. RAM (Linux /proc/meminfo)
        mem_total_mb = 0
        mem_avail_mb = 0
        mem_pct = 0.0
        if os.path.exists("/proc/meminfo"):
            try:
                mem_dict = {}
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        parts = line.split(":")
                        if len(parts) == 2:
                            key = parts[0].strip()
                            val = parts[1].split()[0].strip()
                            mem_dict[key] = int(val)
                total_kb = mem_dict.get("MemTotal", 0)
                avail_kb = mem_dict.get("MemAvailable", mem_dict.get("MemFree", 0))
                mem_total_mb = round(total_kb / 1024, 1)
                mem_avail_mb = round(avail_kb / 1024, 1)
                if total_kb > 0:
                    mem_pct = round(((total_kb - avail_kb) / total_kb) * 100, 1)
            except Exception:
                pass

        return {
            "platform": f"{platform.system()} {platform.release()} ({platform.machine()})",
            "cpu": {
                "cores": cpu_count,
                "load_average_1m": round(load_1, 2),
                "load_average_5m": round(load_5, 2),
                "load_average_15m": round(load_15, 2),
                "load_per_core_1m": round(load_1 / cpu_count, 2)
            },
            "memory": {
                "total_mb": mem_total_mb,
                "available_mb": mem_avail_mb,
                "used_percentage": mem_pct
            },
            "disk": {
                "total_gb": disk_total,
                "used_gb": disk_used,
                "free_gb": disk_free,
                "used_percentage": disk_pct
            }
        }
