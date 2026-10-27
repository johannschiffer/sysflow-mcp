# sysflow-mcp (v2.0.0)

[![PyPI version](https://img.shields.io/badge/PyPI-v2.0.0-blue.svg)](https://pypi.org/project/sysflow-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Support on Ko-fi](https://img.shields.io/badge/Support%20on-Ko--fi-ff5e5b.svg)](https://ko-fi.com/johannschiffer)

> **100% Free & Open Source (MIT)**: All features, proxy rotation, migration simulation, Docker stacks, and recipes are completely unlocked. Support open development on [Ko-fi](https://ko-fi.com/johannschiffer).

> ### ⚡ Open Source Ecosystem & Community Tools
> | Resource | Access | Description |
> |---|---|---|
> | **Ruleset Bundle** | **100% Free** | 55+ production rulesets & MCP config templates. [Download Free](https://johannschiffer.github.io/) |
> | **Support & Donate** | **Ko-fi** | Support open-source maintenance. [Support on Ko-fi](https://ko-fi.com/johannschiffer) |

<a href="https://glama.ai/mcp/servers/@johannschiffer/sysflow-mcp">
  <img width="380" height="200" src="https://glama.ai/mcp/servers/@johannschiffer/sysflow-mcp/badge" alt="sysflow-mcp MCP server" />
</a>

[![Release](https://img.shields.io/github/v/release/johannschiffer/sysflow-mcp?include_prereleases&color=blue)](https://github.com/johannschiffer/sysflow-mcp/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-brightgreen.svg)](https://python.org)
[![MCP Compliant](https://img.shields.io/badge/MCP-2024--11--05-purple.svg)](https://modelcontextprotocol.io)


**SysFlow MCP** is a lightweight, zero-overhead Model Context Protocol server that gives AI agents in **Claude Desktop**, **Cursor**, **Windsurf**, and **Antigravity** safe, structured access to Linux sysadmin inspection, log tailing, and service health without granting unrestricted root shells or risking interactive terminal freezes.

---

## Run without cloning

Execute directly via `uvx` (PyPI direct or Git source):

```bash
# Direct PyPI invocation:
uvx sysflow-mcp

# Or direct Git invocation (pre-PyPI sync):
uvx --from git+https://github.com/johannschiffer/sysflow-mcp sysflow-mcp
```

Claude Desktop / Cursor config entry:

```json
{
  "mcpServers": {
    "sysflow-mcp": {
      "command": "uvx",
      "args": [
        "sysflow-mcp"
      ]
    }
  }
}
```
*(Alternative for pre-indexation: replace `"args": ["sysflow-mcp"]` with `"args": ["--from", "git+https://github.com/johannschiffer/sysflow-mcp", "sysflow-mcp"]`)*

[![CI](https://github.com/johannschiffer/sysflow-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/johannschiffer/sysflow-mcp/actions/workflows/ci.yml)

## 🖥️ Why SysFlow MCP?

Giving an AI assistant raw terminal execution often ends in frustration:
1. **Interactive Terminal Freezes:** Commands like `journalctl`, `systemctl status`, or `git log` default to interactive pagers (`less`), leaving the AI agent permanently hung waiting for user input.
2. **Context Window Flooding:** Tailing an unconstrained `/var/log/nginx/access.log` dumps thousands of lines into the LLM prompt, wasting tokens and causing memory errors.
3. **Destructive Shell Commands:** Without sandboxing, a hallucinated command can kill critical background daemons or delete workspace assets.

**SysFlow** exposes safe, bounded, non-blocking tools specifically tailored for autonomous developer agents.

---

## ⚡ Features (Open Source v2.0)

- 📊 **Resource Healthcheck**: Reports CPU core load averages (1m, 5m, 15m), RAM availability (MB and percentage), and disk partition metrics.
- 📜 **Safe Log Tailer**: Reads the last N lines (bounded and memory-safe) with optional regex filtering; automatically rejects binary files.
- ⚙️ **Systemd User Service Inspector**: Lists user-level services and timers (`systemctl --user`), highlighting failed units without requiring `sudo`.
- ⏱️ **Sandboxed Task Runner with Timeouts**: Anti-freeze execution plane for shell tasks.
- 🐳 **Docker Container Health & Log Inspector**: Inspects container states, health status, and logs.
- 📄 **Verified Systemd Unit File Generator**: Generates clean, secure service unit files.
- 🔌 **Listening Socket & Port Conflict Auditor**: Discovers active listening ports and detects binding collisions.
- 🐳 **Production Docker Container**: Containerized system observability plane.
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

[Live config builder](https://johannschiffer.github.io) | [GitHub Profile](https://github.com/johannschiffer) | [Support on Ko-fi ☕](https://ko-fi.com/johannschiffer)

## Recommended Infrastructure & Sponsorship

- **Sponsorship & Corporate Support**: Support continued maintenance and priority feature requests via [GitHub Sponsors](https://github.com/sponsors/johannschiffer).
- **Verified Cloud & Network Infrastructure**:
  - **High-Performance VPS & Nodes**: [Hetzner Cloud](https://www.hetzner.com/cloud) & [DigitalOcean](https://m.do.co/c/johannschiffer)
  - **Reliable Proxy Pool & IP Rotation**: [Webshare](https://www.webshare.io/) & [Bright Data](https://brightdata.com/)
  - **Documentation & Setup Guides**: [johannschiffer.github.io](https://johannschiffer.github.io/)

---

## Support

[![Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/johannschiffer)

If you find this tool helpful, you can support its maintenance via Ko-fi.
