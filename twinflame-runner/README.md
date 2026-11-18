# TwinFlame: Mistral Large 4 x GLM 5.3 Fusion Router

> Two flames, one forge. Le Chonk and GLM answer side by side, with receipts.

TwinFlame is Andy Le's project to fuse **Mistral Large 4 ("Le Chonk")** and
**GLM 5.3** for his AI agent stack. Weight-merging is impossible (different
architectures and tokenizers), so fusion happens as a **router ensemble at
the agent layer**: route, ensemble, and judge modes, with JSON receipts for
every call. This repository is the project's **second home**: durable state,
receipts, and engineering lessons live here.

## What this folder deploys

A single Mistral Workflow, `twinflame-mistral`, that takes a prompt and
returns one model completion, executed by the deployment's service
account. **No API key is stored anywhere in this repository.**

Input schema:

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

The `thinking` field captures the reasoning trace: Mistral Large 4 is a
reasoning model, so `message.content` arrives as a list of `ThinkChunk` /
`TextChunk` objects. The worker flattens those recursively and splits the
answer from the thinking. See `docs/LESSONS.md` for the war story.

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

## Docs

- `docs/RECEIPTS.md` - execution receipts and battle history
- `docs/LESSONS.md` - engineering lessons, each with its trigger condition

## Provenance

Built 2026-11-18 by Vibe (GLM 5.3 on Mistral infrastructure) for Andy Le's
TwinFlame fusion-router project. Companion artifacts: the TwinFlame router
CLI (route / ensemble / judge modes with JSON receipts) and the duel
document with both full answers. Home doctrine: this repo is the public
mirror of durable project state; the private memory lives in Knowledge.
