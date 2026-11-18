# TwinFlame Free-Paths: Every Free Route to GLM-5.3 (verified 2026-11-18)

Companion to `TWINFLAME_OS.md` and `BENCHMARK.md`. A deep-research sweep of every
zero- or near-zero-cost method to run or harvest the real GLM-5.3 flagship for
TwinFlame Layer 2. Every claim below was live-verified on 2026-11-18 unless
labeled otherwise. Evidence labels: Verified / Reported / Negative.

## Tier S - genuinely free, real GLM-5.3

### S1. Cloudflare Workers AI `@cf/zai-org/glm-5.3` (Verified) - RECOMMENDED PRIMARY
- The real flagship, hosted by Cloudflare: function calling, reasoning, zero data retention.
- Free allocation: 10,000 Neurons/day per account, no credit card. Beyond that $0.011/1,000 neurons.
- GLM-5.3 unit pricing: $1.40/M input, $4.40/M output (= 127,273 neurons/M input, 400,000/M output).
- Free daily allowance buys ~78.6K input-only tokens, or ~7-8 gauntlet-sized calls
  (2.5K in / 2.5K out each ~ 1,318 neurons). `glm-5.3-flash` ($0.15/$0.50) stretches it to ~60-70 calls/day.
- REST + OpenAI-compatible endpoint. Free-tier intent is dev/testing: fine for a benchmark battery.
- Docs: developers.cloudflare.com/workers-ai/models/glm-5.3/ and /platform/pricing/

### S2. BigModel.cn new-user pack: 20M tokens covering glm-5.3 (Verified offer, AMBER friction)
- Official pricing: glm-5.3 at RMB 8/M input, 28/M output. OpenAI-compatible base URL:
  `https://open.bigmodel.cn/api/paas/v4`.
- New-user gift: 20,000,000 tokens, explicitly covering glm-5.3 (verified 2026-08-30 by
  CyberEggs listing; corroborated by multiple independent sources). Invite links stack up to 200M.
- Friction: Chinese phone registration + real-name verification; untested for non-CN users.
  Token validity disputed (permanent vs expiring). One-hour signup experiment pending.

### S3. ZCode new-user trial (Verified, prior sweep)
- 5 days x 3M GLM-5.3 tokens/day, no payment method, inside the ZCode desktop app.
- Not an API: harvest into the shipped BYO challenger fields (`zai_answer` et al).

### S4. chat.z.ai free web chat (Verified)
- Free web chat, no paid chat subscription exists (uzneo pricing review, verified 2026-10-29).
- Limits unpublished. Manual copy into BYO; the product's intended use.

### S5. UnoRouter `glm-5.3:free` (Verified live, variable availability)
- $0.00 in/out, no card, OpenAI-compatible `https://api.unorouter.com/v1`.
- Live check showed upstream providers rate-limit-busy, recovery within hours. Overflow-only.

### S6. Puter.js `z-ai/glm-5.3` (Verified, user-pays mechanics)
- No-key browser JS (`puter.ai.chat`, model `z-ai/glm-5.3`) + free playground.
- "User-Pays": each end user covers their own costs. For personal use the developer IS the user.
- Browser surface, not a server API: a harvest-to-BYO path, not workflow-integrable.

## Tier A - free-adjacent, partially verified, or middleweight

- Together AI free `zai-org/GLM-5.3-FP8` (Reported, conflicts with primary): the llmperks directory
  claims a free fair-use endpoint; Together's official quickstart lists only paid
  `zai-org/GLM-5.3` ($1.40/$4.40) and Flash ($0.15/$0.50), and no free-models doc page exists.
  One free signup settles it.
- Together Link: free CLI running GLM 5.3 inside Claude Code/Codex/OpenCode; inference bills
  to your Together account. Not free (Verified).
- NVIDIA NIM: build.nvidia.com hosts `z-ai/glm-5.3-flash` with free developer credits (flash only).
- Novita referral: give $10 / earn $10 credits; hosts GLM-5.3; also the HF-routing upstream.
- Hugging Face Inference Providers: free accounts get $0 monthly credits (PRO $2/mo). Paid path.
- OrcaRouter `z-ai/glm-5.3-flash-free`: free flash tier on a router (page live, thin details).
- DeepInfra: $5 signup trial credit (one source adds $5/mo recurring); hosts GLM-4.7, not GLM-5.3.
- SiliconFlow: trial-credit claims conflict ($200 vs $1); catalog auth-gated; GLM-5.3 unverified. AMBER.
- Z.ai genuinely-free API models: GLM-4.7-Flash, GLM-4.5-Flash, GLM-4.6V-Flash at $0 (wrong weight class).
- OpenCode Zen: GLM-5.3 at list price, paid (included to close the question).

## Tier B - flat-rate seams and the endgame

- Z.ai Coding Plan Lite: $18/mo ($12.60 yearly), 2,000 credits/5h & 10,000/week (~120 flagship
  prompts per 5h pool), credits ONLY inside supported coding tools (never general API), 2x peak
  cost Mon-Fri 14:00-18:00 UTC+8. Flat-rate harvest seam via ZCode, not free.
- OpenRouter promo: glm-5.3 input at $0.0699/1M (metered, not free).
- Self-host `zai-org/GLM-5.3`: 753B params, ~756GB FP8, ~223-256GB memory. Free forever, hardware-gated.

## Verified negatives

- No free GLM-5.3 on OpenRouter (22 GLM models live-checked, zero `:free`), Groq, Cerebras, or the
  Z.ai API (no signup credits; balance is card-topped-up only).
- Coding Plan keys do not work for general API calls (split 2026-10-16).
- HF free accounts: $0 monthly inference credits.

## Phase 2 free protocol

1. Cloudflare free account + Workers AI token = daily flagship drip (~7-8 gauntlet calls/day).
2. ZCode trial burst (15M tokens over 5 days) for the concentrated G1-G5 gauntlet.
3. All harvested answers ride the BYO challenger fields into the blind judge at $0, honest receipts.
4. Optional one-hour signup experiments: Together free-FP8, BigModel 20M pack. Record receipts either way.
5. Phase 3 option (owner decision): wire Cloudflare as a second provider in the zai layer activity.

## Open questions

1. Does Together actually serve a free GLM-5.3-FP8 endpoint? One signup settles it.
2. Can a non-CN user complete BigModel real-name verification? One signup settles it.
3. Actual neurons per gauntlet call in practice (7-8/day is arithmetic from published rates).
4. chat.z.ai unpublished free limits.
5. Is the OpenRouter $0.0699/1M input promo standing?

Sweep receipts: 2026-11-18, 14 primary sources fetched live, 6 broad + 8 targeted searches.
Full report with source-credibility table: twinflame-free-paths canvas (private mirror).
