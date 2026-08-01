# ClubConnect AI Assistant — Documentation

## What This Is

This package contains the complete documentation for the **ClubConnect AI Assistant**, the AI Services Module of the ClubConnect university club management platform. It covers the assistant's architecture, its runtime behavior rules, and its retrieval knowledge base (RAG corpus).

This documentation is the source of truth for implementing, maintaining, and extending the AI Services Module. It is written for developers building the intent router, SQL context builder, RAG retriever, prompt builder, and Gemini/LLM integration described in the architecture.

## Purpose

- Give developers a single, organized reference for how the ClubConnect AI Assistant is designed to behave and what knowledge it draws on.
- Separate **how the assistant should act** (System Documents) from **what the assistant knows** (RAG Documents), so each can be maintained independently.
- Provide a clear onboarding path for anyone joining the project.

## High-Level AI Architecture Overview

The ClubConnect AI Assistant is a shared AI service layered across every platform module (Student, Club Operations, Treasurer, Faculty, University Administration). At runtime, a user message is classified into an intent, authorized against the user's role, enriched with SQL context and/or retrieved documentation, assembled into a prompt, sent to the LLM provider (Gemini, with Groq/OpenRouter as alternates), and returned as a formatted response. Full architectural detail — module design, intent catalog, workflow diagrams — lives in `Architecture/ClubConnect_AI_Architecture_V2.md`.

## Architecture vs. System Documents vs. RAG Documents

| Category | What it contains | Loaded when |
|---|---|---|
| **Architecture** | The finalized design of the whole AI Services Module — module structure, intent catalog, workflows, integrations. The source of truth all other documents implement. | Reference material for developers; not injected into the LLM at runtime. |
| **System Documents** | Rules for how the assistant behaves — identity, tone, refusals, escalation, recommendation logic, dashboard redundancy handling. | Always injected into every LLM call, regardless of user intent. |
| **RAG Documents** | Platform knowledge the assistant can retrieve — how workflows and processes work (memberships, events, rewards, governance, support, finance). | Retrieved on demand, only when the detected intent needs process knowledge. |

## Folder Structure

```
ClubConnect_AI_Documentation/
│
├── README.md                          ← this file
├── Documentation_Guide.md             ← internal developer guide
│
├── Architecture/                      ← source-of-truth design doc (placed manually)
│
├── System_Documents/                  ← always-injected behavior rules
│   ├── assistant_conversation_behavior.md
│   ├── recommendation_logic_playbook.md
│   └── dashboard_redundancy_map.md
│
└── RAG_Documents/                     ← retrieval corpus
    ├── platform_getting_started.md
    ├── membership_process_guide.md
    ├── event_lifecycle_guide.md
    ├── rewards_system_guide.md
    ├── club_creation_governance_guide.md
    ├── helpdesk_support_guide.md
    └── financial_operations_guide.md
```

## Recommended Reading Order for New Developers

1. **This README** — orientation.
2. **`Architecture/ClubConnect_AI_Architecture_V2.md`** — the overall design; read this in full before anything else.
3. **`System_Documents/assistant_conversation_behavior.md`** — the assistant's core behavior rules.
4. **`System_Documents/recommendation_logic_playbook.md`** and **`dashboard_redundancy_map.md`** — the two specialized behavior rule sets.
5. **`RAG_Documents/platform_getting_started.md`** — general platform orientation, then the remaining RAG documents in any order, as needed for the workflow you're implementing.
6. **`Documentation_Guide.md`** — the full internal developer guide, including the runtime request flow and loading strategy.

## Implementation Roadmap (Brief)

The documentation described here is complete. Remaining implementation work:

1. **Intent Router** — classify incoming messages against the architecture's intent catalog.
2. **SQL Context Builder** — build authorized, pre-summarized per-user data for SQL-backed intents.
3. **RAG Retriever** — retrieve the relevant RAG document chunk(s) for intents that need process knowledge.
4. **Prompt Builder** — assemble System Documents (always) + SQL context + RAG chunks (as applicable) into the final prompt.
5. **Gemini Integration** — call the LLM provider with the assembled prompt, with Groq/OpenRouter as fallback providers.
6. **Response Formatter** — apply formatting rules, escalation routing, and disclaimers before returning the final response.
7. **Evaluation Suite** — build offline tests validating assistant responses against this documentation.

See `Documentation_Guide.md` for full detail on each stage.
