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
    Analyse an existing codebase and produce UML class, sequence, and state diagrams.

    USE THIS WHEN:
    - You have a GitHub URL and want to understand what the code does
    - You want to audit a codebase for architectural problems
    - You need diagrams of code that already exists (your own or a public repo)
    - You want an Architectural Intelligence Report on any codebase

    NOT FOR:
    - Designing a new system from scratch → use umlforge_stakeholder_arch
    - Updating diagrams after a sprint → use umlforge_living_docs
    - Documenting database schema → use umlforge_erd_schema
    - Mapping how services call each other → use umlforge_api_sequence

    Produces:
    - Class diagram: entities, attributes, relationships, multiplicities
    - Sequence diagram: primary execution flow or dominant use case
    - State diagram: entity lifecycle (if stateful entities are detected)
    - Architectural smell flags: god classes, circular deps, anemic models
    - (report_mode=True) Architectural Intelligence Report: system overview,
      key findings, modernisation roadmap, health scores (A–F)

    Provide EITHER github_url OR codebase — not both.

    Args:
        github_url: Public GitHub URL. Accepted formats:
                      github.com/owner/repo
                      github.com/owner/repo/tree/branch/path/to/dir
                      github.com/owner/repo/blob/branch/path/to/file.py
        codebase: Paste code directly when you have files in context
                  or the repo is private.
        max_nodes: Max classes/components per diagram (default 20).
        report_mode: True → also produce an Architectural Intelligence Report.
                     Pro/Team/Enterprise only.
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
    report_mode: bool = False,
) -> str:
    """
    Generate a C4 architecture diagram for a mixed technical/non-technical audience.

    USE THIS WHEN:
    - You are designing or presenting a system to stakeholders (CTO, investors, board)
    - You need a high-level picture of a system you are planning or explaining
    - You want Context + Container + Component diagrams in one call

    NOT FOR:
    - Analysing code that already exists → use umlforge_reverse_engineer
    - Tracing a specific API request across services → use umlforge_api_sequence
    - Infrastructure and deployment topology → use umlforge_deployment
    - Security threat modelling → use umlforge_threat_model

    Produces:
    - C4 Context: system boundary, external actors, primary integrations
    - C4 Container: deployable units, tech stack labels, communication protocols
    - C4 Component: internals of the most complex container
    - (report_mode=True) Architecture Communication Notes: audience fit,
      communication gaps, clarity quick wins

    Args:
        system_description: What the system does, who uses it, its major components.
        audience_description: Who will read this (e.g. "CTO and non-technical board",
                              "backend engineers new to the system").
        report_mode: True → also produce Architecture Communication Notes.
                     Pro/Team/Enterprise only.
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_stakeholder_arch",
        {
            "system_description": system_description,
            "audience_description": audience_description,
            "report_mode": report_mode,
        },
        guided_mode=config.guided_mode,
    )


# ── 3. API Sequence ───────────────────────────────────────────────────────────

@mcp.tool(annotations=_READ_ONLY)
async def umlforge_api_sequence(
    services: str,
    user_journey: str,
    report_mode: bool = False,
) -> str:
    """
    Diagram how services call each other for a specific user action or API flow.

    USE THIS WHEN:
    - You want to trace a request across multiple services (e.g. "user logs in")
    - You are designing API contracts between microservices
    - You need to show failure paths, retries, and error handling between services
    - You are writing QA test cases or doing incident post-mortems

    NOT FOR:
    - Full codebase analysis → use umlforge_reverse_engineer
    - Async/event-driven messaging → use umlforge_event_driven
    - Frontend component interactions → use umlforge_frontend_components
    - Database schema design → use umlforge_erd_schema

    Produces:
    - Sequence diagram: happy path + at least 2 failure paths, activation boxes,
      sync vs async arrows, performance boundary annotations
    - Inter-service dependency table: caller, callee, protocol, failure mode, mitigation
    - (report_mode=True) Design Score: Resilience, Performance, Contract Clarity (A–F)

    Args:
        services: All participants, e.g.
                  "API Gateway, Auth Service, Order Service, Payment Provider, User DB".
        user_journey: The action to diagram in plain English,
                      e.g. "User places an order through checkout".
        report_mode: True → also produce a Design Score report.
                     Pro/Team/Enterprise only.
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_api_sequence",
        {"services": services, "user_journey": user_journey, "report_mode": report_mode},
        guided_mode=config.guided_mode,
    )


