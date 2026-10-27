"""
Unit tests for SysFlow MCP Server JSON-RPC protocol compliance.
"""
import pytest
import json
from sysflow.server import SysFlowServer

def test_mcp_initialize():
    server = SysFlowServer()
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        }
    }
    resp = server.handle_request(req)
    assert resp["id"] == 1
    assert resp["result"]["serverInfo"]["name"] == "sysflow-mcp"

def test_mcp_tools_list():
    server = SysFlowServer()
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    resp = server.handle_request(req)
    tools = resp["result"]["tools"]
    names = [t["name"] for t in tools]
    assert "check_system_resources" in names
    assert "tail_logs" in names
    assert "inspect_systemd_services" in names
    assert "inspect_systemd_timers" in names
    assert "run_sandboxed_task" in names
    assert "generate_systemd_unit" in names
    assert "audit_listening_ports" in names

def test_mcp_check_resources():
    server = SysFlowServer()
    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "check_system_resources",
            "arguments": {}
        }
    }
    resp = server.handle_request(req)
    content = json.loads(resp["result"]["content"][0]["text"])
    assert content["success"] is True
    assert "cpu" in content["resources"]
