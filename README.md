# UML Forge — MCP Connector

> 13 AI-powered UML diagram tools for Claude Code, Cursor, Windsurf, and any MCP-compatible coding agent.

[![PyPI version](https://img.shields.io/pypi/v/umlforge)](https://pypi.org/project/umlforge/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://pypi.org/project/umlforge/)
[![MCP](https://img.shields.io/badge/protocol-MCP-8b5cf6)](https://modelcontextprotocol.io)

## What is this?

This repository contains the **open-source MCP connector** for [UML Forge](https://umlforge.dev) — a hosted service that generates professional Mermaid UML diagrams from inside your coding environment.

When installed, the connector runs locally as a stdio MCP server. Your coding agent (Claude Code, Cursor, Windsurf, etc.) calls one of the 13 diagram tools, the connector forwards the request to the UML Forge API (`api.umlforge.dev`), and the diagram is returned directly in your editor.

```
Your editor  →  MCP connector (this repo, runs locally)  →  UML Forge API  →  Mermaid diagram
```

**No code is stored.** Input is processed in memory on the API server and discarded after the response is returned. See [Security and Privacy](#security-and-privacy) below.

---

## Quick start

### 1. Get an API key

Sign up for a free account at [umlforge.dev](https://umlforge.dev). The free tier includes 5 diagrams per month with no credit card required.

### 2. Configure your editor

**Claude Code** — add to `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "umlforge": {
      "command": "uvx",
      "args": ["umlforge==0.1.1"],
      "env": {
        "UMLFORGE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**Cursor** — add to your MCP settings (`~/.cursor/mcp.json` or the project `.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "umlforge": {
      "command": "uvx",
      "args": ["umlforge==0.1.1"],
      "env": {
        "UMLFORGE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

**Windsurf** — same JSON block, placed in your Windsurf MCP configuration.

> **Tip:** Pin the version (`umlforge==0.1.1`) so your setup is reproducible. Check [PyPI](https://pypi.org/project/umlforge/) for the latest release.

---

## Tools included

| Tool | What it generates |
|------|-------------------|
| `umlforge_reverse_engineer` | Class, sequence, and state diagrams from a codebase or GitHub URL |
| `umlforge_api_sequence` | Sequence diagrams from REST/OpenAPI endpoint descriptions |
| `umlforge_erd_schema` | Entity-relationship diagrams from SQL schema or ORM models |
| `umlforge_state_machine` | State diagrams from business rules or UI flows |
| `umlforge_frontend_components` | Component hierarchy and data-flow diagrams |
| `umlforge_deployment` | Infrastructure and deployment architecture diagrams |
| `umlforge_threat_model` | STRIDE threat model + attack surface diagram |
| `umlforge_event_driven` | Event flow and pub/sub architecture diagrams |
| `umlforge_ai_agent` | Agent topology and tool-call flow diagrams |
| `umlforge_stakeholder_arch` | C4 context diagrams for stakeholder communication |
| `umlforge_living_docs` | Living documentation diagrams synced to code |
| `umlforge_onboarding` | Onboarding maps for new team members |
| `umlforge_suggest` | Recommends the best diagram type for a description |

---

## How it works

This connector is intentionally thin. Every tool in `connector/tools.py` does one thing: forward the call to the UML Forge API.

`api_client.py` sends an authenticated HTTPS POST to `https://api.umlforge.dev/v1/generate` with:
- The tool name
- Your input (code snippet, description, GitHub URL, etc.)
- Your API key in the `Authorization: Bearer` header

The API server runs the diagram generation, validates the Mermaid output, and returns it. The connector passes the result back to your editor.

There is **no local LLM**, no file system access, no process spawning, and no data persistence in the connector.

---

## Security and privacy

**What is sent to the API:**
- Your tool inputs (code snippets, system descriptions, GitHub URLs you explicitly provide)
- Your API key (used for authentication and rate limiting only)

**What is NOT collected:**
- File system contents beyond what you explicitly pass to a tool
- Environment variables or secrets
- Conversation history from your editor
- Any data beyond the specific tool call arguments

**API server behaviour:**
- Input is processed in memory and discarded after the response is returned
- No code or description you submit is stored
- All traffic is encrypted via TLS (HTTPS)

Full privacy policy: [umlforge.dev/privacy](https://umlforge.dev/privacy)

---

## Requirements

- Python 3.11 or later
- `uvx` (comes with [uv](https://docs.astral.sh/uv/)) — or install with `pip install umlforge`
- An API key from [umlforge.dev](https://umlforge.dev)

---

## Repository structure

```
connector/
  __init__.py       — package marker
  __main__.py       — entry point for uvx umlforge
  server.py         — FastMCP server initialisation
  tools.py          — 13 MCP tool definitions (signatures + docstrings)
  api_client.py     — HTTPS client for api.umlforge.dev
  config.py         — API key loading from UMLFORGE_API_KEY env var
  README.md         — PyPI package description
pyproject.toml      — package metadata and dependencies
server.json         — MCP Registry metadata
```

The diagram generation logic, prompt engineering, Mermaid validation, and billing are all server-side at `api.umlforge.dev` and are not part of this repository.

---

## License

The connector is proprietary software. It is freely distributable and installable for use with a UML Forge account. Redistribution or modification without permission is not permitted.

© 2026 UML Forge. All rights reserved.

---

## Links

- **Website:** [umlforge.dev](https://umlforge.dev)
- **PyPI:** [pypi.org/project/umlforge](https://pypi.org/project/umlforge/)
- **MCP Registry:** [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io/servers?search=io.github.dave1362)
- **Support:** [support@umlforge.dev](mailto:support@umlforge.dev)
