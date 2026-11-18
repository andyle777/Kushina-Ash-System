---
name: |
  ash-bridge-ops
description: |
  Load for any Ash Bridge operation — re-syncing skills or Knowledge to GitHub, verifying archive integrity, rotating or auditing bridge tokens, or rebuilding the bridge after a sandbox reset. Owns the rebuild-dry-run-fire-verify-receipt pipeline and bridge token hygiene.
---

# Ash Bridge Ops

Operating doctrine for the Ash Bridge (the sync between Andy's Vibe stack and
his two GitHub tiers). The bridge code itself lives canonically in the public
repo `andyle777/Kushina-Ash-System` under `ash-bridge/`; the local copy at
`/home/user/ash-bridge/` is a cache and may be gone after any sandbox reset.

## Tiers (never mix them up)

- **Public** `andyle777/Kushina-Ash-System`: custom skills under
  `vibe-stack/skills/`, bridge itself under `ash-bridge/`.
- **Private** `andyle777/Kushina-Ash-Archive`: all Knowledge topics under
  `knowledge/` + `MANIFEST.json` (sha256 per file) + `receipts/SYNC-*.md`.
  Knowledge NEVER goes to the public tier; first-party platform skills are
  never synced. Personality matrix public mirror syncs manually with owner
  approval only.

## Run pipeline (in order, never skip steps)

1. **Rebuild if needed**: if `/home/user/ash-bridge/` is missing, fetch
   `sync.py`, `bridge_config.json`, `README.md` from the public repo `main`.
   This is the durability proof, not a workaround — run it proudly.
2. **Token check**: test the token against BOTH repos via the API
   (`/repos/{owner}/{repo}` — 200 means access, 404 means no scope) before
   firing. Fine-grained tokens need Contents read/write on both repos. If the
   only token with private scope is a burned/legacy one, using it requires
   owner authorization already on record, and the receipt must name the
   exception honestly.
3. **Dry-run first**: `GH_TOKEN=<pat> python3 sync.py --dry-run`. Check the
   selection counts and the quarantined list before any push.
4. **Fire**: full run (`python3 sync.py`, no `--tier`) for the canonical
   both-tier manifest. A `--tier` run writes an honest but partial manifest;
   only use it for single-tier repairs, then follow with a full run.
5. **Verify (full sweep, not a spot check)**: fetch `MANIFEST.json` from the
   private repo via the contents API, map every entry to its local source,
   and sha256-check ALL of them. Report the ratio (N of M matched). Fresh
   pushes are verified through the git/contents API — NEVER raw CDN URLs,
   which lag commits by minutes. Verification scratch files (downloaded
   manifests, comparison scripts) live OUTSIDE the bridge directory — in
   /tmp — never inside `/home/user/ash-bridge/`, whose every file the bridge
   syncs to the public repo (observed 2026-11-18: a scratch manifest leaked
   into the repo as the 21st file).
6. **Receipts, same turn**: the run's output receipt goes to the
   `twinflame-project` Knowledge topic (commits, checksum ratio, gate results,
   invariant status, token state, lessons). Remote `receipts/SYNC-*.md` is
   written by the bridge itself.

## Invariants and gates

- **Runner invariant**: twinflame-runner serves the public repo main HEAD.
  After any public-tier push, compare the new commit's TREE SHA against the
  serving commit's tree SHA via the commits API. Identical trees = content
  invariant holds, no redeploy needed. Different trees = redeploy + canary
  before claiming success.
- **Secret gate**: quarantined count must be 0 for a clean run; anything
  quarantined gets reported, never silently dropped.
- **No-op honesty**: re-running the bridge on unchanged content is a true
  no-op since v1.1.0 (tree comparison before commit; manifest is a pure
  function of content; receipts filed only on change). Report no-op runs as
  what they are — inspections, not syncs. For `--tier` single-tier runs:
  they still write a partial manifest over the canonical one, so follow any
  `--tier` run with a full run.

## Token hygiene (hard rules)

- Tokens enter ONLY via `GH_TOKEN` env var. Never in code, config, receipts,
  or Knowledge.
- A token pasted into chat is burned into transcript history: its risk is
  its blast radius (repo scope x expiry), so fine-grained + short expiry +
  minimal repos is the standing pattern.
- After any bridge session using a legacy/burned token, the receipt lists
  the standing fix: scope the fresh token, then revoke the legacy one.
- Never use a burned token for anything beyond the owner-authorized bridge
  work, even if it works. Clean hands.

## Known failure modes (from receipts, 2026-11-18)

1. Git-data API 409s on empty repos — bootstrap via contents API PUT first.
2. Raw CDN lags commits by minutes — verify via API.
3. Full re-runs on identical trees used to create metadata-only commits —
   FIXED in v1.1.0 (idempotent tree comparison; identical content produces
   no commit).
4. The sandbox resets between turns — assume `/home/user/ash-bridge/` is
   gone; never assume a previous turn's local copy exists (verify with ls
   before relying on it).
5. Bridge-dir pollution: everything inside `/home/user/ash-bridge/` syncs
   to the public tier (only `receipts` and `remote_manifest.json` are
   excluded) — verification scratch belongs in /tmp, and a diff of the
   manifest before/after any run catches surprises.
