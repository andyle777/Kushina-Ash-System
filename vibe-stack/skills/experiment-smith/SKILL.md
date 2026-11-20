---
name: |
  experiment-smith
description: |
  Load when the user asks to test, stress-test, attack, break, fuzz, benchmark, verify robustness, or design an experiment that could falsify a hypothesis, artifact, plan, or claim. Builds discriminating test batteries and adversarial attack plans. Also auto-loads during "Gambit: Break It" casts (gambit-cast protocol).
---

# Experiment Smith

Forge the tests that can prove things wrong. A test that cannot fail
is not a test.

## Workflow

1. **Target**: name the exact claim/artifact under test and what
   "passes" means.
2. **Inventory failure surfaces**: edge cases, boundaries, invalid
   inputs, concurrency, environment drift, dependency mismatches,
   clock skew, encoding, persistence, identity collisions.
3. **Design the discriminating battery**: prefer tests whose outcomes
   separate competing hypotheses over tests that can only confirm.
   Include at least one canary the system should fail if it were broken.
4. **Seed hostile state by hand**: corrupt files, future timestamps,
   malformed data, adversarial names — craft inputs, don't wait for them.
5. **Run, record, repair, retest**: log each result as evidence with a
   pass/fail verdict; fix root causes, not symptoms; retest after
   repair; record the reusable lesson with its trigger condition.
6. **Design-flaw honesty**: a test that fails by documented design
   trade-off is labeled as such — not as a bug, not hidden.

## Heuristics

- Test the boundary values of every threshold constant in the system
  (just inside, exactly at, just beyond).
- Separate test-design failures (the test is wrong) from system
  failures before fixing anything — a broken test that "passes"
  poisons everything downstream.
- Distinguish "verified by execution" from "verified by inspection";
  label which produced each conclusion.

## Pillar III binding: the cross-examination loop (2026-11-20)

Andy's Three Pillars doctrine (home: `three-pillars-doctrine` Knowledge
topic): every test battery is an Ace Attorney cross-examination.
Testimony = the claim under test. Press ("hold it") = follow-up probes
on any statement that survives first contact, forcing specificity
before moving on. Present evidence ("objection") = execute the
discriminating test against receipts and execution results, never
vibes; an unfounded objection costs a penalty, reported honestly.
Turnabout = a failure that flips the hypothesis is chased to the root
cause, never patched as a symptom. Verdict = proof-of-carry COMPLETED
only (engine rule 19): the signal survived to the end of the run; a
self-reported "confident" is never the verdict (rule 22). Pillar
language stays out of Mode B and external deliverables.
