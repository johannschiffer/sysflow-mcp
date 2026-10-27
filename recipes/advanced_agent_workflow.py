from sysflow.core.port_auditor import PortAuditor
from sysflow.monitors.resources import ResourceMonitor

def main():
    auditor = PortAuditor()
    listening_ports = auditor.get_open_ports()
    print("Open listening ports:", listening_ports)

    resources = ResourceMonitor()
    stats = resources.get_snapshot()
    print("System stats: CPU", stats.get("cpu_percent"), "%, RAM", stats.get("memory_percent"), "%")

if __name__ == "__main__":
    main()