# ── 4. State Machine ──────────────────────────────────────────────────────────

@mcp.tool(annotations=_READ_ONLY)
async def umlforge_state_machine(
    entity: str,
    states: str,
    events: str,
    business_rules: str = "",
    report_mode: bool = False,
) -> str:
    """
    Design a state machine for a domain entity that has a lifecycle.

    USE THIS WHEN:
    - An entity moves through states (Order: pending → active → cancelled)
    - You need to model a workflow, approval chain, or subscription lifecycle
    - You want to find missing states, invalid transitions, or race conditions

    NOT FOR:
    - Flows between services (requests, responses) → use umlforge_api_sequence
    - Async event messaging between services → use umlforge_event_driven
    - Full codebase analysis → use umlforge_reverse_engineer

    Produces:
    - stateDiagram-v2: all states, entry/exit actions, guard conditions,
      composite states, explicit ERROR and TERMINAL states
    - State transition table: current state → event → guard → next state → action
    - Implementation notes: DB write requirements, domain events, race condition guards
    - (report_mode=True) Analysis Notes: transition risks, unreachable states, quick wins

    Args:
        entity: The domain entity (e.g. "Order", "Subscription", "JobApplication").
        states: Known lifecycle states (e.g. "pending, active, suspended, cancelled").
        events: Triggers that cause transitions (e.g. "payment_received, user_cancels").
        business_rules: Constraints on transitions (optional).
        report_mode: True → also produce State Machine Analysis Notes.
                     Pro/Team/Enterprise only.
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_state_machine",
        {
            "entity": entity,
            "states": states,
            "events": events,
            "business_rules": business_rules,
            "report_mode": report_mode,
        },
        guided_mode=config.guided_mode,
    )


# ── 5. Living Docs ────────────────────────────────────────────────────────────

@mcp.tool(annotations=_READ_ONLY)
async def umlforge_living_docs(
    current_diagrams: str,
    sprint_changes: str,
    affected_files: str = "",
    report_mode: bool = False,
) -> str:
    """
    Update diagrams you already have to reflect what changed in a sprint or PR.

    USE THIS WHEN:
    - You ALREADY HAVE Mermaid diagrams (from a previous generation or your own)
    - Code has changed in a sprint or PR and your diagrams are now out of date
    - You want a changelog-annotated diff of your diagrams

    NOT FOR:
    - Generating diagrams for the first time → use umlforge_reverse_engineer
      (for existing codebases) or umlforge_stakeholder_arch (for new designs)
    - Analysing a GitHub URL → use umlforge_reverse_engineer instead
    - Generating diagrams without existing ones to update → use any other tool

    IMPORTANT: current_diagrams is REQUIRED — paste your existing Mermaid
    diagrams (including the ```mermaid fences). This tool cannot generate
    from scratch.

    Produces:
    - Updated diagrams for affected sections only (with %% changelog headers)
    - New diagrams for newly introduced patterns
    - Architecture evolution note for pasting into a wiki
    - (report_mode=True) Documentation Analysis Notes: change impact, drift risks,
      coverage quick wins

    Args:
        current_diagrams: Your existing Mermaid diagram(s) — paste the full
                          content including ```mermaid fences. REQUIRED.
        sprint_changes: What changed this sprint: new components, removed flows,
                        renamed services, modified behaviour.
        affected_files: Files or modules touched in this sprint/PR (optional).
        report_mode: True → also produce Documentation Analysis Notes.
                     Pro/Team/Enterprise only.
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_living_docs",
        {
            "current_diagrams": current_diagrams,
            "sprint_changes": sprint_changes,
            "affected_files": affected_files,
            "report_mode": report_mode,
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
    report_mode: bool = False,
) -> str:
    """
    Design a database schema with ERD, integrity rules, and index recommendations.

    USE THIS WHEN:
    - You are designing or reviewing a database schema
    - You need an ERD with foreign keys, cardinality, and data types
    - You want index recommendations and N+1 risk flags

    NOT FOR:
    - Full codebase analysis (which may include DB) → use umlforge_reverse_engineer
    - API flows between services → use umlforge_api_sequence
    - Event-driven data pipelines → use umlforge_event_driven

    Produces:
    - erDiagram: entities with typed attributes, cardinality, FK labels
    - Schema narrative: one paragraph per entity — purpose, index recommendations,
      denormalisation decisions
    - Data integrity checklist: uniqueness, FK integrity, null policies, constraints
    - N+1 query risk flags
    - (report_mode=True) Design Score: Normalisation, Query Performance,
      Data Integrity (A–F)

    Args:
        domain_description: What the database stores
                            (e.g. "E-commerce: users, products, orders, payments").
        entities: Known entities and key attributes
                  (e.g. "User(id, email, tier), Order(id, user_id, status, total)").
        access_patterns: Most frequent read/write queries (optional — used for
                         index recommendations).
        db_technology: Database technology (default: PostgreSQL).
        report_mode: True → also produce a Design Score report.
                     Pro/Team/Enterprise only.
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_erd_schema",
        {
            "domain_description": domain_description,
            "entities": entities,
            "access_patterns": access_patterns,
            "db_technology": db_technology,
            "report_mode": report_mode,
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
    Generate a full STRIDE security threat model for a system.

    USE THIS WHEN:
    - You want to identify security vulnerabilities before launch
    - You need to document auth flows, trust boundaries, or sensitive data handling
    - You are preparing for a penetration test or compliance audit (GDPR, SOC2, PCI-DSS)

    NOT FOR:
    - General architecture review → use umlforge_reverse_engineer with report_mode=True
    - Deployment and infrastructure topology → use umlforge_deployment
    - API flow design (without security focus) → use umlforge_api_sequence

    Produces:
    - Auth flow sequence diagram: all failure paths, trust boundary annotations
    - Data flow diagram: sensitivity labels (PUBLIC / INTERNAL / CONFIDENTIAL / SECRET)
    - STRIDE threat table: all 6 categories with likelihood, mitigation, status
    - Critical flags (🚨) for high-risk gaps
    - (report_mode=True) Security Assessment Report: threat landscape, critical
      vulnerability deep-dives, compliance status, remediation roadmap, risk score

    Args:
        system_description: What the system does, how users access it, main components.
        auth_mechanism: Auth in use (e.g. "JWT Bearer token", "API Key", "OAuth2 + PKCE").
        trust_boundaries: Boundary crossings (e.g. ["public internet → API",
                          "API → database"]) (optional).
        sensitive_data: Sensitive data types (e.g. ["user emails", "payment tokens"])
                        (optional).
        compliance_framework: Compliance scope (e.g. "GDPR", "NDPA 2023", "PCI-DSS")
                              (optional).
        report_mode: True → also produce a Security Assessment Report.
                     Pro/Team/Enterprise only.
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
    report_mode: bool = False,
) -> str:
    """
    Design a frontend component tree and interaction flow for a UI feature.

    USE THIS WHEN:
    - You are designing or documenting a React, Vue, Angular, or Svelte feature
    - You want to see component hierarchy, props flow, and state management
    - You need to identify god components or prop drilling issues

    NOT FOR:
    - Backend service interactions → use umlforge_api_sequence
    - Full codebase including frontend → use umlforge_reverse_engineer
    - Overall system architecture for stakeholders → use umlforge_stakeholder_arch

    Produces:
    - Component hierarchy graph: parent-child, props (downward arrows),
      events/callbacks (upward dashed arrows), state store connections, API origins
    - Interaction sequence diagram: most complex user flow — loading, success, error
    - Component responsibility table: responsibilities, state owned, reusability flag
    - Accessibility note: ARIA roles needed, keyboard nav, WCAG risks
    - God component flags (⚠️) for components with too many responsibilities
    - (report_mode=True) Component Analysis Notes: coupling risks, refactoring quick wins

    Args:
        feature_description: The UI feature or page to diagram.
        framework: Frontend framework (default: React).
        state_management: State approach — Redux, Zustand, Context API, Pinia (optional).
        interactions: Key user interactions (optional — improves sequence diagram).
        report_mode: True → also produce Component Analysis Notes.
                     Pro/Team/Enterprise only.
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_frontend_components",
        {
            "feature_description": feature_description,
            "framework": framework,
            "state_management": state_management,
            "interactions": interactions,
            "report_mode": report_mode,
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
    report_mode: bool = False,
) -> str:
    """
    Design an event-driven or async messaging architecture (Kafka, SQS, RabbitMQ, etc.).

    USE THIS WHEN:
    - Services communicate via events or messages (not direct API calls)
    - You are designing event sourcing, CQRS, or pub/sub patterns
    - You want to model producer → broker → consumer flows with failure handling

    NOT FOR:
    - Synchronous REST/gRPC calls between services → use umlforge_api_sequence
    - Entity lifecycle (Order goes pending → active) → use umlforge_state_machine
    - Full system architecture overview → use umlforge_stakeholder_arch

    Produces:
    - Event flow sequence: producers → broker → consumers with ack,
      retry loops (max N), dead-letter queue handling
    - Event catalogue table: name, producer, consumers, payload, idempotency, retention
    - Choreography vs orchestration assessment with coupling risk flags
    - Failure mode analysis: scenario, impact, detection, recovery
    - (report_mode=True) Event System Analysis Notes: reliability risks,
      idempotency gaps, resilience quick wins

    Args:
        system_context: What this event-driven system does and why it uses messaging.
        producers: Services that emit events (e.g. "Order Service emits order.placed").
        consumers: Services that consume events (e.g. "Notification, Inventory, Analytics").
        broker: Message broker (e.g. "Kafka", "RabbitMQ", "AWS SQS/SNS") (optional).
        events: Named domain events (e.g. "order.placed, payment.failed") (optional).
        report_mode: True → also produce Event System Analysis Notes.
                     Pro/Team/Enterprise only.
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
            "report_mode": report_mode,
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
    report_mode: bool = False,
) -> str:
    """
    Create a day-one knowledge-transfer package for a developer joining a team.

    USE THIS WHEN:
    - A developer is joining a new team or project and needs to get up to speed
    - You are handing off a module or system to another team
    - You want gotchas, constraints, and workflow diagrams in one package

    NOT FOR:
    - Analysing existing code for architectural problems → use umlforge_reverse_engineer
    - Designing a new system → use umlforge_stakeholder_arch
    - Documenting a specific API flow → use umlforge_api_sequence

    Produces:
    - System overview (C4 Container): the lay-of-the-land on day one
    - Developer workflow sequence: local dev → test → CI → staging → production
      + most common debugging path
    - Gotchas & constraints table: what the code does, why, what breaks if changed
    - (report_mode=True) Onboarding Analysis Notes: coverage assessment,
      knowledge gaps, documentation quick wins

    Args:
        system_description: High-level description of the system.
        tech_stack: Technologies in the stack (e.g. "FastAPI, PostgreSQL, React, Railway").
        key_workflows: 2–3 flows a new developer must understand first.
        pain_points: Known gotchas, non-obvious decisions (optional).
        report_mode: True → also produce Onboarding Analysis Notes.
                     Pro/Team/Enterprise only.
    """
    config = load_config()
    return await api_client.generate(
        "umlforge_onboarding",
        {
            "system_description": system_description,
            "tech_stack": tech_stack,
            "key_workflows": key_workflows,
            "pain_points": pain_points,
            "report_mode": report_mode,
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
    report_mode: bool = False,
) -> str:
    """
    Design an AI agent pipeline or multi-agent orchestration system.

    USE THIS WHEN:
    - You are building a system where LLMs call tools or hand off to other agents
    - You want to visualise a multi-agent workflow (planner → researcher → writer)
    - You need to document tool access, memory strategy, and failure behaviour

    NOT FOR:
    - General system architecture → use umlforge_stakeholder_arch
    - Standard synchronous API flows → use umlforge_api_sequence
    - Event-driven pipelines without LLM agents → use umlforge_event_driven

    Produces:
    - Agent pipeline sequence: agents as participants with model names,
      tool calls as self-calls, human-in-the-loop gates, retry/fallback logic
    - Agent component map: agents, tool deps, memory, external integrations
    - Agent responsibility matrix: model, role, tools, inputs, outputs, failure behaviour
    - Risk & observability note: hallucination hotspots, validation gates, logging points
    - Tool overload flags (⚠️) for agents with more than 5 tools
    - (report_mode=True) Agent Pipeline Analysis Notes: pipeline risks,
      coverage gaps, reliability quick wins

    Args:
        pipeline_purpose: What the agent system does
                          (e.g. "Research pipeline that queries the web and drafts a report").
        agents: Agents and their roles
                (e.g. "Planner [claude-opus-4], Researcher [claude-sonnet-4]").
        tools_available: Tools agents can call (e.g. "web_search, execute_code") (optional).
        orchestration_approach: Coordination strategy — sequential, DAG, hierarchical,
                                parallel fan-out (optional).
        memory_strategy: Memory approach — shared context, vector memory, Redis,
                         none (optional).
        report_mode: True → also produce Agent Pipeline Analysis Notes.
                     Pro/Team/Enterprise only.
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
            "report_mode": report_mode,
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
    report_mode: bool = False,
) -> str:
    """
    Generate a deployment topology and CI/CD pipeline diagram.

    USE THIS WHEN:
    - You want to visualise your cloud infrastructure and how services connect
    - You need to document your CI/CD pipeline from commit to production
    - You are planning infrastructure, disaster recovery, or a DevOps handover

    NOT FOR:
    - Application-level architecture (how code is structured) → use umlforge_reverse_engineer
    - Security threat modelling → use umlforge_threat_model
    - How services call each other at the API level → use umlforge_api_sequence

    Produces:
    - Deployment diagram: nodes, artefacts, network paths, protocol/port labels,
      internet-facing vs internal traffic distinction
    - CI/CD pipeline flow: commit → build → test → staging → production,
      automated gates, manual approvals, rollback paths
    - Deployment environment table: infrastructure, triggers, data classification,
      monitoring, rollback strategy per environment
    - Infrastructure risk note: SPOFs, missing redundancy, environment parity gaps
    - Observability gap flags (⚠️) for services without /health endpoints
    - (report_mode=True) Infrastructure Health Report: reliability score,
      observability score, deployment safety score (A–F)

    Args:
        system_name: Name of the system (e.g. "UML Forge API").
        cloud_provider: Cloud provider(s) (e.g. "AWS", "Railway + Vercel", "GCP").
        environments: Deployment environments (e.g. "development, staging, production").
        services: Services and infrastructure (e.g. "FastAPI API, Next.js, PostgreSQL, Redis").
        cicd_tool: CI/CD tool (e.g. "GitHub Actions", "GitLab CI") (optional).
        report_mode: True → also produce an Infrastructure Health Report.
                     Pro/Team/Enterprise only.
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
            "report_mode": report_mode,
        },
        guided_mode=config.guided_mode,
    )


# ── 13. Suggest ───────────────────────────────────────────────────────────────

@mcp.tool(annotations=_READ_ONLY)
async def umlforge_suggest(task_description: str) -> str:
    """
    *** START HERE if you are unsure which tool to use. ***

    Describe what you want to achieve in plain English. This tool will:
    1. Identify the right tool for your goal
    2. Return the EXACT tool call with parameters pre-filled — ready to execute
    3. Explain why this tool fits and suggest an alternative

    USE THIS WHEN:
    - You are not sure which of the 12 tools to use
    - You want to describe a goal ("analyse this repo", "model our order lifecycle")
      and get a ready-to-run recommendation
    - You want to avoid trial and error with the wrong tool

    Example inputs:
    - "analyse https://github.com/pallets/flask and give me an architecture report"
    - "show how our Order entity moves through states"
    - "diagram our Kafka event flow between Order, Inventory, and Notification services"
    - "I have existing diagrams and my sprint changed the auth service"

    The response will include the exact tool name, all parameters pre-filled with
    values derived from your description, and a one-line explanation.

    Args:
        task_description: Plain-English description of what you want to achieve.
                          Include any relevant details: URLs, entity names, service
                          names, tech stack — the more context, the better the
                          pre-filled parameters.
    """
    return await api_client.suggest(task_description)
