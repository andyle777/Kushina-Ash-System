# OmniSoul Mystic X 4.5.1 — Stress-Test Review

Reviewed 2026-11-18 by Vibe (GLM 5.3 on Mistral infrastructure) under the
Experiment Smith discipline: a test that cannot fail is not a test.

## Method

The original 4.5 build was run live and probed with a discriminating
12-case battery: canary math, documented examples, undefined/zero inputs,
out-of-range jumps, unbounded loops, persistence across restart, hostile
(corrupt) state files, and dead-code inspection. Every fix was retested
against the same probes.

## Findings on 4.5 (original)

| # | Verdict | Finding | Severity |
|---|---|---|---|
| 1 | BUG (verified by execution) | `cards <program>` args form is broken: even the help text's own first example fails with "Invalid op on card 1: A". Only `--prog` works. | Blocker (UX) |
| 2 | BUG (verified by execution) | JZ with out-of-range target while mill == 0 reports "JZ not taken" — a lie. The engine wanted to jump, could not, and hid the error. | High (honesty) |
| 3 | DESIGN FLAW (verified by execution) | Startup demo unconditionally reloads cards, clobbering persisted pc/program. The advertised "persistent engine state" never survives a restart for programs. | High (feature-breaking) |
| 4 | FLAW (verified by execution) | Backup filename has 1-second resolution: all steps within a second silently overwrite one backup. Per-step backup history does not exist. (The reviewer initially predicted spam; the truth was collision. Falsified hypothesis, recorded.) | Medium |
| 5 | RIGOR GAP (verified by inspection) | Undefined variables silently read as 0.0 — masks typos; fabricated data looks like computed data. | Medium |
| 6 | DEAD CODE (verified by inspection) | `hashlib`, `zlib`, `Optional`, and `VAULT` are imported/defined but never used. | Low |
| 7 | PASS | DIV by zero: clean error, engine continues, no crash. | — |
| 8 | PASS | `JMP 0` infinite loop: bounded by max_steps, no hang. | — |
| 9 | PASS | Corrupt state file: graceful recovery, error logged, no crash. | — |
| 10 | PASS | Canary: 8 * 2 = 16, store/PRINT/HALT all correct. | — |

## Fixes in 4.5.1 (all retested)

1. `cards` args are joined and split on `|` — the help example now runs.
2. JZ out-of-range now returns `ERROR: JZ out of range` (honest failure).
3. Demo loads only when no restorable state exists; persisted programs
   resume (verified: pc=3 resumed to completion).
4. Backups: unique per step_count, throttled to load/reset and every 50
   steps.
5. Undefined variable reads log `warn: <OP> read undefined var '<V>' as
   0.0` into the error log (visible in status).
6. Dead imports and VAULT removed.

## Test-design lesson (with trigger)

When a stateful engine persists its accumulator between probes, then a
probe that assumes a fresh accumulator is a broken test, not a passing
system. The JZ re-probe initially "failed" because mill carried 25.0 from a
prior probe; the fix was reseeding state, not the code. Label test-design
failures separately from system failures before touching the artifact.
