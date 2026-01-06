## Create New Revision

When [creating a new deployment](#create-new-deployment), a new revision is created by default. Subsequent revisions can be created to deploy new code changes.

Starting from the <a href="https://smith.langchain.com/" target="_blank">LangSmith UI</a>...

1. In the left-hand navigation panel, select `LangGraph Platform`. The `LangGraph Platform` view contains a list of existing LangGraph Platform deployments.
1. Select an existing deployment to create a new revision for.
1. In the `Deployment` view, in the top-right corner, select `+ New Revision`.
1. In the `New Revision` modal, fill out the required fields.
    1. Specify the full path to the [LangGraph API config file](../reference/cli.md#configuration-file) including the file name. For example, if the file `langgraph.json` is in the root of the repository, simply specify `langgraph.json`.
    1. Determine if the deployment should be `Shareable through LangGraph Studio`.
        1. If unchecked, the deployment will only be accessible with a valid LangSmith API key for the workspace.
        1. If checked, the deployment will be accessible through LangGraph Studio to any LangSmith user. A direct URL to LangGraph Studio for the deployment will be provided to share with other LangSmith users.
    1. Specify `Environment Variables` and secrets. Existing secrets and environment variables are prepopulated. See the [Environment Variables reference](../reference/env_var.md) to configure additional variables for the revision.
        1. Add new secrets or environment variables.
        1. Remove existing secrets or environment variables.
        1. Update the value of existing secrets or environment variables.
1. Select `Submit`. After a few seconds, the `New Revision` modal will close and the new revision will be queued for deployment.

### Source References

- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`close`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L573) (function in checkpoint)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`list`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L174) (function in checkpoint)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`json`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L173) (function in sdk-py)
