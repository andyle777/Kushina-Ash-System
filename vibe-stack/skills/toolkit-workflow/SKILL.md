---
name: |
  toolkit-workflow
description: |
  Load when a task spans multiple tools or connectors — GitHub, Gmail, web search, canvases, spreadsheets, or Personal Knowledge. Codifies Andy's preferred orchestration: default tool choices, sequencing, verification, and output destinations for his Mistral + GLM Vibe stack.
---

# Toolkit Workflow (Andy's Stack Orchestration)

Operational layer for Andy's workflow. Pairs with ORION (thinking) and Kushina persona (voice). This skill governs *which tool to use, in what order, with what verification*.

## Routing Table

| Task type | Default route | Rules |
|---|---|---|
| Code / repos | `github_app` | `get_me` first; `list_*` for broad retrieval, `search_*` for targeted queries; paginate 5–10; `minimal_output: true` unless detail needed |
| Email | `gmail` | `search_threads` → `get_thread` for full bodies; never guess addresses; draft in markdown, confirm with Andy, then `create_draft` |
| Fresh info / current events | `web_search` (+ `news_search` for news) | Resolve relative dates; open 2–3 sources when time-sensitive; cite every claim |
| Deep investigation | `deep-research` skill | Multi-source, evidence-based briefs |
| Analysis / math / data | `data-analysis` skill | For `.xlsx` work, always this skill |
| Standalone deliverable | Canvas (`canvas` skill; `canvas-react` for apps) | Canvas is the default for artifacts Andy will edit/iterate |
| One-off list / steps | Inline checklist (`rich-ui`) | Never a Canvas |
| Persistence request | `knowledge-mutations` skill | Ask only for clearly reusable context |
| Temporal grounding for companions | `omnichronos` skill (project frozen v2.1) | `--peek` never advances state; sliding 30-min session window; route via the skill — its spec canvas is canonical |

## Sequencing Rules

1. **Read Personal Knowledge first** if any topic plausibly matches the task — it may carry preferences, prior decisions, or project context.
2. **Load the matching skill before tool use**, not after.
3. **Parallelize independent calls**; sequence only when dependent.
4. **Verify before declaring done**: tool results, citations, and current file state are the source of truth — not memory of earlier steps.

## Output Discipline

- Deliverables → Canvas. Explanations → chat. Files the user downloads → `artifacts` skill.
- Never expose internal paths, shell commands, or tool mechanics in user-visible text.
- Cite web/connector sources with markdown links on first use of each claim.
- End multi-step work with: what was accomplished, what was verified, what remains uncertain.

## Durability Rules

- The upgraded native sandbox is ephemeral across turns; canvases, Personal Knowledge, and Skills are durable. Never leave a durable artifact only in the sandbox — run and verify there, then persist to a canvas or Knowledge.
- Before relying on any file from a previous turn, verify it still exists; current filesystem state is the source of truth, not memory of earlier steps.
- Releases get checksum manifests so integrity survives any rebuild. The `durability-guardian` skill owns the full protocol.

## Stack Awareness

Andy's stack: Mistral AI infrastructure (EU privacy, serving) + Z.ai GLM base model (reasoning) + Vibe agent framework (tools, skills, canvases, knowledge). When explaining behavior or limits, attribute to the correct layer.
