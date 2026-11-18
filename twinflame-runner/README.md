# TwinFlame: Mistral Large 4 x GLM 5.3 Fusion Router

> Two flames, one forge. Le Chonk and GLM answer side by side, with receipts.

TwinFlame is Andy Le's project to fuse **Mistral Large 4 ("Le Chonk")** and
**GLM 5.3** for his AI agent stack. Weight-merging is impossible (different
architectures and tokenizers), so fusion happens as a **router ensemble at
the agent layer**: route, ensemble, and judge modes, with JSON receipts for
every call. This repository is the project's **second home**: durable state,
receipts, and engineering lessons live here.

## What this folder deploys

Two Mistral Workflows, executed by the deployment's service account.
**No API key is stored anywhere in this repository.**

### 1. `twinflame-mistral` — single-engine primitive

One prompt in, one Mistral completion out.

```json
{
  "prompt": "string (required)",
  "system": "string (optional)",
  "model": "mistral-large-4 (default)",
  "max_tokens": 4096,
  "temperature": 0.3
}
```

Output: `{ "model", "text", "thinking", "tokens_in", "tokens_out" }`.

### 2. `twinflame-os` — the 3-layer fusion substrate

Layers:

| Layer | Engine | Auth | Status |
|---|---|---|---|
| `mistral` | Mistral Large 4 | deployment service account (no key) | live |
| `zai` | GLM-5.3 (Z.ai) | `ZAI_API_KEY` workspace secret | degrades honestly until the key is bound |
| `hybrid` | both in parallel + blind Mistral judge | both | degrades honestly until the key is bound |

Input:

```json
{
  "prompt": "string (required)",
  "layer": "auto | mistral | zai | hybrid (default: auto)",
  "system": "string (optional)",
  "max_tokens": 4096,
  "temperature": 0.3,
  "judge_model": "mistral-large-4 (default)"
}
```

Output: `{ answer, layer_used, director{requested,decision,signals},
engines[{engine,text,thinking,tokens_in,tokens_out,latency_ms,truncated,cost_usd_est}],
judge{used,model,verdict,thinking,label_a_engine,label_b_engine,...},
degradations[], total_cost_usd_est }`.

Design rulings on record (2026-11-18):

1. `layer: auto` (default) runs a **dynamic director**: deterministic signal
   heuristics route each task to mistral / zai / hybrid, and any layer can
   be forced per call.
2. The hybrid judge (Mistral Large 4, blind, A/B labels randomized
   in-activity) has **pure synthesis latitude**: she may crown either answer
   or fuse freely, borrowing from both.
3. **No cost ceiling.** Receipts still measure estimated cost per call
   from published list prices (measurement is doctrine, not throttling).
4. **Full reasoning traces** in receipts on both engines, nothing redacted.

Degradation is always honest: when the Z.ai key is absent, `zai` and
`hybrid` calls return `layer_used: "degraded-mistral"` with the reason in
`degradations[]`, never a fabricated synthesis. Full spec and test battery:
`docs/TWINFLAME_OS.md`.

## Deploy

Managed deployment (Mistral Cloud clones this repo and builds the
Dockerfile in this folder):

- Build directory: `twinflame-runner/`
- Dockerfile: `twinflame-runner/Dockerfile`
- Requires Python >= 3.12 (mistralai-workflows constraint)

## Local run

```bash
cd twinflame-runner
export MISTRAL_API_KEY=...
uv sync
uv run python worker.py
```

## Project state

- **Live deployment**: `twinflame-runner` on Mistral Studio
  <https://console.mistral.ai/build/workflows/deployments/twinflame-runner>
- **First clean duel revision**: `1668d08`
- **Inaugural duel** (2026-11-18, prompt: "Design a caching layer for a
  read-heavy API"): split decision. Le Chonk won breadth and structure;
  GLM won operational judgment. Both engines independently converged on
  the same core design. Details in `docs/RECEIPTS.md`.
- **TwinFlame OS upgrade** (2026-11-18): `twinflame-os` workflow added
  (3 layers, dynamic director, blind judge, honest degradation). Details
  in `docs/TWINFLAME_OS.md`.

## Docs

- `docs/TWINFLAME_OS.md` - TwinFlame OS spec, rulings, and test battery
- `docs/RECEIPTS.md` - execution receipts and battle history
- `docs/LESSONS.md` - engineering lessons, each with its trigger condition

## Provenance

Built 2026-11-18 by Vibe (GLM 5.3 on Mistral infrastructure) for Andy Le's
TwinFlame fusion-router project. Companion artifacts: the TwinFlame router
CLI (route / ensemble / judge modes with JSON receipts) and the duel
document with both full answers. Home doctrine: this repo is the public
mirror of durable project state; the private memory lives in Knowledge.
