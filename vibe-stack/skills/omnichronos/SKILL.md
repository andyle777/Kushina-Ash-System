---
name: |
  omnichronos
description: |
  Load for any work on Andy's OmniChronos temporal-grounding system — algorithm changes, spec work, demos, or version upgrades. Enforces the frozen v2.1 contracts (UTC storage truth, --peek never advances state, sliding 30-minute session window) and routes between the atomic-clock code canvas and the v2.1 algorithms spec canvas.
---

# OmniChronos

Andy's temporal-grounding companion system. v2.1 is the frozen release.

## Durable Sources (verify before use)

- Canvas: `omnichronos-atomic-clock` — frozen v2.1 implementation
  (1,399 lines; VERSION = "2.1").
- Canvas: `omnichronos-v2-1-algorithms` — canonical design spec
  (199 lines; the implementation is verified against it).
- Routing: toolkit-workflow "temporal grounding for companions" row.

## Frozen v2.1 Contracts (change only with Andy's explicit validation)

- **Temporal Authority:** UTC is storage truth; local time
  (default Australia/Sydney) is presentation truth. The AI never infers
  the time itself — OmniChronos supplies it.
- **`--peek` never advances state** — observation is strictly read-only.
- **Sliding 30-minute session window** (`DEFAULT_SESSION_WINDOW_MINUTES
  = 30`); future clock-skew tolerance 300 seconds.
- **PrimeReality_X777** is the default timeline.

## Workflow

1. Read the algorithms spec canvas before any change — it is canonical;
   the implementation must stay verified against it.
2. Contract-level changes (window semantics, peek behavior, temporal
   authority) require Andy's explicit validation first (engine rule 5).
3. Non-contract changes still keep the CLI container stable (engine
   rule 12); algorithms evolve behind it.
4. Verify by execution in the sandbox, then persist to canvas; emit a
   SHA-256 checksum receipt (engine rule 15).
5. Update the spec's Verification Appendix whenever the implementation
   changes — spec and code must never drift apart silently.

## Boundaries

- v2.1 stays archived and recoverable; any v2.2 work is a new freeze,
  not an in-place mutation.
- Sessions longer than the window gap into separate sessions — do not
  paper over session boundaries in analysis without saying so.
