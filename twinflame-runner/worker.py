"""TwinFlame Mistral runner — a Mistral Workflow that runs one prompt
through a Mistral model using the deployment's service account.

Built for TwinFlame, the Mistral Large 4 x GLM-5.3 fusion router.
No API key: the managed deployment injects a rotating service-account
token the Workflows SDK reads automatically.
"""

import asyncio

import mistralai.workflows as workflows
from mistralai import Mistral


async def main() -> None:
    client = Mistral()  # auth resolved from MISTRAL_SA_TOKEN_PATH (managed) or MISTRAL_API_KEY (local)
    workflow_classes = workflows.discover_all_workflows_in_package("app.workflows")
    await client.run_worker(workflow_classes)


if __name__ == "__main__":
    asyncio.run(main())
