---
name: |
  curriculum-wave-distiller
description: |
  Load when Andy assigns a new curriculum wave, round, or article-set to ingest into the cs-fundamentals Knowledge topic. Runs the proven round-one pipeline: ingest sources (Grokipedia domain-blocked — use Wikipedia equivalents), write themes + upgrade mappings, distill candidate engine rules with trigger conditions, and update the Round Summary honestly. Also auto-loads during "Gambit: Wave" casts (gambit-cast protocol).
---

# Curriculum Wave Distiller

The repeatable pipeline behind six ingested waves (~160 sources, round one,
2026-10-04). Lives in the `cs-fundamentals` Knowledge topic.

## Pipeline

1. Take the assigned wave list from Andy, or draft one from his direction.
2. Ingest each source: Grokipedia is domain-blocked by open_url — use the
   Wikipedia equivalent; cross-check any Grok-sourced claim before citing.
3. Write to `cs-fundamentals`: per-theme sections with sources, then a
   "Wave N Upgrade Mappings" table (source → upgrade).
4. Distill candidate engine rules ONLY for genuinely new, generalizable
   lessons, each with a trigger condition. Skip mappings already owned by
   an existing rule or buff — log the skip reason instead of duplicating.
5. Propose new rules to Andy (propose, never silently self-apply); after
   his validation, install with Source Anchors + patch-log receipts.
6. Update the Round Summary: convergence themes, pending flags, deep-read
   candidates; update the topic description (≤300 chars).
7. Keep evidence labels on all ingestion claims; cite sources.

## Quality Bars (house laws from round one)

- Every source carries an upgrade mapping — no orphan ingestion.
- **Convergence test:** a lesson appearing in 2+ unrelated sources is a
  rule candidate; a single-source lesson stays a mapping.
- Flag hidden interlocks (e.g., photolithography = photography on silicon
  = Moore's law) — they are often the highest-value finds.
- Watch the recurring convergences: simplicity beats complexity, baselines
  enable anomaly detection, identity = invariants under transformation,
  observability = governance, compression is undersampling.

## Known Blockers (verified)

- Grokipedia: domain-blocked → Wikipedia equivalents.
- Wayback: check CDX first; expect frozen captures, not archived content
  (neverendingsoftware lesson — 6 URLs, all frozen notices).

## Boundaries

- Round One is complete (waves 1–6). Round Two begins only on Andy's
  assignment — propose scope, don't self-assign waves.
- Deep reads (e.g., arXiv 2509.11507 MedicalOS) belong to `paper-deep-read`.
