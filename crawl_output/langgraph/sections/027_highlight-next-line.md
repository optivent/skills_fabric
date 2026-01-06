## highlight-next-line

config = {"configurable": {"thread_id": "1"}}
sf_response = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
    # highlight-next-line
    config  # (2)!
)
ny_response = agent.invoke(
    {"messages": [{"role": "user", "content": "what about new york?"}]},
    # highlight-next-line
    config
)
```

1. `checkpointer` allows the agent to store its state at every step in the tool calling loop. This enables [short-term memory](../how-tos/memory/add-memory.md#add-short-term-memory) and [human-in-the-loop](../concepts/human_in_the_loop.md) capabilities.
2. Pass configuration with `thread_id` to be able to resume the same conversation on future agent invocations.
   :::

:::js

```typescript
import { createReactAgent } from "@langchain/langgraph/prebuilt";
import { MemorySaver } from "@langchain/langgraph";

// highlight-next-line
const checkpointer = new MemorySaver();

const agent = createReactAgent({
  llm: "anthropic:claude-3-5-sonnet-latest",
  tools: [getWeather],
  // highlight-next-line
  checkpointSaver: checkpointer, // (1)!
});

// Run the agent
// highlight-next-line
const config = { configurable: { thread_id: "1" } };
const sfResponse = await agent.invoke(
  { messages: [{ role: "user", content: "what is the weather in sf" }] },
  // highlight-next-line
  config // (2)!
);
const nyResponse = await agent.invoke(
  { messages: [{ role: "user", content: "what about new york?" }] },
  // highlight-next-line
  config
);
```

1. `checkpointSaver` allows the agent to store its state at every step in the tool calling loop. This enables [short-term memory](../how-tos/memory/add-memory.md#add-short-term-memory) and [human-in-the-loop](../concepts/human_in_the_loop.md) capabilities.
2. Pass configuration with `thread_id` to be able to resume the same conversation on future agent invocations.
   :::

:::python
When you enable the checkpointer, it stores agent state at every step in the provided checkpointer database (or in memory, if using `InMemorySaver`).
:::

:::js
When you enable the checkpointer, it stores agent state at every step in the provided checkpointer database (or in memory, if using `MemorySaver`).
:::

Note that in the above example, when the agent is invoked the second time with the same `thread_id`, the original message history from the first conversation is automatically included, together with the new user input.

For more information, see [Memory](../how-tos/memory/add-memory.md).

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
