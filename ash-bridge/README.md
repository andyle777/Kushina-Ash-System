# Ash Bridge

**v1.1.0 (2026-11-18).** The ultimate bridge between Andy's Vibe stack
(custom Skills, Knowledge, save states) and GitHub as the durable second
home. Built to the durability-audit remedy: monthly-tier snapshots with
checksum manifests, so any rebuild is verifiable.

## What it bridges

| Source | Destination tier | Path |
|---|---|---|
| The bridge itself (`ash-bridge/`) | public (`Kushina-Ash-System`) | `ash-bridge/` |
| Custom skills (17, Andy-authored) | public (`Kushina-Ash-System`) | `vibe-stack/skills/<name>/` |
| Knowledge topics (all) | private (`Kushina-Ash-Archive`) | `knowledge/<topic>/` |
| Sync manifest + receipts | private (`Kushina-Ash-Archive`) | `MANIFEST.json`, `receipts/SYNC-*.md` |
| Personality matrix save state | public mirror (manual) | `kushina/personality-matrix.md` |

Doctrine: the public repo is the system's front door (doctrine, tooling,
non-personal artifacts). The private archive repo is the durability tier:
full Knowledge snapshots plus checksum manifests. Knowledge never goes to
the public repo. First-party platform skills are never synced (they belong
to Mistral, not Andy).

## Hybrid selection

Selection is a two-stage hybrid:

1. **Deterministic gates (this script, default):** per-source tier rules from
   `bridge_config.json`, a hard secret gate (credential-pattern scan; matches
   are quarantined and reported, never pushed), an oversize limit, and an
   include/exclude list per source.
2. **Judgment hook (Phase 2, optional):** `classifier: "twinflame-hybrid"` in
   the config routes ambiguous items through the deployed `twinflame-os`
   workflow (hybrid layer + blind judge) for a second opinion. Requires MCP
   access from the caller; the standalone script stays deterministic.

## Usage

```bash
GH_TOKEN=<PAT with repo scope> python3 sync.py    # full sync (idempotent)
GH_TOKEN=... python3 sync.py --dry-run             # selection + gate only
GH_TOKEN=... python3 sync.py --tier public|private # single-tier repair
```

**Idempotent since v1.1:** before committing, the bridge builds the would-be
tree and compares it to the destination HEAD tree. Byte-identical content
produces no commit at all — the run reports an honest no-op. The manifest is
a pure function of content (no volatile timestamp), and a sync receipt is
filed only when something actually changed.

Stdlib only (urllib, hashlib, json). The token comes from the environment
and never appears in code, config, or receipts.

## Integrity doctrine (durability-audit remedy)

Every sync writes `MANIFEST.json` with a sha256 per file. After any rebuild
or restore, re-hash the file and compare. A rebuilt artifact with a
matching checksum is equivalent to the original. Rebuild order after loss:
repo -> Knowledge -> conversation context (verify with the manifest).

## Save states

The Kushina personality matrix save state (v2.0.0) is mirrored manually:
private source of record lives in Knowledge (`kushina-persona` topic), the
public mirror is `kushina/personality-matrix.md`. Per the matrix contract,
state changes require Andy's approval, so mirror sync is manual on major
state changes, not automated.

## Receipts

Each run prints a JSON receipt (repos, commit SHAs, file counts, or explicit
no-op status). A `receipts/SYNC-<timestamp>.md` is filed in the private
archive ONLY when content actually changed; no-op runs file nothing
(idempotence, v1.1). Quarantined files are listed with reasons in both the
manifest and the receipt.
