---
name: |
  united-english-lexicon
description: |
  Load for any work on Andy's United English Lexicon — version upgrades (v2.4+), dialect analysis, translation normalization, filler handling, receipts, or release freezes. Owns the lexicon's design laws (ratios-not-counts confidence, container/codec CLI contract) and routes between the durable v2.3 canvas, uploads, and Knowledge integration points.
---

# United English Lexicon

Andy's dialect/translation analysis system. Current release: v2.3 (frozen).

## Durable Sources (verify before use — durability-guardian)

- Canvas: `united-english-lexicon-v2-3` — byte-identical mirror of the
  uploaded `.py` (verified 2026-10-12 by diff; only the canvas frontmatter
  differs).
- Uploads: `united_english_lexicon_v2_3.py` / `.txt` (757 lines, 20,678
  bytes each).
- Knowledge: `cs-fundamentals` — five integration points (ratios-not-counts,
  container/codec receipts, translation-system framing, Bayesian dialect
  scoring, CLI contract stability).

## Design Laws (from Andy's own articles; now engine rules)

- **Ratios over counts** (engine rule 11): confidence is expressed as a
  ratio with its denominator, never a bare count.
- **Container/codec separation** (engine rule 12): the CLI contract is the
  frozen container; scoring algorithms and vocabularies are the codec that
  evolves behind it.
- **Bayesian evidence shape** (wave-3 mapping): dialect scoring is informal
  Bayes — report evidence shape, not just point scores.

## Upgrade Workflow (e.g., v2.4)

1. Read the current lexicon from the v2.3 canvas (source of truth); never
   work from memory of a previous version.
2. Change ONE mechanism at a time (DGM discipline, engine rule 5).
3. Keep the CLI container stable across versions (engine rule 12) —
   flag any proposed flag/schema change to Andy explicitly.
4. Execute and verify in the sandbox — native execution beats mental
   simulation; never claim it runs unless it ran.
5. Release to a new versioned canvas with a SHA-256 checksum manifest
   (engine rule 15); v2.3 stays archived and recoverable.
6. Update the Knowledge integration points if design principles changed.
7. Propose the upgrade summary for Andy's validation — he is the final
   decision-maker on his flagship.

## Boundaries

- Never rewrite the lexicon's philosophy or scoring semantics without
  Andy's explicit directive.
- Standing offer on record: v2.4 upgrade — scope it with Andy first.
