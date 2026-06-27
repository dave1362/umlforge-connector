"""
UML Forge Connector — MCP Tool Definitions

Registers all 13 UML Forge tools with the FastMCP server.

CRITICAL CONSTRAINTS (enforced by architecture):
  - ZERO business logic in this file
  - ZERO prompt text in this file
  - NO Anthropic API calls
  - Every tool body is a single call to api_client.generate() or api_client.suggest()

The tool docstrings are what coding agents (Claude Code, Cursor, etc.) read
to decide which tool to call — write them clearly and specifically.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from connector import api_client
from connector.config import load_config

mcp = FastMCP("umlforge_mcp")

_READ_ONLY = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=True,
)


# ── 1. Reverse Engineer ────────────────────────────────────────────────────────

@mcp.tool(annotations=_READ_ONLY)
async def umlforge_reverse_engineer(
    codebase: str = "",
    github_url: str | None = None,
    max_nodes: int = 20,
    report_mode: bool = False,
) -> str:
    """
    Reverse-engineer a codebase into UML class, sequence, and state diagrams.

    Analyses the provided code and produces:
    - Class diagram: entities, attributes, relationships, multiplicities
    - Sequence diagram: primary execution flow or dominant use case
    - State diagram: entity lifecycle (if stateful entities are found)
    - Architectural smell flags: god classes, circular deps, anemic models

    Pro/Team/Enterprise: set report_mode=True to also receive an Architectural
    Intelligence Report — a plain-English document with system overview,
    key findings, modernisation recommendations, and a health score (A-F).

    Best for: legacy system audits, onboarding, code review preparation,
    technical debt assessment.

    Provide EITHER codebase OR github_url — not required to supply both.

    Args:
        codebase: Code snippets, file contents, or structured description
                  of the codebase. Use this when you have code in context
                  or want to paste specific files.
        github_url: Public GitHub URL — the server fetches the code for you.
                    Accepted formats:
                      github.com/owner/repo
                      github.com/owner/repo/tree/branch/path/to/dir
                      github.com/owner/repo/blob/branch/path/to/file.py
                    Only provide URLs to repositories you have the right
                    to analyse (public repos or repos you own/have access to).
        max_nodes: Maximum classes/components per diagram (default 20).
                   Increase for large codebases; decrease for readability.
        report_mode: When True, generate an Architectural Intelligence Report
                     alongside the diagrams. Pro/Team/Enterprise tier only.
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_reverse_engineer",
        {
            "codebase": codebase,
            "github_url": github_url,
            "max_nodes": max_nodes,
            "report_mode": report_mode,
        },
        guided_mode=config.guided_mode,
    )


# ── 2. Stakeholder Architecture ───────────────────────────────────────────────

@mcp.tool(annotations=_READ_ONLY)
async def umlforge_stakeholder_arch(
    system_description: str,
    audience_description: str,
) -> str:
    """
    Generate a C4 architecture diagram (Context + Container + Component levels).

    Produces three diagrams scaled for a mixed technical/non-technical audience:
    - C4 Context: system boundary, external actors, primary integrations
    - C4 Container: deployable units, tech stack labels, communication protocols
    - C4 Component: internals of the most complex container

    Best for: investor presentations, client onboarding, architecture review boards,
    pre-demo documentation.

    Args:
        system_description: What the system does, who uses it, its major components.
        audience_description: Who will read this (e.g. "CTO and backend engineers",
                              "non-technical investors").
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_stakeholder_arch",
        {
            "system_description": system_description,
            "audience_description": audience_description,
        },
        guided_mode=config.guided_mode,
    )


# ── 3. API Sequence ───────────────────────────────────────────────────────────

@mcp.tool(annotations=_READ_ONLY)
async def umlforge_api_sequence(
    services: str,
    user_journey: str,
) -> str:
    """
    Generate a detailed sequence diagram for an API or microservices interaction.

    Produces:
    - Sequence diagram: happy path + at least 2 failure/exception paths,
      activation boxes, sync vs async arrows, performance boundary annotation
    - Inter-service dependency table: caller, callee, protocol, failure mode, mitigation

    Best for: new service integration design, API contract definition,
    QA test planning, incident post-mortems.

    Args:
        services: Participants in the interaction, e.g.
                  "API Gateway, Auth Service, Order Service, Payment Provider, User DB".
        user_journey: The user action or flow to diagram in plain English,
                      e.g. "User places an order through checkout".
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_api_sequence",
        {"services": services, "user_journey": user_journey},
        guided_mode=config.guided_mode,
    )


# ── 4. State Machine ──────────────────────────────────────────────────────────

