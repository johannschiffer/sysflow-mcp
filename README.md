# SysFlow MCP (Lite Edition)

> **Free:** [Genesis Starter Kit](https://johanld.gumroad.com/l/khffw) (25 `.cursorrules`/`CLAUDE.md` rulesets + MCP configs). Try the [live config builder](https://johannschiffer.github.io).
> **Full stack:** all six servers in [Genesis Enterprise Suite ($19)](https://johanld.gumroad.com/l/tzuvz).


[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)](https://python.org)
[![MCP Compliant](https://img.shields.io/badge/MCP-2024--11--05-purple.svg)](https://modelcontextprotocol.io)

**SysFlow MCP** is a lightweight, zero-overhead Model Context Protocol server that gives AI agents in **Claude Desktop**, **Cursor**, **Windsurf**, and **Antigravity** safe, structured access to Linux sysadmin inspection, log tailing, and service health without granting unrestricted root shells or risking interactive terminal freezes.

---

## Run without cloning

```bash
uvx --from git+https://github.com/johannschiffer/sysflow-mcp sysflow-mcp
```

Claude Desktop / Cursor config entry:

```json
{
  "mcpServers": {
    "sysflow-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/johannschiffer/sysflow-mcp",
        "sysflow-mcp"
      ]
    }
  }
}
```

[![CI](https://github.com/johannschiffer/sysflow-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/johannschiffer/sysflow-mcp/actions/workflows/ci.yml)

## 🖥️ Why SysFlow MCP?

Giving an AI assistant raw terminal execution often ends in frustration:
1. **Interactive Terminal Freezes:** Commands like `journalctl`, `systemctl status`, or `git log` default to interactive pagers (`less`), leaving the AI agent permanently hung waiting for user input.
2. **Context Window Flooding:** Tailing an unconstrained `/var/log/nginx/access.log` dumps thousands of lines into the LLM prompt, wasting tokens and causing memory errors.
3. **Destructive Shell Commands:** Without sandboxing, a hallucinated command can kill critical background daemons or delete workspace assets.

**SysFlow** exposes safe, bounded, non-blocking tools specifically tailored for autonomous developer agents.

---

## ⚡ Features (Lite Edition)

- 📊 **Resource Healthcheck**: Reports CPU core load averages (1m, 5m, 15m), RAM availability (MB and percentage), and disk partition metrics.
- 📜 **Safe Log Tailer**: Reads the last N lines (bounded and memory-safe) with optional regex filtering; automatically rejects binary files.
- ⚙️ **Systemd User Service Inspector**: Lists user-level services and timers (`systemctl --user`), highlighting failed units without requiring `sudo`.
- 🪶 **Zero External Dependencies**: Operates strictly on Python standard library and Linux `/proc` filesystem.

---

## 🚀 Quick Setup in 2 Minutes

### 1. Installation

```bash
git clone https://github.com/johannschiffer/sysflow-mcp.git
cd sysflow-mcp
pip install .
```

### 2. Configure Claude Desktop (`claude_desktop_config.json`)

On Linux: `~/.config/Claude/claude_desktop_config.json`  
On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`  
On Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "sysflow": {
      "command": "python",
      "args": ["-m", "sysflow.server"],
      "cwd": "/path/to/sysflow-mcp"
    }
  }
}
```

### 3. Verify via CLI

```bash
python -m sysflow.cli resources
```

---

## 🛠️ MCP Tools Exposed to AI Agents

| Tool | Parameters | Description |
|---|---|---|
| `check_system_resources` | *(none)* | Returns CPU load, memory usage, and partition disk metrics |
| `tail_logs` | `filepath`, `lines`, `pattern` | Safely tails recent log lines with optional regex filter |
| `inspect_systemd_services` | `failed_only` | Lists user-level services, states, and detects failed daemons |
| `inspect_systemd_timers` | *(none)* | Lists scheduled systemd user timers |

---

## 💎 Need Enterprise Build Sandboxing? Upgrade to SysFlow Pro

Looking to automate shell task execution, manage Docker containers, or generate verified systemd units?

| Feature | Lite (Open Source) | Enterprise Suite ($19) |
|---|:---:|:---:|
| **CPU, RAM & Disk Monitoring** | ✅ | ✅ |
| **Safe Bounded Log Tailer** | ✅ | ✅ |
| **Systemd User Service Auditing** | ✅ | ✅ |
| **Sandboxed Task Runner with Timeouts** *(Anti-freeze)* | ❌ | ✅ |
| **Docker Container Health & Log Inspector** | ❌ | ✅ |
| **Verified Systemd Unit File Generator** | ❌ | ✅ |
| **Listening Socket & Port Conflict Auditor** | ❌ | ✅ |
| **Production Docker Container** | ❌ | ✅ |
| **Full Pytest Suite & Sysadmin Automation Guide** | ❌ | ✅ |

👉 **[Get the Genesis Enterprise Suite ($19)](https://johanld.gumroad.com/l/tzuvz)**

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

## Recommended Infrastructure

VPS hosting that work well with SysFlow MCP. Some links are referral links.

- [Hetzner Cloud](https://www.hetzner.com/cloud)
- [DigitalOcean](https://www.digitalocean.com/)

## Genesis MCP Ecosystem

| Module | What it does | Repo |
|---|---|---|
| **CrawlEngine MCP** | Anti-bot web scraping, clean Markdown, proxy rotation and TLS evasion | [GitHub](https://github.com/johannschiffer/crawlengine-mcp) |
| **BrowserBridge MCP** | Deterministic headless browser automation with cryptographic action receipts | [GitHub](https://github.com/johannschiffer/browserbridge-mcp) |
| **PgSafe MCP** | Zero-trust PostgreSQL/SQLite guard, live PII masking, zero-downtime migration checks | [GitHub](https://github.com/johannschiffer/pgsafe-mcp) |
| **OmniBridge MCP** | Multi-channel notification and webhook bus with a persistent SQLite WAL queue | [GitHub](https://github.com/johannschiffer/omnibridge-mcp) |
| **SysFlow MCP** (this repo) | Safe Linux administration plane: systemd, port audit, isolated execution | [GitHub](https://github.com/johannschiffer/sysflow-mcp) |
| **FastMCP Forge** | Production MCP server scaffolder: stdio, SSE and auth middleware | [GitHub](https://github.com/johannschiffer/fastmcp-forge) |

[Live config builder](https://johannschiffer.github.io) | [Starter Kit, free](https://johanld.gumroad.com/l/khffw) | [Enterprise Suite, $19](https://johanld.gumroad.com/l/tzuvz)
