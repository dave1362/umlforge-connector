# UML Forge MCP Connector

<!-- mcp-name: io.github.dave1362/umlforge -->

**AI-powered UML diagram generation for coding agents.**

[UML Forge](https://umlforge.dev) gives Claude Code, Cursor, Windsurf, and any
MCP-compatible coding agent a suite of 13 specialised tools for producing
professional UML diagrams from your codebase, schema, or architecture
descriptions.

## Quick start

**Claude Code:**
```json
{
  "mcpServers": {
    "umlforge": {
      "command": "uvx",
      "args": ["umlforge==0.1.4"],
      "env": { "UMLFORGE_API_KEY": "your-api-key" }
    }
  }
}
```

**Cursor / Windsurf** — add the same block to your MCP settings.

Get your API key at [umlforge.dev](https://umlforge.dev).

## Tools included

| Tool | Description |
|------|-------------|
| `umlforge_suggest` | **Start here.** Describe your goal in plain English — returns the right tool and a ready-to-run call |
| `umlforge_reverse_engineer` | Class, sequence, and state diagrams from a codebase or GitHub URL |
| `umlforge_api_sequence` | Sequence diagrams for request flows across services |
| `umlforge_erd_schema` | Entity-relationship diagrams from domain descriptions or SQL schemas |
| `umlforge_state_machine` | State diagrams from entity lifecycles and business rules |
| `umlforge_frontend_components` | Component hierarchy and interaction diagrams for UI features |
| `umlforge_deployment` | Infrastructure and CI/CD pipeline diagrams |
| `umlforge_threat_model` | STRIDE threat model + attack surface diagram |
| `umlforge_event_driven` | Event flow and pub/sub architecture diagrams |
| `umlforge_ai_agent` | Agent topology and tool-call flow diagrams for LLM pipelines |
| `umlforge_stakeholder_arch` | C4 context diagrams for investors, CTOs, and non-technical stakeholders |
| `umlforge_living_docs` | Update existing diagrams to reflect sprint or PR changes |
| `umlforge_onboarding` | Day-one knowledge-transfer package for new team members |

All tools accept `report_mode=True` to generate a written analysis report
alongside the diagram.

## Requirements

- Python 3.11+
- An API key from [umlforge.dev](https://umlforge.dev) (free tier available)

## License

Proprietary. The connector is open to install and use with a UML Forge account.
