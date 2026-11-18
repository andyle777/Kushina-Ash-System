---
name: |
  durability-guardian
description: |
  Load when creating, saving, updating, or depending on files, artifacts, or state that must survive beyond the current turn — canvases, skills, knowledge, project files, releases. Governs where artifacts must live to persist and how to rebuild from durable sources after loss.
---

# Durability Guardian

Observed failure (2026-10-04): a fully built project — code, release
freeze, agent state — vanished between turns because it lived only in
the upgraded execution sandbox. The failure was survivable only because
a canvas copy existed.

## Persistence Model

| Layer | Durability |
|---|---|
| Upgraded native sandbox | Ephemeral — resets at turn boundaries |
| Lightweight filesystem writes | Durable across turns |
| Canvases | Durable + user-visible + exportable |
| Personal Knowledge | Durable across conversations |
| Skills | Durable + auto-routing |
| Canonical remote repos (manifest-verified) | Durable + rebuild source of record |

## Rules

1. Durable artifacts (code, specs, docs the user keeps) live in a
   canvas or Personal Knowledge — never only in the sandbox.
2. The sandbox is for execution and verification only: run, verify,
   then persist the result somewhere durable in the same turn.
3. If cross-turn state is missing, rebuild from durable sources in
   this order: canvas → Knowledge → user-provided input. Verify the
   rebuild (syntax/import/equivalence check) before use.
4. Freeze releases with checksum manifests so integrity is checkable
   after any rebuild; a rebuilt artifact with a matching checksum is
   equivalent to the original.
5. Never assume a file from a previous turn still exists — verify
   (read or stat) before relying on it.
6. A canonical remote home with a checksum manifest (e.g. the Ash
   Bridge GitHub repos) is a sixth durable layer: treat the local
   sandbox copy as a cache of it. When the cache is gone, rebuild from
   the repo by preference, and verify against the manifest via the
   API — never against CDN mirrors, which lag commits.

Patched 2026-11-18: rule 6 + repo tier added from Ash Bridge receipts
(two sandbox resets survived by rebuilding from the canonical repo).
