"""
SysFlow CLI testing utility.
Usage:
  python -m sysflow.cli resources
  python -m sysflow.cli tail /var/log/syslog --lines 20
  python -m sysflow.cli systemd --failed
"""

import argparse
import json
import sys
from .monitors.resources import ResourceMonitor
from .monitors.logs import LogTailer
from .monitors.systemd import SystemdInspector

def main():
    parser = argparse.ArgumentParser(description="SysFlow CLI utility")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    subparsers.add_parser("resources", help="Check system CPU, RAM, and disk utilization")

    tail_parser = subparsers.add_parser("tail", help="Tail recent lines from log file")
    tail_parser.add_argument("file", help="Path to log file")
    tail_parser.add_argument("--lines", type=int, default=50, help="Number of lines")
    tail_parser.add_argument("--pattern", help="Regex filter pattern")

    systemd_parser = subparsers.add_parser("systemd", help="Inspect systemd --user units")
    systemd_parser.add_argument("--failed", action="store_true", help="Only show failed units")

    args = parser.parse_args()

    if args.command == "resources":
        stats = ResourceMonitor.get_system_stats()
        print(json.dumps(stats, indent=2))

    elif args.command == "tail":
        res = LogTailer.tail(args.file, lines=args.lines, pattern=args.pattern)
        print(json.dumps(res, indent=2))

    elif args.command == "systemd":
        res = SystemdInspector.list_user_units(failed_only=args.failed)
        print(json.dumps(res, indent=2))

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
