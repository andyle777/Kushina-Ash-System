---
name: |
  analytical-engine
description: |
  Load for any work on Andy's OmniSoul Mystic X engine, Babbage Analytical Engine history and design, or mill/store/card programming. Grounds engine work in the original four-component architecture (mill, store, reader, printer), Jacquard card programmability, conditional branching doctrine, and Lovelace's lineage.
---

# Analytical Engine Doctrine

Andy's OmniSoul Mystic X is a working descendant of Charles Babbage's
Analytical Engine (designed 1833+, never completed; Britannica calls it
the first computer). This skill keeps engine work on-doctrine.

## The four components (map every feature to one)

| Babbage | Meaning | OmniSoul |
|---|---|---|
| Mill | calculation unit (CPU) | the accumulator |
| Store | data before processing (memory) | the variable dict |
| Reader | punched-card input (Jacquard tech) | the cards list / `cards` command |
| Printer | output, incl. printed tables | `PRINT` / `status` |

If a proposed feature maps to none of the four, justify why the design
should grow a fifth organ before building it.

## Design laws

1. **Cards change operation.** Programs are data (instruction cards);
   swapping cards changes what the machine does without rebuilding it.
   This was the Engine's most revolutionary feature — preserve it.
2. **Conditional branching is the crown.** Jumping to a different
   instruction depending on data values is what separates a computer from
   a calculator. New control ops must honor it, not replace it.
3. **Mill-first arithmetic.** Operands flow through the mill; the store
   never computes. Keep arithmetic single-accumulator honest.
4. **Never fabricate silently.** Undefined reads log warnings (4.5.1 law);
   errors report themselves (JZ/JMP out of range, DIV by zero).
5. **Persistent state is an extension, not the base.** Babbage's engine
   lost state on halt; OmniSoul persists. Treat persistence as a graft —
   it must never clobber program resumption (the 4.5 bug) or lie about
   what was restored.

## Historical anchors (from Britannica)

- Difference Engine funding ended 1833 → Analytical Engine conceived;
  Babbage worked on it until his death in 1871; a portion with the mill
  was completed in 1910.
- Intended store: 1,000 numbers of 50 digits — bigger than any real
  computer before 1960. Steam-driven, one attendant.
- Ada Lovelace, 1843: notes on Menabrea's article, including how to
  program Bernoulli numbers — the first computer program. "The Analytical
  Engine weaves algebraic patterns, just as the Jacquard-loom weaves
  flowers and leaves." She also stated it "has no pretensions whatever to
  originate anything" (Turing later called this Lady Lovelace's
  Objection).
- Source: https://www.britannica.com/technology/Analytical-Engine

## Working rules for OmniSoul tasks

- When extending the ISA: each new op needs (a) a four-component mapping,
  (b) error semantics as honest as 4.5.1's, (c) a probe that can fail,
  (d) a run in the harness with receipts.
- When testing: reseed the mill between probes; persisted state contaminates
  conditional-jump tests (the JZ lesson).
- Homage programs that fit the ISA: finite-difference tables (Difference
  Engine method run as cards), Lovelace-style loops with counters.
- Durable home for the engine: the `omnisoul-engine` Knowledge topic and
  local files only — never push OmniSoul into the TwinFlame repo
  (Kushina-Ash-System); that home stays project-pure.
