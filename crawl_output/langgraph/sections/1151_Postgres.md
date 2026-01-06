## Postgres

Postgres is the persistence layer for all user, run, and long-term memory data in a LangGraph Server. This stores both checkpoints (see more info [here](./persistence.md)), server resources (threads, runs, assistants and crons), as well as items saved in the long-term memory store (see more info [here](./persistence.md#memory-store)).

### Source References

- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`Assistant`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L242) (class in sdk-py)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`Cron`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L348) (class in sdk-py)
- [`Item`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L51) (class in checkpoint)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`threads`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L961) (class in sdk-py)
