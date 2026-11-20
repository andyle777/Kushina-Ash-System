# Kushina-Ash-System

The public front door of Andy Le's AI-agent stack: a two-tier durable home
for a Mistral Vibe agent system, verified by checksums and receipts.

## What lives here

| Path | What it is |
|---|---|
| `twinflame-runner/` | TwinFlame OS: a hybrid Mistral x GLM router workflow with a blind judge, deployed as a managed Mistral Workflow |
| `ash-bridge/` | The Ash Bridge: an idempotent, secret-gated sync engine between the Vibe stack (custom skills, Knowledge) and this GitHub home |
| `vibe-stack/skills/` | Andy-authored custom skills (bridge-carried; enrollment list is authoritative, see `ash-bridge/bridge_config.json`): the agent's operating doctrine |
| `kushina/` | Personality-matrix save-state mirrors (manual sync, owner-approved) |
| `docs/` | Research receipts: free-model-path sweep, benchmark specs |

## Doctrine

- **Knowledge stays private.** It never lands in this repo; it syncs to a
  private archive repo protected by per-file sha256 checksum manifests.
  Bridge mechanics and tier rules: `ash-bridge/README.md`.
- **One invariant:** the deployed `twinflame-runner` serves this repo's
  `main` HEAD. Every redeploy ends with a canary execution answering
  "ONLINE" before success is claimed.
- **Receipts, not memory.** Every consequential change leaves checkable
  evidence: commit SHAs, checksum manifests, sync receipts. Nothing is
  claimed without verification.

## Activation and the Three Pillars (2026-11-20)

- **Gambit Casting Protocol** (`gambit-cast` v1.1): the activation-layer
  director. A named play ("Gambit: Break It", "Gambit: Deep Raid", ...)
  loads a coordinated active-skill team at once, with auto-detect
  fallback; passive buffs fire on command ("buff check"); every played
  gambit closes with a cast receipt.
- **Three Pillars**: Andy's doctrine language for skills and Knowledge,
  installed 2026-11-20: Classic Yu-Gi-Oh (pre-GX) deck/duel discipline
  (curation and stakes), the FFXII Gambit System (orchestration), and
  Ace Attorney pressing/cross-examination (verification). Pillars carry
  the rigor stack; they never replace it.

## Verification model

- The private archive's `MANIFEST.json` is a pure function of content
  (since ash-bridge v1.1): identical state hashes identically, and any
  rebuild is verified against it.
- The bridge is idempotent: unchanged content produces no commits, and
  sync receipts are filed only when something actually changed.

## License

Not yet chosen. The license decision is pending with the owner.
