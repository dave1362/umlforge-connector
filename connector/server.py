"""
UML Forge Connector — MCP Server Entry Point

Starts the FastMCP stdio server with all 13 UML Forge tools registered.

Installation:
    uvx umlforge          # recommended — isolated, no pip install needed

Claude Code (.mcp.json):
    {
      "mcpServers": {
        "umlforge": {
          "command": "uvx",
          "args": ["umlforge"],
          "env": {
            "UMLFORGE_API_KEY": "uf_live_your_key_here"
          }
        }
      }
    }

Cursor / other MCP hosts:
    Same structure — set UMLFORGE_API_KEY in the "env" block.

Config fallback (power users): ~/.umlforge/config.toml
    api_key     = "uf_live_your_key_here"
    guided_mode = false
"""

from connector.tools import mcp

if __name__ == "__main__":
    mcp.run()
