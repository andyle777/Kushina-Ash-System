# TwinFlame Mistral Runner

The Mistral half of **TwinFlame**, the Mistral Large 4 (Le Chonk) x GLM-5.3
fusion router. This project deploys to Mistral AI Studio as a managed
workflow deployment.

## What it does

A single Mistral Workflow, `twinflame-mistral`, that takes a prompt and
returns one model completion, executed by the deployment's service
account — no API key is stored anywhere in this repository.

Input schema:

```json
{
  "prompt": "string (required)",
  "system": "string (optional)",
  "model": "mistral-large-4 (default)",
  "max_tokens": 2048,
  "temperature": 0.3
}
```

Output: `{ "model", "text", "tokens_in", "tokens_out" }`.

## Deploy

Managed deployment (Mistral Cloud clones this folder and builds the
Dockerfile at the project root):

- Build directory: `twinflame-runner/`
- Dockerfile: `twinflame-runner/Dockerfile`

## Local run

```bash
cd twinflame-runner
export MISTRAL_API_KEY=...
uv sync
uv run python worker.py
```

## Provenance

Built 2026-11-18 by Vibe (GLM 5.3 on Mistral infrastructure) for Andy Le's
TwinFlame fusion-router project. Companion artifact: the TwinFlame router
CLI (route / ensemble / judge modes with JSON receipts).
