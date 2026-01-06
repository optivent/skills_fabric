## Create New Deployment

Starting from the <a href="https://smith.langchain.com/" target="_blank">LangSmith UI</a>...

1. In the left-hand navigation panel, select `LangGraph Platform`. The `LangGraph Platform` view contains a list of existing LangGraph Platform deployments.
1. In the top-right corner, select `+ New Deployment` to create a new deployment.
1. In the `Create New Deployment` panel, fill out the required fields.
    1. `Deployment details`
        1. Select `Import from GitHub` and follow the GitHub OAuth workflow to install and authorize LangChain's `hosted-langserve` GitHub app to access the selected repositories. After installation is complete, return to the `Create New Deployment` panel and select the GitHub repository to deploy from the dropdown menu. **Note**: The GitHub user installing LangChain's `hosted-langserve` GitHub app must be an [owner](https://docs.github.com/en/organizations/managing-peoples-access-to-your-organization-with-roles/roles-in-an-organization#organization-owners) of the organization or account.
        1. Specify a name for the deployment.
        1. Specify the desired `Git Branch`. A deployment is linked to a branch. When a new revision is created, code for the linked branch will be deployed. The branch can be updated later in the [Deployment Settings](#deployment-settings).
        1. Specify the full path to the [LangGraph API config file](../reference/cli.md#configuration-file) including the file name. For example, if the file `langgraph.json` is in the root of the repository, simply specify `langgraph.json`.
        1. Check/uncheck checkbox to `Automatically update deployment on push to branch`. If checked, the deployment will automatically be updated when changes are pushed to the specified `Git Branch`. This setting can be enabled/disabled later in the [Deployment Settings](#deployment-settings).
    1. Select the desired `Deployment Type`.
        1. `Development` deployments are meant for non-production use cases and are provisioned with minimal resources.
        1. `Production` deployments can serve up to 500 requests/second and are provisioned with highly available storage with automatic backups.
    1. Determine if the deployment should be `Shareable through LangGraph Studio`.
        1. If unchecked, the deployment will only be accessible with a valid LangSmith API key for the workspace.
        1. If checked, the deployment will be accessible through LangGraph Studio to any LangSmith user. A direct URL to LangGraph Studio for the deployment will be provided to share with other LangSmith users.
    1. Specify `Environment Variables` and secrets. See the [Environment Variables reference](../reference/env_var.md) to configure additional variables for the deployment.
        1. Sensitive values such as API keys (e.g. `OPENAI_API_KEY`) should be specified as secrets.
        1. Additional non-secret environment variables can be specified as well.
    1. A new LangSmith `Tracing Project` is automatically created with the same name as the deployment.
1. In the top-right corner, select `Submit`. After a few seconds, the `Deployment` view appears and the new deployment will be queued for provisioning.

### Source References

- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`count`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L6530) (function in sdk-py)
- [`list`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L174) (function in checkpoint)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
