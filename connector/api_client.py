"""
UML Forge Connector — API Client

Thin HTTP client for the UML Forge hosted API.
ZERO business logic. ZERO prompt text.
All diagram generation happens server-side.
"""

from __future__ import annotations

import asyncio
import os
from importlib import metadata as _metadata

import httpx

from connector.config import load_config

# Generation can take 1-3 minutes on paid tiers (diagram + optional report call)
_GENERATE_TIMEOUT = 210.0
_SUGGEST_TIMEOUT  = 30.0

# Job flow: many MCP clients cancel a tool call after ~60 s, so a tool call waits at
# most this long for a generation, then hands back a job id for umlforge_get_result.
# Clients with longer timeouts can raise it: UMLFORGE_WAIT_SECONDS (5-200).
_DEFAULT_WAIT_SECONDS = 45.0
_JOB_START_TIMEOUT = 30.0
_POLL_SLICE_SECONDS = 20       # longest single server-side wait per poll request


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


# ── Job flow (generation runs server-side; the tool call never waits >~45 s) ──

def _wait_budget() -> float:
    try:
        value = float(os.environ.get("UMLFORGE_WAIT_SECONDS", _DEFAULT_WAIT_SECONDS))
    except ValueError:
        value = _DEFAULT_WAIT_SECONDS
    return max(5.0, min(value, 200.0))


def _missing_key_message() -> str:
    return (
        "**UML Forge: API key not configured.**\n\n"
        "Set `UMLFORGE_API_KEY` in your MCP configuration. "
        "Get your free API key at https://umlforge.dev"
    )


def _pending_message(job_id: str) -> str:
    return (
        f"**UML Forge: still generating** (job `{job_id}`).\n\n"
        f'Call `umlforge_get_result(job_id="{job_id}")` to retrieve the result. '
        "Generation usually finishes within a minute or two, and results are kept "
        "for one hour."
    )


def _job_error_message(error: dict) -> str:
    status = error.get("status", 500)
    detail = error.get("detail")
    if isinstance(detail, dict):
        message = detail.get("error") or detail.get("message") or str(detail)
    else:
        message = str(detail) if detail else "Generation failed."
    if status == 402:
        upgrade = (detail or {}).get("upgrade_url", "https://umlforge.dev/billing") \
            if isinstance(detail, dict) else "https://umlforge.dev/billing"
        return f"**Monthly diagram limit reached.**\n\n{message}\n\nUpgrade at: {upgrade}"
    if status == 429:
        return f"**UML Forge: request limit reached.** {message}"
    if status == 504:
        return "**UML Forge: the AI service timed out.** Please try again in a moment."
    if status == 422:
        return f"**UML Forge: the request was not valid.** {message}"
    return f"**UML Forge: generation failed** ({status}). {message}"


async def _await_job(job_id: str, budget_seconds: float) -> str:
    """Poll a job for up to budget_seconds; return the result, an error, or a pending note."""
    config = load_config()
    if not config.api_key:
        return _missing_key_message()

    loop = asyncio.get_running_loop()
    deadline = loop.time() + budget_seconds
    while True:
        remaining = deadline - loop.time()
        wait = int(max(0, min(_POLL_SLICE_SECONDS, remaining)))
        try:
            async with httpx.AsyncClient(timeout=wait + 15.0) as client:
                response = await client.get(
                    f"{config.api_base_url}/v1/jobs/{job_id}",
                    params={"wait": wait},
                    headers=_headers(config.api_key),
                )
        except httpx.TimeoutException:
            if loop.time() >= deadline:
                return _pending_message(job_id)
            continue

        if response.status_code == 401:
            return (
                "**Authentication failed.** Check that your API key in "
                "your UMLFORGE_API_KEY is correct and active."
            )
        if response.status_code == 404:
            return (
                f"**UML Forge: job `{job_id}` was not found.** It may have expired "
                "(results are kept for one hour). Run the generation again."
            )
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            return _failure_message(exc)

        body = response.json()
        state = body.get("status")
        if state == "done":
            return _format_generate_response(body["result"])
        if state == "error":
            return _job_error_message(body.get("error", {}))
        if loop.time() >= deadline - 0.5:
            return _pending_message(job_id)


async def generate_job(
    tool: str,
    params: dict,
    guided_mode: bool = False,
) -> str:
    """
    Run a generation through the job API (POST /v1/jobs), waiting up to the wait
    budget for the result. Falls back to the synchronous endpoint on a server that
    has no job API.
    """
    config = load_config()
    if not config.api_key:
        return _missing_key_message()

    if params.get("report_mode") is None:
        params = {k: v for k, v in params.items() if k != "report_mode"}

    try:
        async with httpx.AsyncClient(timeout=_JOB_START_TIMEOUT) as client:
            response = await client.post(
                f"{config.api_base_url}/v1/jobs",
                json={
                    "tool": tool,
                    "params": params,
                    "guided_mode": guided_mode and config.guided_mode,
                },
                headers=_headers(config.api_key),
            )
    except httpx.TimeoutException as exc:
        return _failure_message(exc)

    if response.status_code in (404, 405, 501):
        try:
            known_tool_error = "available_tools" in str(response.json())
        except ValueError:
            known_tool_error = False
        if not known_tool_error:
            # Server predates the job API: use the synchronous endpoint
            return await generate(tool, params, guided_mode)

    if response.status_code >= 500:
        # Starting a job does no LLM work, so a 5xx here means the job API itself is
        # unavailable (for example mid-deploy). The synchronous endpoint still works.
        return await generate(tool, params, guided_mode)

    if response.status_code == 401:
        return (
            "**Authentication failed.** Check that your API key in "
            "your UMLFORGE_API_KEY is correct and active."
        )
    if response.status_code != 202:
        # 402 / 429 / 404 (unknown tool) / 5xx come back as the same errors /v1/generate gives
        try:
            error = response.json()
        except ValueError:
            error = {}
        detail = error.get("detail", error) if isinstance(error, dict) else error
        if response.status_code == 402 and isinstance(error, dict):
            detail = error
        if response.status_code in (402, 404, 422, 429):
            return _job_error_message({"status": response.status_code, "detail": detail})
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            return _failure_message(exc)

    job_id = response.json()["job_id"]
    return await _await_job(job_id, _wait_budget())


async def get_result(job_id: str) -> str:
    """Retrieve (waiting up to the wait budget) the result of a started generation."""
    return await _await_job(job_id.strip(), _wait_budget())


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
