# TwinFlame Engineering Lessons

Each lesson installs with its trigger condition.

## 1. Reasoning models return chunked content

**When calling Mistral reasoning models (Large 4), then expect
`message.content` to be a list of `ThinkChunk` / `TextChunk` objects, not a
string.** Flatten recursively: check `.text` first, then `.thinking` /
`.content`; split answer from reasoning by chunk type (`type == "thinking"`
or presence of a `thinking` attribute). A plain-string fallback stays for
non-reasoning models.

Cost of learning this: three full completions burned on identical retries.

## 2. Validate output serialization before wiring retries

**When an activity has a retry policy, then validate that serialization
succeeds on the very first attempt's shape.** A Pydantic `ValidationError`
is deterministic: retrying it burns tokens and changes nothing. Guard
risky serialization, or validate the response shape before constructing
the output model.

## 3. A run that ends at exactly max_tokens is truncated

**When `tokens_out == max_tokens`, then the answer is clipped - re-fire
with a bigger budget instead of accepting it.** Duel-quality answers from
Mistral Large 4 with thinking need 4096 tokens of headroom. The worker's
default is therefore 4096.

## 4. Budget ~60 seconds for a 2.5k-token reasoning answer

**When polling `get_workflow_execution` for a Large 4 run, then budget
roughly 100 poll iterations.** Thinking generation takes about 60 s wall
time for a 2.5k-token answer.

## 5. Blind protocol for engine duels

**When running a duel, then pre-commit each contestant's answer to a file
before reading the other's output.** No peeking, no rewriting after the
reveal - otherwise the receipt is worthless.
