from sysflow.core.port_auditor import PortAuditor
from sysflow.monitors.resources import ResourceMonitor


def main():
    port_report = PortAuditor.audit_listening_ports()
    print("Listening TCP ports count:", port_report.get("count", 0))

    stats = ResourceMonitor.get_system_stats()
    cpu_load = stats.get("cpu", {}).get("load_average_1m", 0.0)
    ram_pct = stats.get("memory", {}).get("used_percentage", 0.0)
    print(f"System stats: 1m load={cpu_load}, RAM={ram_pct}%")


if __name__ == "__main__":
    main()
