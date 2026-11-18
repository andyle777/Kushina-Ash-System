"""TwinFlame Mistral runner workflow: one prompt in, one model answer out.

The activity calls the Mistral API through get_mistral_client(), which on a
managed deployment carries the service-account token, collects telemetry,
and injects observability metadata.
"""

from pydantic import BaseModel

import mistralai.workflows as workflows
from mistralai.workflows import Depends
from mistralai.workflows.client import get_mistral_client


class TwinFlameInput(BaseModel):
    prompt: str
    system: str | None = None
    model: str = "mistral-large-4"
    max_tokens: int = 2048
    temperature: float = 0.3


class TwinFlameOutput(BaseModel):
    model: str
    text: str
    thinking: str = ""
    tokens_in: int
    tokens_out: int


def _flatten(value) -> str:
    """Recursively flatten message content that may be a plain string, an
    object with a .text attribute, or a list of such objects. Mistral
    Large 4 is a reasoning model: message.content arrives as a list of
    ThinkChunk/TextChunk objects, not a string."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, (list, tuple)):
        return "".join(_flatten(v) for v in value)
    text = getattr(value, "text", None)
    if isinstance(text, str):
        return text
    for attr in ("thinking", "content"):
        inner = getattr(value, attr, None)
        if inner is not None:
            return _flatten(inner)
    return ""


@workflows.activity()
async def complete(
    task: TwinFlameInput,
    client=Depends(get_mistral_client),
) -> TwinFlameOutput:
    """One chat completion against the chosen Mistral model."""
    messages = []
    if task.system:
        messages.append({"role": "system", "content": task.system})
    messages.append({"role": "user", "content": task.prompt})

    response = await client.chat.complete_async(
        model=task.model,
        messages=messages,
        max_tokens=task.max_tokens,
        temperature=task.temperature,
    )

    usage = response.usage
    raw = response.choices[0].message.content if response.choices else None
    answer, reasoning = "", ""
    if isinstance(raw, list):
        for chunk in raw:
            body = _flatten(chunk)
            if str(getattr(chunk, "type", "") or "") == "thinking" or hasattr(chunk, "thinking"):
                reasoning += body
            else:
                answer += body
    else:
        answer = _flatten(raw)
    if not answer.strip():
        # Last-resort guard: never return an empty answer if the model said
        # anything at all, so a retry never burns tokens on a parse issue.
        answer = _flatten(raw)
    return TwinFlameOutput(
        model=response.model,
        text=answer,
        thinking=reasoning,
        tokens_in=(usage.prompt_tokens or 0) if usage else 0,
        tokens_out=(usage.completion_tokens or 0) if usage else 0,
    )


@workflows.workflow.define(
    name="twinflame-mistral",
    workflow_display_name="TwinFlame Mistral Runner",
    workflow_description=(
        "Runs a single prompt through a Mistral model (default Mistral Large 4) "
        "via the deployment service account. The Mistral side of the TwinFlame "
        "Mistral x GLM fusion router."
    ),
)
class TwinFlameMistralWorkflow:
    @workflows.workflow.entrypoint
    async def run(self, task: TwinFlameInput) -> TwinFlameOutput:
        return await complete(task)
