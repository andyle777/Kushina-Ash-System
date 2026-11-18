"""TwinFlame OS: the 3-layer fusion substrate.

Layers:
  - mistral  : Mistral Large 4 via the deployment service account (no key)
  - zai      : GLM-5.3 via Z.AI_API_KEY (workspace secret, bound at deploy)
  - hybrid   : both engines in parallel + a blind Mistral judge that may
               crown either answer or produce a pure synthesis

A dynamic director classifies each prompt when layer="auto" (the default).
Andy's rulings on record (2026-11-18):
  1. default layer = auto (dynamic director); all layers manually callable
  2. judge latitude = pure synthesis allowed; may lead with any engine
  3. cost ceiling = none; receipts still MEASURE estimated cost
  4. GLM thinking = full reasoning traces in receipts, nothing redacted

Degradation is always honest: every fallback lands in `degradations[]`.
"""

import asyncio
import random
import time
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel

import mistralai.workflows as workflows
from mistralai.workflows import Depends
from mistralai.workflows.client import get_mistral_client

from app.workflows.twinflame_mistral import _flatten

# Env reads happen INSIDE activities (unsandboxed). Module-level os.environ
# access runs inside the Temporal workflow sandbox and is restricted.
ZAI_ENDPOINT_DEFAULT = "https://api.z.ai/api/paas/v4/chat/completions"
ZAI_MODEL_DEFAULT = "glm-5.3"
ENGINE_TIMEOUT_S = 120

# Published list prices, USD per 1M tokens (input, output). Estimates only.
PRICES: Dict[str, Tuple[float, float]] = {
    "mistral-large-4": (0.70, 2.10),
    "glm-5.3": (1.40, 4.40),
}

# --- Dynamic director (deterministic heuristics; runs inside the workflow) ---

MISTRAL_SIGNALS = [
    "quick", "snippet", "one-liner", "one liner", "regex", "lint", "typo",
    "rename", "short answer", "fix this",
]
ZAI_SIGNALS = [
    "implement", "build ", "build a", "build an", "code a", "code this",
    "write a function", "write a script", "algorithm", "agentic", "tool call",
]
HYBRID_SIGNALS = [
    "architecture", "design", "migrate", "migration", "review", "audit",
    "plan", "roadmap", "compare", "tradeoff", "trade-off", "critical",
    "high-stakes", "comprehensive", "end-to-end", "refactor", "strategy",
    "evaluate", "deep dive",
]


def _direct(prompt: str) -> Tuple[str, List[str]]:
    """Classify a prompt and pick a layer. Deterministic: string matching only."""
    p = prompt.lower()
    for layer, signals in (
        ("mistral", MISTRAL_SIGNALS),
        ("zai", ZAI_SIGNALS),
        ("hybrid", HYBRID_SIGNALS),
    ):
        matched = [s for s in signals if s in p]
        if matched:
            return layer, matched
    return "hybrid", []  # full-fusion default when no signal matches


# --- Schemas ---


class TwinFlameOSInput(BaseModel):
    prompt: str
    layer: str = "auto"  # auto | mistral | zai | hybrid
    system: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.3
    judge_model: str = "mistral-large-4"


class EngineReceipt(BaseModel):
    engine: str
    text: str
    thinking: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    latency_ms: int = 0
    truncated: bool = False
    cost_usd_est: float = 0.0


class JudgeReceipt(BaseModel):
    used: bool = False
    model: str = "mistral-large-4"
    verdict: str = ""  # "a" | "b" | "synthesis" | "judge-failed"
    thinking: str = ""
    label_a_engine: str = ""  # true engine behind label A, logged post-hoc
    label_b_engine: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd_est: float = 0.0
    notes: str = ""


class TwinFlameOSOutput(BaseModel):
    answer: str
    layer_used: str  # mistral | zai | hybrid | degraded-mistral | degraded-zai
    director: Dict[str, Any] = {}
    engines: List[EngineReceipt] = []
    judge: JudgeReceipt = JudgeReceipt()
    degradations: List[str] = []
    total_cost_usd_est: float = 0.0


