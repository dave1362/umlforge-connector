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
      "args": ["umlforge==0.1.3"],
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
| `umlforge_reverse_engineer` | Class, sequence, and state diagrams from a codebase or GitHub URL |
| `umlforge_api_sequence` | Sequence diagrams from OpenAPI / REST endpoints |
| `umlforge_erd_schema` | Entity-relationship diagrams from SQL schema or ORM models |
| `umlforge_state_machine` | State diagrams from business rules or UI flows |
| `umlforge_frontend_components` | Component hierarchy and data-flow diagrams |
| `umlforge_deployment` | Infrastructure and deployment diagrams |
| `umlforge_threat_model` | STRIDE threat model + attack surface diagram |
| `umlforge_event_driven` | Event flow and pub/sub architecture diagrams |
| `umlforge_ai_agent` | Agent topology and tool-call flow diagrams |
| `umlforge_stakeholder_arch` | C4 context diagrams for stakeholder communication |
| `umlforge_living_docs` | Living documentation diagrams synced to code |
| `umlforge_onboarding` | Onboarding maps for new team members |
| `umlforge_suggest` | Recommends the best diagram type for a description |

## Requirements

- Python 3.11+
- An API key from [umlforge.dev](https://umlforge.dev) (free tier available)

## License

Proprietary. The connector is open to install and use with a UML Forge account.
