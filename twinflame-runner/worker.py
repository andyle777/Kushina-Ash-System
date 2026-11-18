"""TwinFlame Mistral runner — worker entrypoint.

Discovers the TwinFlame workflows and hands them to run_worker. Auth is
resolved automatically: MISTRAL_SA_TOKEN_PATH on managed deployments,
MISTRAL_API_KEY locally.
"""

import asyncio

import mistralai.workflows as workflows


async def main() -> None:
    workflow_classes = workflows.discover_all_workflows_in_package("app.workflows")
    await workflows.run_worker(workflow_classes)


if __name__ == "__main__":
    asyncio.run(main())
