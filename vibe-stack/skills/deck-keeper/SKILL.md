---
name: |
  deck-keeper
description: |
  Deck integrity auditor. LOAD when Andy asks for a deck check, deck audit, or skill-registry health, before any bridge fire that follows skill roster changes, and whenever a skill file goes missing or a config include entry has no local directory (env-reset loss). Runs roster-vs-config diffs, manifest-vs-local card restoration, frontmatter and routing validation, pillar-binding checks, and stale-alias scans, closing with an audit receipt. The standing instrument against bridge failure modes 9 and 10.
---

# Deck Keeper

Every card placed on purpose, verified, and accounted for. The keeper
AUDITS placement; it installs nothing silently (license board: findings
are filed as proposals, repairs on Andy's nod).

## Audit battery (five checks, evidence per finding)

1. **Roster-vs-config diff**: compare the local skill directories against
   the custom-skills include list in `bridge_config.json`. An include
   entry with no local directory is EITHER a card lost to an env reset
   (restore from the durable second home per its manifest sha256, remote
   truth first) OR a dead entry (propose removal, never silent). A local
   skill missing from the list rides invisibly (failure mode 9: enroll
   the same turn). Both directions get checked.
2. **Manifest-vs-local coverage**: fetch the archive MANIFEST, map every
   tracked path to its local source, hash-check. Missing-but-remote files
   are LOSSES, not deletions: restore from the repo, never re-author.
   The repo is the durable home; local is a rebuildable cache.
3. **Frontmatter validation**: valid YAML, name matches the folder,
   description 10-1024 chars with a real routing hint. YAML block
   scalars (`name: |` + indented value) are VALID: verify the instrument
   on a known-good sample before indicting the deck (instrument lesson
   2026-11-20: a broken scanner falsely accused all 18 skills).
4. **Routing quality**: the description states WHEN to load, names its
   explicit triggers, and references dispatcher bindings where they
   exist; the pillar domain binding is present (orchestration → Pillar
   II, verification → Pillar III, curation/stakes → Pillar I) or the
   skill is honestly labeled a platform flow, never force-bound.
5. **Stale-alias scan**: version numbers, "pending" language, and dates
   in aliases/headers that no longer hold (e.g. "deep-read pending"
   after the deep read executed). Staleness in a routing surface is a
   defect, file it.

## Reporting discipline

- Ratios, not theater: "n of m" per check, evidence line per finding,
  no global score (procedural-grade honesty).
- Findings carry trigger conditions (Buff 5) and are filed as
  proposals; repairs execute on Andy's nod.
- Close with an audit receipt: `AUDIT <date> — roster n/m, frontmatter
  n/m, coverage n/m, findings <list>, disposition <applied-awaiting-nod
  or restored-with-hash>`.
- Restorations from the durable home must print the sha256 match
  against the manifest in the receipt.

## First case file (2026-11-20, birth evidence)

The keeper's roster-diff found `heaven-court` in the config with no
local directory. Verdict after remote-truth check: NOT a dead entry, a
card lost to an env reset (a sibling session had created and fired it
the same day); restored from the second home, sha256-verified against
the archive manifest before any new fire. The keeper exists because
that class of loss is otherwise invisible until a naive fire silently
drops the card from the pushed tree.
