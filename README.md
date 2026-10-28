# sysflow-mcp

[![PyPI](https://img.shields.io/pypi/v/sysflow-mcp.svg)](https://pypi.org/project/sysflow-mcp/)
[![CI](https://github.com/johannschiffer/sysflow-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/johannschiffer/sysflow-mcp/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)](https://python.org)
[![MCP Compliant](https://img.shields.io/badge/MCP-2024--11--05-purple.svg)](https://modelcontextprotocol.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Support on Ko-fi](https://img.shields.io/badge/Support%20on-Ko--fi-ff5e5b.svg)](https://ko-fi.com/johannschiffer)

<a href="https://glama.ai/mcp/servers/@johannschiffer/sysflow-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@johannschiffer/sysflow-mcp/badge" alt="sysflow-mcp MCP server" />
</a>

**SysFlow MCP** is a zero-dependency Linux administration and diagnostics Model Context Protocol server for Claude Desktop, Cursor, Windsurf, and Antigravity. It exposes host CPU/RAM/disk metrics, path-guarded log tailing, `systemd --user` service and timer inspection, validated unit generation, TCP port auditing, and timeout-bounded argv command execution.

---

## Quickstart

Run directly via `uvx`:

```bash
uvx sysflow-mcp
```

Claude Desktop / Cursor configuration:

```json
{
  "mcpServers": {
    "sysflow-mcp": {
      "command": "uvx",
      "args": ["sysflow-mcp"]
    }
  }
}
```

---

## Core Capabilities

1. **System Resource Telemetry:** Reads CPU load averages, `/proc/meminfo` memory usage, and root partition utilization without requiring root privileges.
2. **Path-Guarded Log Tailer:** Reads backward in chunks from `/var/log`, `/tmp`, or configured `SYSFLOW_LOG_DIRS`, filtering regex matches before slicing and rejecting binary files or sensitive dotfiles (`.env`, `.ssh`, `.git/config`).
3. **Systemd User Plane Inspection:** Lists `systemd --user` services, failed units, and scheduled timers.
4. **Validated Systemd Unit Generator:** Generates `.service` and `.timer` definitions, rejecting control-character injection and distinguishing `OnUnitActiveSec` intervals (`12h`, `30min`) from `OnCalendar` expressions (`hourly`, `daily`, `*-*-* 04:00:00`).
5. **Listening TCP Port Auditor:** Inspects active TCPv4/TCPv6 listeners via `ss` with a `/proc/net/tcp{,6}` hex-decoding fallback.
6. **Timeout-Bounded Task Runner:** Executes non-interactive argv commands (`shell=False` by default, secret environment variables scrubbed) inside a dedicated process group that is cleanly killed if the timeout expires.

---

## MCP Tools

| Tool | Parameters | Description |
|---|---|---|
| `check_system_resources` | *(none)* | Returns CPU load averages, RAM usage, and disk space |
| `tail_logs` | `filepath`, `lines`, `pattern` | Tails text log files inside allowed directories with optional regex filter |
| `inspect_systemd_services` | `failed_only` | Lists `systemd --user` service units and active states |
| `inspect_systemd_timers` | *(none)* | Lists active `systemd --user` timers |
| `run_sandboxed_task` | `command`, `timeout_sec`, `cwd` | Runs an argv command with secret scrubbing and process-group timeout |
| `generate_systemd_unit` | `service_name`, `exec_start`, `cwd`, `timer_schedule` | Emits validated `.service` and `.timer` unit strings |
| `audit_listening_ports` | *(none)* | Lists listening TCPv4 and TCPv6 ports |

---

## Related Open-Source MCP Servers

| Package | Description | Repository |
|---|---|---|
| **genesis-blackbox** | Runtime flight recorder and AST blast-radius crash compiler | [GitHub](https://github.com/johannschiffer/genesis-blackbox) |
| **pgsafe-mcp** | Read-only PostgreSQL/SQLite query guard and PII masker | [GitHub](https://github.com/johannschiffer/pgsafe-mcp) |
| **crawlengine-mcp** | HTTP web extraction, clean Markdown conversion, and proxy rotation | [GitHub](https://github.com/johannschiffer/crawlengine-mcp) |
| **browserbridge-mcp** | Session-pooled HTTP DOM inspection and SHA-256 action trail receipts | [GitHub](https://github.com/johannschiffer/browserbridge-mcp) |
| **omnibridge-mcp** | Multi-channel notification bus with SQLite retry queue | [GitHub](https://github.com/johannschiffer/omnibridge-mcp) |
| **fastmcp-forge** | MCP server framework and project scaffolder | [GitHub](https://github.com/johannschiffer/fastmcp-forge) |

## Support

If this project is useful in your workflow, you can support ongoing maintenance on [Ko-fi](https://ko-fi.com/johannschiffer).

## License

MIT License. Copyright (c) 2026 [Johann Schiffer](https://github.com/johannschiffer).
