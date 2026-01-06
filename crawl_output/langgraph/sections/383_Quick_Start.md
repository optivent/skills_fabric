## Quick Start

1. Call `POST /v2/deployments` to create a new Deployment. The response body contains the Deployment ID (`id`) and the ID of the latest (and first) revision (`latest_revision_id`).
1. Call `GET /v2/deployments/{deployment_id}` to retrieve the Deployment. Set `deployment_id` in the URL to the value of Deployment ID (`id`).
1. Poll for revision `status` until `status` is `DEPLOYED` by calling `GET /v2/deployments/{deployment_id}/revisions/{latest_revision_id}`.
1. Call `PATCH /v2/deployments/{deployment_id}` to update the deployment.

### Source References

- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`patch`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3753) (function in sdk-py)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`set`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L84) (function in checkpoint)
- [`retrieve`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/graphs/storm.py#L470) (function in cli)
- [`up`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L3118) (function in langgraph)
- [`new`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L779) (function in cli)
