## Checkpointer libraries

Under the hood, checkpointing is powered by checkpointer objects that conform to @[BaseCheckpointSaver] interface. LangGraph provides several checkpointer implementations, all implemented via standalone, installable libraries:

:::python

- `langgraph-checkpoint`: The base interface for checkpointer savers (@[BaseCheckpointSaver]) and serialization/deserialization interface (@[SerializerProtocol][SerializerProtocol]). Includes in-memory checkpointer implementation (@[InMemorySaver][InMemorySaver]) for experimentation. LangGraph comes with `langgraph-checkpoint` included.
- `langgraph-checkpoint-sqlite`: An implementation of LangGraph checkpointer that uses SQLite database (@[SqliteSaver][SqliteSaver] / @[AsyncSqliteSaver]). Ideal for experimentation and local workflows. Needs to be installed separately.
- `langgraph-checkpoint-postgres`: An advanced checkpointer that uses Postgres database (@[PostgresSaver][PostgresSaver] / @[AsyncPostgresSaver]), used in LangGraph Platform. Ideal for using in production. Needs to be installed separately.

:::

:::js

- `@langchain/langgraph-checkpoint`: The base interface for checkpointer savers (@[BaseCheckpointSaver][BaseCheckpointSaver]) and serialization/deserialization interface (@[SerializerProtocol][SerializerProtocol]). Includes in-memory checkpointer implementation (@[MemorySaver]) for experimentation. LangGraph comes with `@langchain/langgraph-checkpoint` included.
- `@langchain/langgraph-checkpoint-sqlite`: An implementation of LangGraph checkpointer that uses SQLite database (@[SqliteSaver]). Ideal for experimentation and local workflows. Needs to be installed separately.
- `@langchain/langgraph-checkpoint-postgres`: An advanced checkpointer that uses Postgres database (@[PostgresSaver]), used in LangGraph Platform. Ideal for using in production. Needs to be installed separately.

:::

### Source References

- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`AsyncSqliteSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/aio.py#L30) (class in checkpoint-sqlite)
- [`SqliteSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/__init__.py#L38) (class in checkpoint-sqlite)
- [`AsyncPostgresSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/aio.py#L32) (class in checkpoint-postgres)
- [`PostgresSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/__init__.py#L32) (class in checkpoint-postgres)
- [`InMemorySaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L31) (class in checkpoint)
- [`sync`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L556) (function in checkpoint)
- [`BaseCheckpointSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L116) (class in checkpoint)
