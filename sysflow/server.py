from ._genesis import NOTICE, print_upgrade_notice
"""
SysFlow MCP: Model Context Protocol Server (Enterprise Pro Edition)
Includes System Resource Monitor, Safe Log Tailer, Systemd Inspector,
Sandboxed Task Runner with Timeouts, Unit Generator, and Port Auditor.
"""

import sys
import json
import logging
from typing import Dict, Any, List, Optional
from .monitors.resources import ResourceMonitor
from .monitors.logs import LogTailer
from .monitors.systemd import SystemdInspector
from .core.task_runner import TaskRunner
from .core.systemd_generator import SystemdGenerator
from .core.port_auditor import PortAuditor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [SysFlow-Pro] %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("SysFlowProServer")

class SysFlowProServer:
    def __init__(self):
        self.server_name = "sysflow-mcp-pro"
        self.server_version = "1.0.0"

    def get_tools_definition(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "check_system_resources",
                "description": "Inspect CPU load average, RAM utilization, and disk partition space.",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "tail_logs",
                "description": "Safely read recent lines from a log or text file with optional regex filtering.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "Absolute or relative path to log file"},
                        "lines": {"type": "integer", "description": "Number of recent lines to retrieve (default: 50, max: 500)"},
                        "pattern": {"type": "string", "description": "Optional regex pattern to filter lines"}
                    },
                    "required": ["filepath"]
                }
            },
            {
                "name": "inspect_systemd_services",
                "description": "List systemd --user services, active states, and detect failed background units.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "failed_only": {"type": "boolean", "description": "Only return units in failed state (default: false)"}
                    }
                }
            },
            {
                "name": "inspect_systemd_timers",
                "description": "List systemd --user scheduled timers and their next trigger times.",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "run_sandboxed_task",
                "description": "Execute a shell or build task with hard timeout control to prevent terminal hangs.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": "Shell command to execute"},
                        "timeout_sec": {"type": "integer", "description": "Timeout in seconds (default: 30, max: 300)"},
                        "cwd": {"type": "string", "description": "Working directory for execution"}
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "generate_systemd_unit",
                "description": "Generate syntactically validated systemd service and timer unit files.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "service_name": {"type": "string", "description": "Name of service (e.g. 'my-scraper')"},
                        "exec_start": {"type": "string", "description": "Full command to execute"},
                        "cwd": {"type": "string", "description": "Working directory path"},
                        "timer_schedule": {"type": "string", "description": "Schedule expression (e.g. '6h', 'daily', or OnCalendar)"}
                    },
                    "required": ["service_name", "exec_start"]
                }
            },
            {
                "name": "audit_listening_ports",
                "description": "Audit local listening TCP ports to detect binding conflicts and open network sockets.",
                "inputSchema": {"type": "object", "properties": {}}
            }
        ]

    def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name == "check_system_resources":
            return {"success": True, "resources": ResourceMonitor.get_system_stats()}

        elif name == "tail_logs":
            return LogTailer.tail(
                arguments.get("filepath", ""),
                lines=arguments.get("lines", 50),
                pattern=arguments.get("pattern")
            )

        elif name == "inspect_systemd_services":
            return SystemdInspector.list_user_units(failed_only=arguments.get("failed_only", False))

        elif name == "inspect_systemd_timers":
            return SystemdInspector.list_user_timers()

        elif name == "run_sandboxed_task":
            return TaskRunner.run_command(
                arguments.get("command", ""),
                timeout_sec=arguments.get("timeout_sec", 30),
                cwd=arguments.get("cwd")
            )

        elif name == "generate_systemd_unit":
            return SystemdGenerator.generate_unit(
                service_name=arguments.get("service_name", ""),
                exec_start=arguments.get("exec_start", ""),
                cwd=arguments.get("cwd"),
                timer_schedule=arguments.get("timer_schedule")
            )

        elif name == "audit_listening_ports":
            return PortAuditor.audit_listening_ports()

        else:
            raise ValueError(f"Unknown tool: {name}")

    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if req_id is None:
            if method == "notifications/initialized":
                logger.info("Pro client completed initialization handshake.")
            return None

        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": self.server_name,
                        "version": self.server_version
                    }
                }
            }

        elif method == "ping":
            return {"jsonrpc": "2.0", "id": req_id, "result": {}}

        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": self.get_tools_definition()}
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                output = self.handle_tool_call(tool_name, tool_args)
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(output, indent=2, ensure_ascii=False)
                            }
                        ],
                        "isError": not output.get("success", True) if "success" in output else False
                    }
                }
            except Exception as e:
                logger.error(f"Error calling tool {tool_name}: {e}")
                return {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32000, "message": str(e)}
                }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }

    def run_stdio(self):
        logger.info(f"Starting {self.server_name} v{self.server_version} stdio listener...")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
                response = self.handle_request(request)
                if response is not None:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
            except Exception as e:
                logger.error(f"Error processing stdio line: {e}")

def main():
    print_upgrade_notice()
    server = SysFlowProServer()
    server.run_stdio()

if __name__ == "__main__":
    main()
