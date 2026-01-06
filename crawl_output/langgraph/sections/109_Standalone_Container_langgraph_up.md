## Standalone Container (`langgraph up`)

`langgraph up` builds your local package into a Docker image and runs the server as a [standalone container](../../concepts/deployment_options.md#standalone-container) consisting of three containers: the API server, a PostgreSQL container, and a Redis container. All persistent data (checkpoints, assistants, etc.) are stored in the PostgreSQL database. Redis is used as a pubsub connection for real-time streaming of events. You can encrypt all checkpoints before saving to the database by setting a valid `LANGGRAPH_AES_KEY` environment variable. You can also specify [TTLs](../../how-tos/ttl/configure_ttl.md) for checkpoints and cross-thread memories in `langgraph.json` to control how long data is stored. All persisted threads, memories, and other data can be deleted via the relevant API endpoints.

Additional API calls are made to confirm that the server has a valid license and to track the number of executed runs and tasks. Periodically, the API server validates the provided license key (or API key).

If you've disabled [tracing](#langsmith-tracing), no user data is persisted externally unless your graph code explicitly contacts an external service.

### Source References

- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`execute`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1174) (function in prebuilt)
- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`delete`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L929) (function in checkpoint)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`Assistant`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L242) (class in sdk-py)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
