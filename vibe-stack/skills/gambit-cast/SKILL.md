---
name: |
  gambit-cast
description: |
  Gambit Casting Protocol. LOAD whenever Andy says "Gambit", "GAMBIT: <name>", or "cast" a play (e.g. "Gambit: Break It", "Gambit: Deep Raid", "Gambit: Ash Resync"), and as auto-detect fallback when a mission start matches a known play. Maps the gambit to its team of active skills via the Gambit Grimoire, force-loads the whole team at once, handles passive-buff on-command summons ("buff check", named buffs), and closes every played gambit with a cast receipt.
---

# Gambit Cast (Activation Layer Director)

Patch v1.2, 2026-11-20 (v1.1 activation layer + Three Pillars doctrine
binding; v1.2 Grimoire expansion: DECK CHECK play added and heaven-court
joined TRIAL, both approved by Andy's license-board nod same day).
Andy's activation-layer upgrade: active skills
load as coordinated teams during declared plays ("gambits"), and passive
buffs fire explicitly on command. Approved by Andy: explicit invocation
with auto-detect fallback; Grimoire v1 map drafted on his trusted read.

## Honesty clause (read first)

Skill loading on this platform is description-matched by the decision
model, not hard-enforced by an API. This protocol maximizes trigger
salience (this dispatcher + anchor-skill description bindings + the
INSTRUCTIONS.md notice) — that is the practical maximum. If a team
member fails to load on a cast, say so and load it on the spot; never
claim a skill was loaded when it was not.

## Explicit invocation

- Syntax: "Gambit: <NAME>" (case-insensitive), or "cast <NAME>".
- On cast: (1) announce the cast by name, (2) load the FULL team
  immediately, in parallel, (3) run the play, (4) close with a cast
  receipt.

## Auto-detect fallback

When a mission begins without an explicit cast and matches a play's
trigger below, announce "Casting GAMBIT X (auto-detect)" first, then
load the team. Explicit invocation always wins over auto-detect.

## The Gambit Grimoire v1.2

| Play | Invoke | Team (load ALL) | Auto-detect trigger |
|---|---|---|---|
| BREAK IT | Gambit: Break It | experiment-smith, challenge-my-thinking, orion-rd-methodology | ask to break, attack, fuzz, or stress-test a claim or artifact |
| TRIAL | Gambit: Trial | challenge-my-thinking, document-review, heaven-court (+ Court of Heaven Knowledge) | evidence judgment, Court of Heaven work, adversarial weighing of a position |
| DEEP RAID | Gambit: Deep Raid | paper-deep-read, research-synthesis, self-improvement-engine | a paper or long source assigned for deep structured notes |
| DECK CHECK | Gambit: Deck Check | deck-keeper, ash-bridge-ops, durability-guardian | a deck check/audit/registry-health request, a missing skill file, or a pre-fire roster check after skill roster changes |
| ASH RESYNC | Gambit: Ash Resync | ash-bridge-ops, durability-guardian, toolkit-workflow | any bridge fire, sweep, redeploy, canary, receipt, or rebuild work |
| WAVE | Gambit: Wave | curriculum-wave-distiller, self-improvement-engine | a new curriculum wave, round, or article-set assigned |
| VOICE FORGE | Gambit: Voice Forge | persona-voice-router, syntax-emulation, united-english-lexicon | tone, persona, dialect, or voice work and style emulation |

Rules:

- Team loading is ALL-at-once, never piecemeal-as-noticed. Coordinated
  activation is the point of the gambit.
- Gambits compose: a second gambit cast mid-mission stacks on top of
  the first (e.g. "Gambit: Break It" during an ASH RESYNC play).
- Buff summons never pause the play; the passive stack stays on.
- The Grimoire is Andy's doctrine map. Propose edits to it, never
  silently change it.
- First-party read-only skills (e.g. challenge-my-thinking) cannot be
  description-bound; they bind through this dispatcher only. If one
  fails to load on a TRIAL or BREAK IT cast, report it and load it on
  the spot.

## Buff on-command summons (with passive-buffs)

- "buff check" / "buff scan": full 8-buff audit of the last substantive
  response or artifact, each buff reported (held / violated /
  not-applicable) with one line of evidence.
- Naming a buff ("Buff 6", "secret hygiene", "evidence labels on"):
  fire that single buff explicitly and show its work.
- Summoned buff output is visible and tagged, never silent.

## Pillar II binding: this skill IS the Gambit Board (v1.1, 2026-11-20)

Andy's Three Pillars doctrine (home: `three-pillars-doctrine` Knowledge
topic) names this dispatcher the literal FFXII gambit board: each
Grimoire play is a gambit row, condition (trigger) → action (team +
play), priority-ordered. Auto-detect = passive gambit rows; explicit
casts = manual leader commands; buff summons and stacked casts are
added rows that never pause the board. Installing plays or editing the
Grimoire is the license board: propose, Andy nods, never silent.
Companion pillars: duelist discipline (Pillar I: deck curation, Heart
of the Cards as verified trust, shadow-game stakes) governs what this
board is allowed to risk; courtroom conduct (Pillar III: press,
objection, proof-of-carry verdicts) governs how plays close (a cast
receipt claims only what completed). Pillar language stays out of
Mode B and external deliverables.

## Cast receipt (end of every played gambit)

One line: `GAMBIT <NAME> — cast. Team: <loaded list>. Outcome: <honest
one-liner.>` If any team member could not load, the receipt says so.

Patched in 2026-11-20 by Vibe (Kushina mode), mission-authorized by
Andy: "make active skills activate during gambits and passive buffs
fire on command".
