## Initializing the graph

:::python

When initializing a `RemoteGraph`, you must always specify:

- `name`: the name of the graph you want to interact with. This is the same graph name you use in `langgraph.json` configuration file for your deployment.
- `api_key`: a valid LangSmith API key. Can be set as an environment variable (`LANGSMITH_API_KEY`) or passed directly via the `api_key` argument. The API key could also be provided via the `client` / `sync_client` arguments, if `LangGraphClient` / `SyncLangGraphClient` were initialized with `api_key` argument.

Additionally, you have to provide one of the following:

- `url`: URL of the deployment you want to interact with. If you pass `url` argument, both sync and async clients will be created using the provided URL, headers (if provided) and default configuration values (e.g. timeout, etc).
- `client`: a `LangGraphClient` instance for interacting with the deployment asynchronously (e.g. using `.astream()`, `.ainvoke()`, `.aget_state()`, `.aupdate_state()`, etc.)
- `sync_client`: a `SyncLangGraphClient` instance for interacting with the deployment synchronously (e.g. using `.stream()`, `.invoke()`, `.get_state()`, `.update_state()`, etc.)

!!! Note

    If you pass both `client` or `sync_client` as well as `url` argument, they will take precedence over the `url` argument. If none of the `client` / `sync_client` / `url` arguments are provided, `RemoteGraph` will raise a `ValueError` at runtime.

:::

:::js

When initializing a `RemoteGraph`, you must always specify:

- `name`: the name of the graph you want to interact with. This is the same graph name you use in `langgraph.json` configuration file for your deployment.
- `apiKey`: a valid LangSmith API key. Can be set as an environment variable (`LANGSMITH_API_KEY`) or passed directly via the `apiKey` argument. The API key could also be provided via the `client`if `LangGraphClient` were initialized with `apiKey` argument.

Additionally, you have to provide one of the following:

- `url`: URL of the deployment you want to interact with. If you pass `url` argument, both sync and async clients will be created using the provided URL, headers (if provided) and default configuration values (e.g. timeout, etc).
- `client`: a `LangGraphClient` instance for interacting with the deployment asynchronously

:::

### Source References

- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`LangGraphClient`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L291) (class in sdk-py)
- [`SyncLangGraphClient`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3637) (class in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
