"""
SysFlow MCP: Model Context Protocol Server (Lite Edition)
Implements standard JSON-RPC 2.0 stdio transport for safe system inspection and log monitoring.
"""

import sys
import json
import logging
from typing import Dict, Any, List, Optional
from .monitors.resources import ResourceMonitor
from .monitors.logs import LogTailer
from .monitors.systemd import SystemdInspector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [SysFlow] %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("SysFlowServer")

class SysFlowMCPServer:
    def __init__(self):
        self.server_name = "sysflow-mcp"
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
            }
        ]

    def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if name == "check_system_resources":
            return {
                "success": True,
                "resources": ResourceMonitor.get_system_stats()
            }

        elif name == "tail_logs":
            filepath = arguments.get("filepath", "")
            lines = arguments.get("lines", 50)
            pattern = arguments.get("pattern")
            return LogTailer.tail(filepath, lines=lines, pattern=pattern)

        elif name == "inspect_systemd_services":
            failed_only = arguments.get("failed_only", False)
            return SystemdInspector.list_user_units(failed_only=failed_only)

        elif name == "inspect_systemd_timers":
            return SystemdInspector.list_user_timers()

        else:
            raise ValueError(f"Unknown tool: {name}")

    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        req_id = request.get("id")
        method = request.get("method")
        params = request.get("params", {})

        if req_id is None:
            if method == "notifications/initialized":
                logger.info("Client completed initialization handshake.")
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
    import argparse
    parser = argparse.ArgumentParser(
        prog="sysflow-mcp",
        description="SysFlow MCP: Safe Linux Sysadmin, Process & Build Automation Engine for AI Agents"
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0.0")
    args, unknown = parser.parse_known_args()
    server = SysFlowMCPServer()
    server.run_stdio()

if __name__ == "__main__":
    main()
