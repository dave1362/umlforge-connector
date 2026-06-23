"""
UML Forge Connector — Configuration

Resolution order (first match wins):
  1. Environment variables — set via .mcp.json "env" block (recommended)
       UMLFORGE_API_KEY        required
       UMLFORGE_GUIDED_MODE    optional, "true"/"false" (default: false)
       UMLFORGE_API_BASE_URL   optional (default: https://api.umlforge.dev)

  2. Config file fallback — ~/.umlforge/config.toml
       api_key       = "uf_live_your_key_here"
       api_base_url  = "https://api.umlforge.dev"   # optional
       guided_mode   = false                         # optional, Pro tier only
"""

import os
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

CONFIG_PATH = Path.home() / ".umlforge" / "config.toml"

_SETUP_INSTRUCTIONS = """\
UML Forge: no API key found.

Add the key via your .mcp.json "env" block (recommended):

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

Or create ~/.umlforge/config.toml:

  api_key = "uf_live_your_key_here"
  guided_mode = false

Get your key at https://umlforge.dev
"""


@dataclass
class ConnectorConfig:
    api_key: str
    api_base_url: str = "https://api.umlforge.dev"
    guided_mode: bool = False


def load_config() -> ConnectorConfig:
    """
    Load connector configuration from env vars (primary) or config file (fallback).
    Exits with setup instructions if no API key is found.
    """
    # ── 1. Environment variables (set by MCP host via .mcp.json "env" block) ──
    api_key = os.environ.get("UMLFORGE_API_KEY", "").strip()
    if api_key:
        return ConnectorConfig(
            api_key=api_key,
            api_base_url=os.environ.get(
                "UMLFORGE_API_BASE_URL", "https://api.umlforge.dev"
            ).rstrip("/"),
            guided_mode=os.environ.get("UMLFORGE_GUIDED_MODE", "false").lower() == "true",
        )

    # ── 2. Config file fallback ────────────────────────────────────────────────
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "rb") as fh:
            data = tomllib.load(fh)

        if "api_key" not in data:
            print(
                f"UML Forge: 'api_key' not found in {CONFIG_PATH}\n"
                "Add: api_key = \"uf_live_your_key_here\"",
                file=sys.stderr,
            )
            sys.exit(1)

        return ConnectorConfig(
            api_key=data["api_key"],
            api_base_url=data.get("api_base_url", "https://api.umlforge.dev").rstrip("/"),
            guided_mode=bool(data.get("guided_mode", False)),
        )

    # ── 3. Nothing found ───────────────────────────────────────────────────────
    print(_SETUP_INSTRUCTIONS, file=sys.stderr)
    sys.exit(1)