def _cost(engine: str, tokens_in: int, tokens_out: int) -> float:
    pin, pout = PRICES.get(engine.split("@")[0], (0.0, 0.0))
    return round(tokens_in / 1e6 * pin + tokens_out / 1e6 * pout, 6)


def _truncated(tokens_out: int, max_tokens: int) -> bool:
    return tokens_out > 0 and tokens_out >= max_tokens


# --- Layer 1: Mistral ---


@workflows.activity()
async def mistral_layer(
    task: TwinFlameOSInput,
    client=Depends(get_mistral_client),
) -> EngineReceipt:
    t0 = time.monotonic()
    messages: List[Dict[str, str]] = []
    if task.system:
        messages.append({"role": "system", "content": task.system})
    messages.append({"role": "user", "content": task.prompt})

    kwargs: Dict[str, Any] = {
        "model": "mistral-large-4",
        "messages": messages,
        "max_tokens": task.max_tokens,
        "temperature": task.temperature,
    }
    if task.temperature == 0:
        kwargs["top_p"] = 1.0  # greedy-sampling guard (Mistral API error 3054)

    response = await client.chat.complete_async(**kwargs)
    latency_ms = int((time.monotonic() - t0) * 1000)

    usage = response.usage
    tokens_in = (usage.prompt_tokens or 0) if usage else 0
    tokens_out = (usage.completion_tokens or 0) if usage else 0
    engine = response.model or "mistral-large-4"

    raw = response.choices[0].message.content if response.choices else None
    answer, reasoning = "", ""
    if isinstance(raw, list):
        for chunk in raw:
            body = _flatten(chunk)
            chunk_type = str(getattr(chunk, "type", "") or "")
            if chunk_type == "thinking" or hasattr(chunk, "thinking"):
                reasoning += body
            else:
                answer += body
    else:
        answer = _flatten(raw)
    if not answer.strip() and raw is not None:
        answer = _flatten(raw)  # never-return-empty guard

    return EngineReceipt(
        engine=engine,
        text=answer,
        thinking=reasoning,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        latency_ms=latency_ms,
        truncated=_truncated(tokens_out, task.max_tokens),
        cost_usd_est=_cost(engine, tokens_in, tokens_out),
    )


# --- Layer 2: Z.ai / GLM-5.3 ---


def _extract_zai(message: Dict[str, Any]) -> Tuple[str, str]:
    """Chunk-tolerant extraction: content may be a string, a list of dicts,
    and thinking may live in reasoning_content or in thinking-type chunks."""
    thinking = str(message.get("reasoning_content") or "")
    content = message.get("content")
    if content is None:
        return "", thinking
    if isinstance(content, str):
        return content, thinking
    if isinstance(content, list):
        text = ""
        for piece in content:
            if isinstance(piece, dict):
                if str(piece.get("type", "")) == "thinking" or "thinking" in piece:
                    thinking += str(piece.get("thinking") or piece.get("text") or "")
                else:
                    text += str(piece.get("text") or "")
            else:
                text += str(piece)
        return text, thinking
    return str(content), thinking


