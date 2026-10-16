"""
UML Forge Connector — API Client

Thin HTTP client for the UML Forge hosted API.
ZERO business logic. ZERO prompt text.
All diagram generation happens server-side.
"""

from __future__ import annotations

from importlib import metadata as _metadata

import httpx

from connector.config import load_config

# Generation can take 1-3 minutes on paid tiers (diagram + optional report call)
_GENERATE_TIMEOUT = 210.0
_SUGGEST_TIMEOUT  = 30.0


def _connector_version() -> str:
    try:
        return _metadata.version("umlforge")
    except Exception:
        return "unknown"


def _headers(api_key: str) -> dict[str, str]:
    version = _connector_version()
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": f"umlforge-connector/{version}",
        # Lets the server apply the current report_mode rules (see /v1/generate)
        "X-UmlForge-Connector": version,
    }


def _failure_message(exc: Exception) -> str:
    """Readable message for transport/server failures instead of a raw traceback."""
    if isinstance(exc, httpx.TimeoutException):
        return (
            "**UML Forge: the request timed out.**\n\n"
            "Generation took longer than the connector waits "
            f"({int(_GENERATE_TIMEOUT)}s). Try again with a shorter description, "
            "or turn off report mode (`report_mode=false`) for a faster diagram-only run."
        )
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        request_id = exc.response.headers.get("x-request-id", "")
        ref = f" Reference: `{request_id}`." if request_id else ""
        if code == 429:
            retry = exc.response.headers.get("retry-after")
            wait = f" Retry in about {retry}s." if retry else ""
            return f"**UML Forge: request limit reached.**{wait}{ref}"
        if code == 504:
            return (
                "**UML Forge: the AI service timed out.** "
                f"Please try again in a moment.{ref}"
            )
        if code >= 500:
            return (
                f"**UML Forge: the service returned an error ({code}).** "
                f"Please try again in a moment.{ref}"
            )
    return f"**UML Forge: request failed** ({type(exc).__name__}). Please try again."


async def generate(
    tool: str,
    params: dict,
    guided_mode: bool = False,
) -> str:
    """
    Call POST /v1/generate on the UML Forge API.
    Returns a formatted Markdown string ready for display in a coding agent.
    """
    config = load_config()
    if not config.api_key:
        return (
            "**UML Forge: API key not configured.**\n\n"
            "Add your key to your MCP configuration:\n\n"
            "```json\n"
            "{\n"
            '  "mcpServers": {\n'
            '    "umlforge": {\n'
            '      "command": "uvx",\n'
            '      "args": ["umlforge"],\n'
            '      "env": { "UMLFORGE_API_KEY": "uf_live_your_key_here" }\n'
            "    }\n"
            "  }\n"
            "}\n"
            "```\n\n"
            "Get your free API key at https://umlforge.dev"
        )

    # report_mode=None means "not specified": omit it so the server can apply the
    # account's saved preference. An explicit True/False is always sent.
    if params.get("report_mode") is None:
        params = {k: v for k, v in params.items() if k != "report_mode"}

    try:
        async with httpx.AsyncClient(timeout=_GENERATE_TIMEOUT) as client:
            response = await client.post(
                f"{config.api_base_url}/v1/generate",
                json={
                    "tool": tool,
                    "params": params,
                    "guided_mode": guided_mode and config.guided_mode,
                },
                headers=_headers(config.api_key),
            )
    except httpx.TimeoutException as exc:
        return _failure_message(exc)

    if response.status_code == 402:
        body = response.json()
        upgrade_url = body.get("upgrade_url", "https://umlforge.dev/billing")
        return (
            f"**Monthly diagram limit reached.**\n\n"
            f"{body.get('error', 'Upgrade to Pro for unlimited diagrams.')}\n\n"
            f"Upgrade at: {upgrade_url}"
        )

    if response.status_code == 401:
        return (
            "**Authentication failed.** Check that your API key in "
            "your UMLFORGE_API_KEY is correct and active."
        )

    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        return _failure_message(exc)
    return _format_generate_response(response.json())


async def suggest(task_description: str) -> str:
    """
    Call POST /v1/suggest on the UML Forge API.
    Returns a formatted recommendation string.
    """
    config = load_config()
    if not config.api_key:
        return (
            "**UML Forge: API key not configured.**\n\n"
            "Add your key to your MCP configuration:\n\n"
            "```json\n"
            "{\n"
            '  "mcpServers": {\n'
            '    "umlforge": {\n'
            '      "command": "uvx",\n'
            '      "args": ["umlforge"],\n'
            '      "env": { "UMLFORGE_API_KEY": "uf_live_your_key_here" }\n'
            "    }\n"
            "  }\n"
            "}\n"
            "```\n\n"
            "Get your free API key at https://umlforge.dev"
        )

    async with httpx.AsyncClient(timeout=_SUGGEST_TIMEOUT) as client:
        response = await client.post(
            f"{config.api_base_url}/v1/suggest",
            json={"task_description": task_description},
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
            },
        )

    if response.status_code == 401:
        return (
            "**Authentication failed.** Check that your API key in "
            "your UMLFORGE_API_KEY is correct and active."
        )

    if response.status_code == 402:
        body = response.json()
        upgrade_url = body.get("upgrade_url", "https://umlforge.dev/billing")
        return (
            f"**Monthly diagram limit reached.**\n\n"
            f"{body.get('error', 'Upgrade to Pro for unlimited diagrams.')}\n\n"
            f"Upgrade at: {upgrade_url}"
        )

    response.raise_for_status()
    body = response.json()

    ready = body.get("ready_to_run", "")
    ready_block = f"\n\n**Ready to run:**\n```\n{ready}\n```" if ready else ""

    return (
        f"**Recommended:** `{body['recommended_tool']}`  \n"
        f"{body['reasoning']}"
        f"{ready_block}\n\n"
        f"**Alternative:** `{body['alternative_tool']}`  \n"
        f"{body['alternative_reasoning']}"
    )


# ── Response formatter ────────────────────────────────────────────────────────

def _format_generate_response(body: dict) -> str:
    """
    Format a /v1/generate response body into readable Markdown.

    Output shape:
      ## Diagram Title [⚠️ if validation warning]

      ```mermaid
      [content]
      ```

      [supplementary tables / notes]

      ---
      *Generated by UML Forge | X diagrams remaining this month*
    """
    parts: list[str] = []

    for diagram in body.get("diagrams", []):
        title   = diagram.get("title", "Diagram")
        mermaid = diagram.get("mermaid", "").strip()
        warning = " ⚠️ _validation warning — review before using_" \
                  if diagram.get("validation_warning") else ""

        parts.append(f"## {title}{warning}\n\n```mermaid\n{mermaid}\n```")

    # Supplementary sections (STRIDE table, implementation notes, etc.)
    supplementary = body.get("supplementary", {})
    for key, content in supplementary.items():
        if isinstance(content, str) and content.strip():
            parts.append(content.strip())

    # Usage footer
    usage     = body.get("usage", {})
    remaining = usage.get("diagrams_remaining")
    tier      = usage.get("tier", "free")

    if remaining is not None:
        footer = f"*Generated by UML Forge | {remaining} diagrams remaining this month*"
    else:
        footer = f"*Generated by UML Forge | {tier.title()} — unlimited diagrams*"

    parts.append("---\n" + footer)

    return "\n\n".join(parts)
