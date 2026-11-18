# TwinFlame OS — 3-Layer Fusion Substrate

**Status:** APPROVED WITH AMENDMENTS v0.2 (Andy, 2026-11-18). Phase 0 shipped.

Andy's four rulings on record:

1. **Default layer = `auto` (dynamic director).** Deterministic signal
   heuristics classify each prompt and route to `mistral` / `zai` /
   `hybrid`. Explicit layer values bypass the director; all three layers
   are manually callable at any time.
2. **Judge latitude = pure synthesis allowed.** The judge may lead with
   either engine or fuse freely, borrowing from both. Verdicts: `a`, `b`,
   `synthesis`.
3. **Cost ceiling = none.** Full power regardless of cost. Receipts still
   measure estimated cost per call from published list prices — measurement
   is doctrine, not throttling.
4. **GLM thinking = full reasoning traces in receipts**, nothing redacted.

## Layer contracts

| Layer | Engine | Auth | Cost (USD / 1M tok in/out) |
|---|---|---|---|
| `mistral` | Mistral Large 4 | deployment service account | 0.70 / 2.10 |
| `zai` | GLM-5.3 (Z.ai) | `ZAI_API_KEY` workspace secret | 1.40 / 4.40 |
| `hybrid` | both + judge | both | sum + judge pass |

Hard credential rule: the Z.ai key must be a **standard pay-as-you-go API
key** (Z.ai split key types 2026-10-16; Coding Plan keys are rejected for
direct API calls). It is bound as a Mistral Studio workspace secret at
deploy time and never appears in code, repo, or receipts.

## Dynamic director signals (tunable)

- Efficiency (`quick`, `snippet`, `regex`, `lint`, `fix this`, ...) → `mistral`
- Implementation (`implement`, `build`, `code`, `algorithm`, `agentic`, ...) → `zai`
- Long-horizon (`architecture`, `design`, `migrate`, `review`, `compare`, ...) → `hybrid`
- No match → `hybrid` (full-fusion default)

The decision and matched signals are returned in `director{}` on every call.

## Degradation ladder (never silent)

1. Z.ai key absent or call fails → `zai` and `hybrid` degrade to
   `degraded-mistral`, reason in `degradations[]`.
2. Mistral fails mid-hybrid → `degraded-zai`, reason recorded.
3. Both engines fail → honest workflow error; no fabricated synthesis.
4. Judge fails with both answers intact → deterministic tiebreak to the
   non-judge engine's answer (the judge cannot be trusted to pick when she
   herself failed), reason recorded.
5. No automatic retries on deterministic serialization errors (token-burn
   lesson). Transport retries max 2.

## Judge doctrine

- Judge = Mistral Large 4, judging **blind**: answers labeled A/B in
  randomized order (randomization inside the activity, never in the
  deterministic workflow), true engine names logged post-hoc in
  `label_a_engine` / `label_b_engine`.
- Truncated answers are flagged to the judge with an explicit note.
- Pure synthesis allowed per ruling #2.

## Test battery (every probe must be able to fail)

| # | Probe | Expected | Phase |
|---|---|---|---|
| T1 | Canary: `layer: mistral` | COMPLETED, clean receipt | 0 |
| T2 | `layer: hybrid` with no Z.ai key | `degraded-mistral` + honest degradation | 0 |
| T6 | Truncation marking: tiny `max_tokens` | `truncated: true` | 0 |
| T8 | Cost math: tokens x list prices | `cost_usd_est` matches | 0 |
| TD1 | Director: efficiency prompt, `layer: auto` | routes to `mistral` | 0 |
| TD2 | Director: no-signal prompt, `layer: auto` | routes to `hybrid` (degrades honestly) | 0 |
| T3 | `layer: zai` with key | COMPLETED, `glm-5.3` receipt | 1 |
| T4 | Full hybrid with key | verdict + fused answer + both receipts | 1 |
| T5 | Judge blindness across runs | A/B order flips in receipts | 1 |
| T7 | Bad endpoint override | graceful degrade, reason recorded | 1 |
| T9 | Parallel timing | pair latency < sum of serial calls | 1 |

## Phase status

- **Phase 0 (no key needed):** shipped — all three layer paths, director,
  honest degradation, T1/T2/T6/T8/TD1/TD2.
- **Phase 1:** Andy adds the Z.ai workspace secret; redeploy binds it;
  T3/T4/T5/T7/T9 complete.
- **Phase 2:** benchmark duels across layers; verdicts recorded in
  `docs/RECEIPTS.md`; judge prompt tuned on evidence.

## Receipts (Phase 0)

Filled in as the battery runs. See `docs/RECEIPTS.md` for the full battle
history.