@workflows.activity()
async def zai_layer(task: TwinFlameOSInput) -> EngineReceipt:
    import os  # activity-local: sandbox-safe

    import httpx  # activity-local: importing httpx at module level breaks the Temporal workflow sandbox

    api_key = os.environ.get("ZAI_API_KEY", "").strip()
    endpoint = os.environ.get("ZAI_ENDPOINT", ZAI_ENDPOINT_DEFAULT)
    model = os.environ.get("ZAI_MODEL", ZAI_MODEL_DEFAULT)
    if not api_key:
        raise RuntimeError("ZAI_API_KEY is not bound to this deployment")

    t0 = time.monotonic()
    messages: List[Dict[str, str]] = []
    if task.system:
        messages.append({"role": "system", "content": task.system})
    messages.append({"role": "user", "content": task.prompt})

    body: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": task.max_tokens,
        "temperature": task.temperature,
        "stream": False,
    }
    if task.temperature == 0:
        body["top_p"] = 1.0  # greedy-sampling guard

    async with httpx.AsyncClient(timeout=ENGINE_TIMEOUT_S) as http:
        resp = await http.post(
            endpoint,
            json=body,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
    latency_ms = int((time.monotonic() - t0) * 1000)
    if resp.status_code != 200:
        raise RuntimeError(f"Z.ai HTTP {resp.status_code}: {resp.text[:300]}")
    data = resp.json()

    choice = (data.get("choices") or [{}])[0]
    text, thinking = _extract_zai(choice.get("message") or {})
    usage = data.get("usage") or {}
    tokens_in = int(usage.get("prompt_tokens") or 0)
    tokens_out = int(usage.get("completion_tokens") or 0)
    if not text.strip() and not thinking.strip():
        raise RuntimeError("Z.ai returned an empty response")

    return EngineReceipt(
        engine=model,
        text=text,
        thinking=thinking,  # full trace, nothing redacted (ruling #4)
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        latency_ms=latency_ms,
        truncated=_truncated(tokens_out, task.max_tokens),
        cost_usd_est=_cost(model, tokens_in, tokens_out),
    )


# --- Layer 3: blind judge (pure synthesis allowed) ---


@workflows.activity()
async def hybrid_judge(
    task: TwinFlameOSInput,
    a: EngineReceipt,
    b: EngineReceipt,
    client=Depends(get_mistral_client),
) -> Tuple[str, JudgeReceipt]:
    """Blind judging: labels are randomized here (inside an activity, never in
    the deterministic workflow), engine names revealed only post-hoc."""
    slots = [("mistral", a), ("zai", b)]
    random.shuffle(slots)
    (label_a_engine, answer_a), (label_b_engine, answer_b) = slots

    def _annotated(engine: str, receipt: EngineReceipt) -> str:
        note = ""
        if receipt.truncated:
            note = (
                "\n[Note: this answer hit its max_tokens ceiling and may be "
                "incomplete; weight it accordingly.]"
            )
        return receipt.text + note

    system_prompt = (
        "You are the TwinFlame Judge, an impartial fusion editor. You receive "
        "one prompt and two anonymous answers, labeled A and B, from two "
        "different frontier models. Evaluate both for correctness, depth, and "
        "operational judgment, then write the best possible final answer for "
        "the user. You may crown A, crown B, or produce a pure synthesis that "
        "leads with the stronger answer and borrows the best material from the "
        "other - synthesis is fully allowed. Your output must follow this "
        "format exactly:\n"
        "VERDICT: A  (or VERDICT: B, or VERDICT: SYNTHESIS)\n"
        "---\n"
        "The fused final answer, with no preamble."
    )
    user_prompt = (
        f"PROMPT:\n{task.prompt}\n\n"
        f"=== Answer A ===\n{_annotated(label_a_engine, answer_a)}\n\n"
        f"=== Answer B ===\n{_annotated(label_b_engine, answer_b)}"
    )

    t0 = time.monotonic()
    response = await client.chat.complete_async(
        model=task.judge_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=task.max_tokens,
        temperature=task.temperature,
    )
    latency_ms = int((time.monotonic() - t0) * 1000)
    usage = response.usage
    tokens_in = (usage.prompt_tokens or 0) if usage else 0
    tokens_out = (usage.completion_tokens or 0) if usage else 0
    engine = response.model or task.judge_model

    raw = response.choices[0].message.content if response.choices else None
    body, reasoning = "", ""
    if isinstance(raw, list):
        for chunk in raw:
            text_part = _flatten(chunk)
            if str(getattr(chunk, "type", "") or "") == "thinking" or hasattr(chunk, "thinking"):
                reasoning += text_part
            else:
                body += text_part
    else:
        body = _flatten(raw)

    verdict = "unparsed"
    fused = body
    lines = body.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip().upper().replace(" ", "")
        for token, name in (("VERDICT:A", "a"), ("VERDICT:B", "b"), ("VERDICT:SYNTHESIS", "synthesis")):
            if stripped.startswith(token):
                verdict = name
                rest = lines[i + 1:]
                if rest and rest[0].strip() == "---":
                    fused = "\n".join(rest[1:]).strip()
                else:
                    fused = "\n".join(rest).strip()
                break
        if verdict != "unparsed":
            break

    receipt = JudgeReceipt(
        used=True,
        model=engine,
        verdict=verdict,
        thinking=reasoning,  # full judge trace, nothing redacted
        label_a_engine=label_a_engine,
        label_b_engine=label_b_engine,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        cost_usd_est=_cost(engine, tokens_in, tokens_out),
        notes=f"labels randomized in-activity; judge latency {latency_ms}ms",
    )
    return fused, receipt


# --- The OS workflow ---


@workflows.workflow.define(
    name="twinflame-os",
    workflow_display_name="TwinFlame OS",
    workflow_description=(
        "3-layer fusion substrate: mistral (Le Chonk, service account), "
        "zai (GLM-5.3 via workspace secret), hybrid (parallel fan-out + "
        "blind judge with pure synthesis allowed). layer=auto runs the "
        "dynamic director. Honest degradation, full receipts."
    ),
)
class TwinFlameOSWorkflow:
    @workflows.workflow.entrypoint
    async def run(self, task: TwinFlameOSInput) -> TwinFlameOSOutput:
        requested = task.layer
        if requested == "auto":
            decision, signals = _direct(task.prompt)
        elif requested in ("mistral", "zai", "hybrid"):
            decision, signals = requested, []
        else:
            raise ValueError(f"unknown layer '{requested}': use auto|mistral|zai|hybrid")
        director = {"requested": requested, "decision": decision, "signals": signals}

        engines: List[EngineReceipt] = []
        degradations: List[str] = []
        judge = JudgeReceipt()
        answer = ""
        layer_used = decision

        if decision == "mistral":
            r = await mistral_layer(task)
            engines.append(r)
            answer = r.text

        elif decision == "zai":
            try:
                r = await zai_layer(task)
                engines.append(r)
                answer = r.text
            except Exception as exc:
                degradations.append(f"zai layer failed ({exc}); degraded to mistral")
                r = await mistral_layer(task)
                engines.append(r)
                answer = r.text
                layer_used = "degraded-mistral"

        else:  # hybrid
            m_res, z_res = await asyncio.gather(
                mistral_layer(task), zai_layer(task), return_exceptions=True
            )
            m = m_res if not isinstance(m_res, BaseException) else None
            z = z_res if not isinstance(z_res, BaseException) else None
            if m is None and z is None:
                raise RuntimeError(
                    f"both engines failed: mistral={m_res}; zai={z_res}"
                )
            if z is None:
                degradations.append(f"zai engine failed ({z_res}); degraded to mistral")
                engines.append(m)
                answer = m.text
                layer_used = "degraded-mistral"
            elif m is None:
                degradations.append(f"mistral engine failed ({m_res}); degraded to zai")
                engines.append(z)
                answer = z.text
                layer_used = "degraded-zai"
            else:
                engines.extend([m, z])
                try:
                    fused, judge = await hybrid_judge(task, m, z)
                    answer = fused
                except Exception as exc:
                    # Judge failed with both answers intact: deterministic
                    # tiebreak to the non-judge engine's answer.
                    degradations.append(
                        f"judge failed ({exc}); deterministic tiebreak to the "
                        "non-judge engine (glm-5.3)"
                    )
                    judge = JudgeReceipt(
                        used=False,
                        model=task.judge_model,
                        verdict="judge-failed",
                        notes=str(exc)[:300],
                    )
                    answer = z.text

        total = round(
            sum(r.cost_usd_est for r in engines) + (judge.cost_usd_est or 0.0),
            6,
        )
        return TwinFlameOSOutput(
            answer=answer,
            layer_used=layer_used,
            director=director,
            engines=engines,
            judge=judge,
            degradations=degradations,
            total_cost_usd_est=total,
        )
