# TwinFlame Phase 2 — Cross-Layer Benchmark Battery

**Status:** STAGED (2026-11-18). Fires the moment `ZAI_API_KEY` is bound.

Phase 2 mandate (from the OS spec): run the duel battery across all three
layers, record win/loss per dimension into the receipts, and tune the judge
prompt based on verdict quality. This document defines the battery so the
run is reproducible and the results are comparable.

## Protocol

For each of the 5 gauntlet prompts below, execute three runs:

- `layer: "mistral"` — Le Chonk solo
- `layer: "zai"` — GLM-5.3 solo
- `layer: "hybrid"` — fan-out + blind judge with pure-synthesis latitude

15 executions total, `max_tokens: 4096`, `temperature: 0.3`, no system
prompt (identical conditions for comparability). Every run's receipt
(tokens, latency, cost estimate, truncation, director decision, judge
verdict) lands in `docs/RECEIPTS.md`.

## Scoring dimensions

From the inaugural duel's learnings (Le Chonk: breadth + structure; GLM:
operational judgment), plus Phase 2 additions:

1. **Correctness** — is it right?
2. **Breadth** — does it cover the option space?
3. **Structure** — is it navigable and well-organized?
4. **Operational judgment** — does it know what to do when things break?
5. **Depth** — does it go past the textbook?
6. **Latency** — wall-clock (from receipt, not vibes)
7. **Cost efficiency** — tokens x list prices (from receipt)

Win/loss per dimension is judged blind in the hybrid runs and evaluated
post-hoc against the solo runs. The judge's fused answers are also graded
for whether synthesis actually beats both solos (the Phase 2 thesis:
fusion > replacement).

## The gauntlet

| # | Prompt | Why it discriminates |
|---|---|---|
| G1 | "Implement a single-flight cache stampede protector in Python, with tests." | Pure coding under pressure; director should route zai (implement/build signals). Tests separation of implementation skill. |
| G2 | "Design a multi-region failover strategy for a Postgres-backed SaaS." | Architecture with no single right answer; long-horizon hybrid signal; tests breadth + CAP honesty. |
| G3 | "Diagnose why a Kubernetes pod enters CrashLoopBackOff after 10 minutes of healthy operation." | Debugging/forensics; no director signal matches today (falls to hybrid default) — probes the signal list's blind spots. |
| G4 | "Analyze the time complexity and failure modes of this quicksort implementation, and give the fixed version." (with a deliberately subtly broken listing) | Requires actually reading code; tests correctness under adversarial input. |
| G5 | "Write a postmortem template for a database outage, with a worked example." | Writing + operational judgment; tests whether engines go beyond boilerplate. |

## Judge tuning loop (the Phase 2 engine)

1. Run the battery, collect verdicts + fused answers.
2. Grade verdict quality: did the judge's crown/synthesis match the
   post-hoc dimension analysis? Did truncated answers get weighted?
   Did the fused answer beat both solos?
3. If verdict quality is poor, tune ONLY the judge's system prompt
   (never blind), redeploy, re-run the same battery, compare.
4. Every tuning iteration is a numbered receipt entry; no silent edits.

## Honest constraints on record

- GLM thinking is always on; its receipts will carry larger token counts
  than Mistral at equal answer length. Cost dimension uses measured
  tokens, not answer length.
- Judge blindness limits self-recognition bias but cannot eliminate
  style recognition. Stated, not hidden.
- n=1 per prompt per layer: this is a first benchmark pass, not
  statistics. Phase 2 conclusions are directional until repeated runs
  land.