@mcp.tool(annotations=_READ_ONLY)
async def umlforge_state_machine(
    entity: str,
    states: str,
    events: str,
    business_rules: str = "",
) -> str:
    """
    Design a state machine diagram for a complex domain entity.

    Produces:
    - stateDiagram-v2: all states with entry/exit actions, transitions with
      guard conditions, composite states, explicit ERROR and TERMINAL states
    - State transition table: current state → event → guard → next state → action
    - Implementation notes: which transitions need DB writes, domain events,
      and race condition guards
    - Assumption flags for any ambiguous business rules

    Best for: domain-driven design, workflow/approval systems, order/job lifecycle,
    IoT device management.

    Args:
        entity: Domain entity name (e.g. "Order", "Subscription", "JobApplication").
        states: Known lifecycle states (e.g. "pending, active, suspended, cancelled").
        events: Triggers that cause state transitions (e.g. "payment_received, user_cancels").
        business_rules: Constraints on transitions (optional).
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_state_machine",
        {
            "entity": entity,
            "states": states,
            "events": events,
            "business_rules": business_rules,
        },
        guided_mode=config.guided_mode,
    )


# ── 5. Living Docs ────────────────────────────────────────────────────────────

@mcp.tool(annotations=_READ_ONLY)
async def umlforge_living_docs(
    current_diagrams: str,
    sprint_changes: str,
    affected_files: str = "",
) -> str:
    """
    Update existing UML diagrams to reflect sprint or PR changes.

    Diffs your current diagrams against described changes and produces:
    - Updated diagrams only for affected sections (with %% changelog headers)
    - New diagrams for any newly introduced architectural patterns
    - Architecture evolution note suitable for pasting into a project wiki
    - Explicit flags for intentionally removed nodes/relationships

    Best for: sprint retrospectives, PR documentation, wiki maintenance,
    architecture changelog management.

    Args:
        current_diagrams: Existing Mermaid diagram(s) to update — paste the
                          full content including ```mermaid fences.
        sprint_changes: What changed: new components, removed flows, renamed
                        services, modified behaviour.
        affected_files: Files or modules touched in this sprint/PR (optional).
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_living_docs",
        {
            "current_diagrams": current_diagrams,
            "sprint_changes": sprint_changes,
            "affected_files": affected_files,
        },
        guided_mode=config.guided_mode,
    )


# ── 6. ERD & Schema ───────────────────────────────────────────────────────────

@mcp.tool(annotations=_READ_ONLY)
async def umlforge_erd_schema(
    domain_description: str,
    entities: str,
    access_patterns: str = "",
    db_technology: str = "PostgreSQL",
) -> str:
    """
    Design a database ERD with schema narrative and integrity checklist.

    Produces:
    - erDiagram: all entities with typed attributes, relationships, cardinality,
      and foreign key labels
    - Schema narrative: one paragraph per entity — business purpose, index
      recommendations, denormalisation decisions
    - Data integrity checklist: uniqueness, FK integrity, null policies, constraints
    - Performance risk flags for N+1 query patterns

    Best for: new feature schema design, migration planning, ORM model definition,
    data architecture reviews.

    Args:
        domain_description: What the database stores (e.g. "E-commerce platform:
                            users, products, orders, payments").
        entities: Known entities and key attributes (e.g. "User(id, email, tier),
                  Order(id, user_id, status, total)").
        access_patterns: Most frequent read/write operations (optional, used
                         for index recommendations).
        db_technology: Database technology — PostgreSQL, MySQL, MongoDB, etc.
                       (default: PostgreSQL).
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_erd_schema",
        {
            "domain_description": domain_description,
            "entities": entities,
            "access_patterns": access_patterns,
            "db_technology": db_technology,
        },
        guided_mode=config.guided_mode,
    )


# ── 7. Threat Model ───────────────────────────────────────────────────────────

@mcp.tool(annotations=_READ_ONLY)
async def umlforge_threat_model(
    system_description: str,
    auth_mechanism: str,
    trust_boundaries: list[str] | None = None,
    sensitive_data: list[str] | None = None,
    compliance_framework: str | None = None,
    report_mode: bool = False,
) -> str:
    """
    Generate a security threat model with full STRIDE analysis.

    Produces:
    - Authentication flow sequence diagram with trust boundary annotations and
      all failure paths (invalid creds, expired token, insufficient permissions)
    - Data flow diagram with sensitivity labels (PUBLIC/INTERNAL/CONFIDENTIAL/SECRET)
    - STRIDE threat table: all 6 categories with likelihood, mitigation, status
    - Critical flags (🚨) for unencrypted sensitive data flows and high-risk gaps

    Pro/Team/Enterprise: set report_mode=True to also receive a Security Assessment
    Report — an executive summary, threat landscape in plain English, critical
    vulnerability deep-dives, compliance status, remediation roadmap, and risk score.

    Best for: pre-production security reviews, auth flow design,
    compliance documentation (GDPR, NDPA 2023, SOC2, PCI-DSS),
    penetration test preparation.

    Args:
        system_description: What the system does, how users access it, main components.
        auth_mechanism: Authentication in use (e.g. "JWT Bearer token", "API Key",
                        "OAuth2 + PKCE").
        trust_boundaries: Trust boundary crossings (e.g. ["public internet → API",
                          "API → database"]).
        sensitive_data: Sensitive data types (e.g. ["user emails", "payment tokens"]).
        compliance_framework: Compliance scope (e.g. "GDPR", "NDPA 2023", "PCI-DSS").
        report_mode: When True, generate a Security Assessment Report alongside
                     the diagrams. Pro/Team/Enterprise tier only.
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_threat_model",
        {
            "system_description": system_description,
            "auth_mechanism": auth_mechanism,
            "trust_boundaries": trust_boundaries or [],
            "sensitive_data": sensitive_data or [],
            "compliance_framework": compliance_framework,
            "report_mode": report_mode,
        },
        guided_mode=config.guided_mode,
    )


# ── 8. Frontend Components ────────────────────────────────────────────────────

@mcp.tool(annotations=_READ_ONLY)
async def umlforge_frontend_components(
    feature_description: str,
    framework: str = "React",
    state_management: str = "",
    interactions: str = "",
) -> str:
    """
    Generate a frontend component architecture diagram.

    Produces:
    - Component hierarchy graph: parent-child relationships, props (downward),
      events/callbacks (upward), state store connections (dashed), API call origins
    - Interaction sequence diagram: most complex user interaction — loading,
      success, and error states
    - Component responsibility table: responsibilities, state owned, reusability
    - Accessibility note: ARIA roles needed, keyboard navigation, WCAG risks
    - God component flags (⚠️) for components with too many responsibilities

    Best for: new feature UI design, design system development,
    component library documentation, frontend architecture reviews.

    Args:
        feature_description: The UI feature or page to diagram.
        framework: Frontend framework — React, Vue, Angular, Svelte, Next.js, etc.
                   (default: React).
        state_management: State approach — Redux, Zustand, Context API, Pinia, etc.
                          (optional).
        interactions: Key user interactions (optional, improves diagram quality).
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_frontend_components",
        {
            "feature_description": feature_description,
            "framework": framework,
            "state_management": state_management,
            "interactions": interactions,
        },
        guided_mode=config.guided_mode,
    )


# ── 9. Event-Driven ───────────────────────────────────────────────────────────

@mcp.tool(annotations=_READ_ONLY)
async def umlforge_event_driven(
    system_context: str,
    producers: str,
    consumers: str,
    broker: str = "",
    events: str = "",
) -> str:
    """
    Design an event-driven or async system architecture.

    Produces:
    - Event flow sequence diagram: producers → broker → consumers with ack,
      retry loops, and dead-letter queue handling
    - Event catalogue table: name, producer, consumers, payload, ordering,
      idempotency, retention
    - Choreography vs orchestration assessment with coupling risk flags
    - Failure mode analysis table: scenario, impact, detection, recovery

    Best for: event sourcing design, CQRS, microservices decoupling,
    message broker integration, async workflow design.

    Args:
        system_context: What the event-driven system does and why it uses messaging.
        producers: Services that emit events (e.g. "Order Service emits order.placed").
        consumers: Services that consume events (e.g. "Notification, Inventory, Analytics").
        broker: Message broker (e.g. "Kafka", "RabbitMQ", "AWS SQS/SNS") (optional).
        events: Named domain events (e.g. "order.placed, payment.failed") (optional).
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_event_driven",
        {
            "system_context": system_context,
            "producers": producers,
            "consumers": consumers,
            "broker": broker,
            "events": events,
        },
        guided_mode=config.guided_mode,
    )


# ── 10. Team Onboarding ───────────────────────────────────────────────────────

@mcp.tool(annotations=_READ_ONLY)
async def umlforge_onboarding(
    system_description: str,
    tech_stack: str,
    key_workflows: str,
    pain_points: str = "",
) -> str:
    """
    Generate a complete team onboarding and knowledge-transfer diagram package.

    Produces four diagrams plus a gotchas table:
    - System overview (C4 Container): the lay-of-the-land on day one
    - Developer workflow sequence: local dev → test → CI → staging → production,
      plus the most common debugging path
    - Data lifecycle (activity diagram): how data enters, transforms, stores, deletes
    - Module dependency map: internal modules + external deps, circular dep flags
    - Gotchas & constraints table: what the code does, why it does it that way,
      what breaks if you change it

    Best for: developer onboarding, module handover, team scaling,
    documentation-before-departure.

    Args:
        system_description: High-level description of the system being handed over.
        tech_stack: Languages, frameworks, and infrastructure (e.g. "FastAPI,
                    PostgreSQL, React, Redis, Railway").
        key_workflows: 2-3 most important flows a new developer must understand.
        pain_points: Known gotchas, non-obvious decisions, workarounds (optional).
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_onboarding",
        {
            "system_description": system_description,
            "tech_stack": tech_stack,
            "key_workflows": key_workflows,
            "pain_points": pain_points,
        },
        guided_mode=config.guided_mode,
    )


# ── 11. AI Agent ──────────────────────────────────────────────────────────────

@mcp.tool(annotations=_READ_ONLY)
async def umlforge_ai_agent(
    pipeline_purpose: str,
    agents: str,
    tools_available: str = "",
    orchestration_approach: str = "",
    memory_strategy: str = "",
) -> str:
    """
    Design an AI agent and orchestration pipeline architecture.

    Produces:
    - Agent pipeline sequence diagram: agents as participants with model names,
      tool calls as self-calls, human-in-the-loop gates, retry/fallback logic
    - Agent component map: agents, tool deps, memory components, external integrations
    - Agent responsibility matrix: model, role, tools, inputs, outputs, failure behaviour
    - Risk & observability note: hallucination hotspots, validation gates, logging points
    - Tool overload flags (⚠️) for agents with more than 5 tools

    Best for: multi-agent system design, LLM pipeline architecture,
    AI product development, agentic workflow documentation.

    Args:
        pipeline_purpose: What the agent system does (e.g. "Research pipeline that
                          searches the web and drafts a report").
        agents: Agents in the pipeline and their roles (e.g. "Planner Agent
                [claude-opus-4], Research Agent [claude-sonnet-4]").
        tools_available: Tools agents can call (e.g. "web_search, execute_code") (optional).
        orchestration_approach: How agents coordinate — sequential, DAG, hierarchical,
                                parallel fan-out (optional).
        memory_strategy: Memory approach — shared context, vector memory, Redis,
                         none (optional).
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_ai_agent",
        {
            "pipeline_purpose": pipeline_purpose,
            "agents": agents,
            "tools_available": tools_available,
            "orchestration_approach": orchestration_approach,
            "memory_strategy": memory_strategy,
        },
        guided_mode=config.guided_mode,
    )


# ── 12. Deployment ────────────────────────────────────────────────────────────

@mcp.tool(annotations=_READ_ONLY)
async def umlforge_deployment(
    system_name: str,
    cloud_provider: str,
    environments: str,
    services: str,
    cicd_tool: str = "",
) -> str:
    """
    Generate a deployment topology and CI/CD pipeline diagram.

    Produces:
    - Deployment diagram: nodes, artefacts, network paths with protocol/port labels,
      internet-facing vs internal traffic distinction
    - CI/CD pipeline flow: all stages from commit to production, automated gates,
      manual approvals, rollback paths, environment promotion sequence
    - Deployment environment table: infrastructure, triggers, data classification,
      monitoring, rollback strategy per environment
    - Infrastructure risk note: single points of failure, missing redundancy,
      environment parity gaps
    - Observability gap flags (⚠️) for services without /health endpoints

    Best for: infrastructure provisioning, CI/CD pipeline design, cloud architecture
    documentation, DevOps handover, disaster recovery planning.

    Args:
        system_name: Name of the system (e.g. "UML Forge API").
        cloud_provider: Cloud provider(s) (e.g. "AWS", "Railway + Vercel", "GCP").
        environments: Deployment environments (e.g. "development, staging, production").
        services: Services and infrastructure to deploy (e.g. "FastAPI API, Next.js
                  frontend, PostgreSQL, Redis").
        cicd_tool: CI/CD pipeline tool (e.g. "GitHub Actions", "GitLab CI") (optional).
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_deployment",
        {
            "system_name": system_name,
            "cloud_provider": cloud_provider,
            "environments": environments,
            "services": services,
            "cicd_tool": cicd_tool,
        },
        guided_mode=config.guided_mode,
    )


# ── 13. Suggest ───────────────────────────────────────────────────────────────

@mcp.tool(annotations=_READ_ONLY)
async def umlforge_suggest(task_description: str) -> str:
    """
    Recommend the best UML Forge tool for your task.

    Given a plain-English description of what you want to diagram,
    returns a ranked recommendation with reasoning and an alternative option.

    Use this when you are not sure which of the 12 diagram tools fits
    your task best.

    Args:
        task_description: Plain-English description of what you want to diagram
                          (e.g. "I want to document the lifecycle of an order"
                          or "I need to show how our auth service works").
    """
    return await api_client.suggest(task_description)
