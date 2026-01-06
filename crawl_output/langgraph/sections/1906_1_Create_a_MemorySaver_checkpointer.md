## 1. Create a `MemorySaver` checkpointer

Create a `MemorySaver` checkpointer:

:::python

```python
from langgraph.checkpoint.memory import InMemorySaver

memory = InMemorySaver()
```

:::

:::js

```typescript
import { MemorySaver } from "@langchain/langgraph";

const memory = new MemorySaver();
```

:::

This is in-memory checkpointer, which is convenient for the tutorial. However, in a production application, you would likely change this to use `SqliteSaver` or `PostgresSaver` and connect a database.

### Source References

- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`SqliteSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/__init__.py#L38) (class in checkpoint-sqlite)
- [`conn`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/conftest.py#L15) (function in checkpoint-postgres)
- [`PostgresSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/__init__.py#L32) (class in checkpoint-postgres)
- [`InMemorySaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L31) (class in checkpoint)
- [`checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L124) (function in langgraph)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
