## `LANGGRAPH_POSTGRES_POOL_MAX_SIZE`

Beginning with langgraph-api version `0.2.12`, the maximum size of the Postgres connection pool (per replica) can be controlled using the `LANGGRAPH_POSTGRES_POOL_MAX_SIZE` environment variable. By setting this variable, you can determine the upper bound on the number of simultaneous connections the server will establish with the Postgres database.

For example, if a deployment is scaled up to 10 replicas and `LANGGRAPH_POSTGRES_POOL_MAX_SIZE` is configured to `150`, then up to `1500` connections to Postgres can be established. This is particularly useful for deployments where database resources are limited (or more available) or where you need to tune connection behavior for performance or scaling reasons.

Defaults to `150` connections.

### Source References

- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`set`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L84) (function in checkpoint)
- [`conn`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/conftest.py#L15) (function in checkpoint-postgres)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`up`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L3118) (function in langgraph)
- [`Version`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/docker.py#L16) (class in cli)
- [`a`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4642) (function in langgraph)
