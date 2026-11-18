---
name: |
  ether-emulation
description: |
  Load for any work on Andy's Vibe-stack emulation of Ether Memories: mind-graph entity/edge queries and mutations, bounded memory-context assembly, dream-cycle proposals (never auto-applied), or store health checks. Owns the ether.emulation.store.v1 contracts and the receipts discipline. The real ether-memories runs on Andy's machine; this is its procedural-grade mirror.
---

# Ether Emulation

Vibe-stack emulation of Andy's Ether Memories (the real TypeScript system
lives on his machine). Procedural-grade: fixed procedures executed by an
LLM — disciplined, not enforced. Design law: **dreams propose, memory
remains authoritative** — nothing applies without Andy's explicit acceptance.

## Durable Store (verify before use — durability-guardian)

Topic `ether-memory-store`, container `ether.emulation.store.v1`:

- `mind-graph.md` — entities + edges. `P###` persons, `E###` everything
  else; IDs never reused.
- `diary.md` — chronological narrative, one entry per conversation.
- `receipts.md` — mutation ledger, md5 checksums (DIGEST_ALGORITHM: md5).

Relation vocabulary (frozen v1, exactly 8): `created_by`, `member_of`,
`works_on`, `powers`, `derives_from`, `references`, `relates_to`,
`assisted_by`. Extending it is a container change requiring Andy's approval.

## Procedures

### Graph operations
Read the store files first (never trust memory of prior state). Additions:
new entities get the next free ID; every edge must use a frozen relation
and reference existing IDs — unknown ID → refuse, fail closed. After any
mutation: append a dated receipt with fresh checksums in the same turn.

### Context assembly
Inputs: `purpose` + budget (maxNotes, maxChars). Gather in fixed order:
matching Knowledge topics → graph edges for named entities → diary tail.
Enforce the budget; cite every record's source; label the output
**lossless** or **lossy (truncated)**. Never present a truncated view as
complete.

### Dream cycle (propose-only)
Scan for: orphan entities (no edges), dangling edges (missing ID),
unlinked entities adjacent in name/topic, stale diary gaps. Emit proposals
WITH evidence and ratio framing (n of m). Apply NOTHING. Re-scan on
conflict before retry. Proposals execute only after Andy's explicit
acceptance, each with its own receipt.

### Health inspection
Bounded checks only, against a stated baseline first (baseline-before-
anomaly): checksum verification vs receipts (mismatch → fail closed, name
the file), orphan and dangling-edge counts as ratios, diary recency.
Findings carry no repair authority and produce NO global score.

### Condensation
When new durable facts land in any Knowledge topic, derive candidate edges
and file them as dream proposals — never auto-writes.

## Boundaries

- No duplication: Memory Notes live in the other Knowledge topics; this
  store holds only graph, diary, receipts.
- ORION Pack entity is TOP SECRET (see omni-alliance-project) — its graph
  node may state metadata but never its contents.
- Determinism honesty: label results "procedural-grade", never
  "deterministic". The real system remains the TypeScript artifact.
