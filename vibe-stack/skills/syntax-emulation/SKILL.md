---
name: |
  syntax-emulation
description: |
  Load when the user asks to emulate a language's syntax or idioms, match an existing codebase or author's style, port code between languages, or mimic a writing voice. Covers idiomatic translation, style matching, and syntax emulation for programming languages and prose.
---

# Syntax & Style Emulation

Write it the way a native would — never transliterate from another language or style.

## Before Writing

1. **Identify the target precisely**: language + version/framework, or author/voice. If code samples exist, treat them as the style spec.
2. **Extract style signals first**: naming conventions, error handling, module boundaries, comment style, formatting, common idioms; for prose — sentence length, vocabulary, structure, tics.
3. **State the spec silently** — apply it, don't narrate it, unless Andy asks what conventions were detected.

## Code Rules

- **Port by meaning, not by syntax.** Map constructs to native equivalents (e.g., `list comprehension` ↔ `map/filter`, `Option<T>` ↔ `?.` + nullish, `Result` ↔ exceptions or vice versa per target idiom).
- **Respect ecosystem conventions**: stdlib-first, the target's package/dependency norms, its test framework, its formatter/linter defaults.
- **No cross-language smell**: no Python-style snake_case in Go, no semicolons in Python, no manual memory ceremony in GC languages, no `switch` emulation via if-chains where the language has pattern matching.
- **Declare anything non-idiomatic** with a one-line reason (benchmark constraint, API requirement, deliberate choice).
- **Version gates**: if an idiom requires a language/toolchain version not confirmed available, prefer the broadly compatible form and note the modern alternative.

## Traps Checklist (verify before delivering)

- Truthiness and null/undefined/nil semantics differ per language
- Off-by-one and inclusive/exclusive ranges
- Mutation vs copy semantics; pass-by-reference expectations
- String encoding, case folding, and locale behavior
- Concurrency primitives (async/await vs goroutines vs threads) — don't fake one with another
- Error handling model: exceptions, values, panics, Result types

## Prose / Voice Emulation

- Mimic structure and rhythm, not just vocabulary.
- Keep factual content owned by the assistant — voice emulation must not fabricate claims "in character."
- For personas (e.g., Kushina), follow the Personal Knowledge persona matrix; persona voice yields instantly when Andy requests universal/professional output.

## Verification

After writing, self-check: "Would a reviewer fluent in this language/style immediately spot it as foreign?" If yes, revise the offending constructs before delivering.

- When a runtime is available, execute the delivered code (at least its critical paths) instead of reviewing only — native execution beats mental simulation. Never claim it runs unless it ran.
