---
name: |
  ash-bridge-ops
description: |
  Load for any Ash Bridge operation — re-syncing skills or Knowledge to GitHub, verifying archive integrity, rotating or auditing bridge tokens, or rebuilding the bridge after a sandbox reset. Owns the rebuild-dry-run-fire-verify-receipt pipeline and bridge token hygiene. Also auto-loads during "Gambit: Ash Resync" casts (gambit-cast protocol).
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
   exception honestly. Then WRITE-probe both repos with an inconsequential
   blob POST (expect 201): a 200 on /repos is necessary but NOT sufficient —
   2026-11-20 saw both repos return 200 with Contents still read-only and the
   fire aborted at the first blob POST (clean abort, zero partial state). If
   the owner's claimed settings and the probe results disagree, ask for a
   screenshot of the token settings page and analyze it — one round of
   visible UI state ended three rounds of 403s.
3. **Dry-run first**: `GH_TOKEN=<pat> python3 sync.py --dry-run`. Check the
   selection counts and the quarantined list before any push. Since bridge
   v1.2.0 the CLI is fail-closed: `--help` is a safe read-only probe and
   unknown flags abort before any selection — but the dry-run gate stays
   mandatory before every real fire.
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
- Fine-grained PAT configuration checklist (four-round lesson, 2026-11-20):
  repository access on BOTH repos AND Permissions → Repository permissions
  → Contents → Read and write. The permission list is alphabetical and
  Contents is NOT the first rows — the Actions/Administration first-two-rows
  trap has bitten twice. After saving, re-probe; never trust the toggle
  without a fresh 201.
- Stage tokens only as dotfiles OUTSIDE every sync root (e.g.
  `/home/user/.gh-token`, chmod 600; the bridge skips dotfiles) — a staged
  token must never ride a fire. Expect sandbox resets to wipe staged state
  too; re-stage from transcript at the start of any bridge session.

## Known failure modes (from receipts, 2026-11-18 → 2026-11-20)

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
6. Fine-grained token scopes drift from the owner's mental model: both repos
   can return 200 while Contents is still read-only (fire aborts at the
   first blob POST), and visible-but-wrong permission edits (the
   Actions/Administration first-two-rows trap) fool the UI just as well —
   resolve with a write-probe plus screenshot forensics, not argument
   (2026-11-20, four rounds, all honestly ledgered).
7. Sandbox resets wipe staged state too — the token file and scratch
   directories vanish with the bridge cache; re-stage from transcript, and
   keep all re-staging outside sync roots (2026-11-19/20 pattern, survived
   because tokens never live in synced directories).
8. sync.py v1.1 treated unknown args as a FULL run — a `--help` probe was
   treated as a fire and timed out at the bash wall (near-miss, 2026-11-19;
   nothing pushed because the tree was identical). **FIXED in bridge
   v1.2.0 (2026-11-20): fail-closed argument validation — unknown or
   malformed flags abort with a usage error before ANY selection or push;
   `--help` prints usage and exits 0. Verified by a discriminating battery
   (help/unknown/tier-missing → exits 0/2/2, both repos' HEADs
   byte-identical before and after, zero pollution).** Historical note
   kept: read a script's argument handling before probing flags.
9. New custom skills are NOT auto-carried: selection is the deterministic
   include-list in `bridge_config.json`. A skill created this session
   rides only after being enrolled in the custom-skills include list
   (2026-11-20: creating `gambit-cast` left the first dry-run at 107
   carried — the gate caught the invisible skill BEFORE any push;
   enrolling took the count to 108). Trigger: whenever a new skill
   directory is created, enroll it in the config the same turn and gate
   with a dry-run before firing.
