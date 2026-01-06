## 3. Replay the full state history

Now that you have added steps to the chatbot, you can `replay` the full state history to see everything that occurred.

:::python

```python
to_replay = None
for state in graph.get_state_history(config):
    print("Num Messages: ", len(state.values["messages"]), "Next: ", state.next)
    print("-" * 80)
    if len(state.values["messages"]) == 6:
        # We are somewhat arbitrarily selecting a specific state based on the number of chat messages in the state.
        to_replay = state
```

```
Num Messages:  8 Next:  ()
--------------------------------------------------------------------------------
Num Messages:  7 Next:  ('chatbot',)
--------------------------------------------------------------------------------
Num Messages:  6 Next:  ('tools',)
--------------------------------------------------------------------------------
Num Messages:  5 Next:  ('chatbot',)
--------------------------------------------------------------------------------
Num Messages:  4 Next:  ('__start__',)
--------------------------------------------------------------------------------
Num Messages:  4 Next:  ()
--------------------------------------------------------------------------------
Num Messages:  3 Next:  ('chatbot',)
--------------------------------------------------------------------------------
Num Messages:  2 Next:  ('tools',)
--------------------------------------------------------------------------------
Num Messages:  1 Next:  ('chatbot',)
--------------------------------------------------------------------------------
Num Messages:  0 Next:  ('__start__',)
--------------------------------------------------------------------------------
```

:::

:::js

```typescript
import type { StateSnapshot } from "@langchain/langgraph";

let toReplay: StateSnapshot | undefined;
for await (const state of graph.getStateHistory({
  configurable: { thread_id: threadId },
})) {
  console.log(
    `Num Messages: ${state.values.messages.length}, Next: ${JSON.stringify(
      state.next
    )}`
  );
  console.log("-".repeat(80));
  if (state.values.messages.length === 6) {
    // We are somewhat arbitrarily selecting a specific state based on the number of chat messages in the state.
    toReplay = state;
  }
}
```

```
Num Messages: 8 Next:  []
--------------------------------------------------------------------------------
Num Messages: 7 Next:  ["chatbot"]
--------------------------------------------------------------------------------
Num Messages: 6 Next:  ["tools"]
--------------------------------------------------------------------------------
Num Messages: 7, Next: ["chatbot"]
--------------------------------------------------------------------------------
Num Messages: 6, Next: ["tools"]
--------------------------------------------------------------------------------
Num Messages: 5, Next: ["chatbot"]
--------------------------------------------------------------------------------
Num Messages: 4, Next: ["__start__"]
--------------------------------------------------------------------------------
Num Messages: 4, Next: []
--------------------------------------------------------------------------------
Num Messages: 3, Next: ["chatbot"]
--------------------------------------------------------------------------------
Num Messages: 2, Next: ["tools"]
--------------------------------------------------------------------------------
Num Messages: 1, Next: ["chatbot"]
--------------------------------------------------------------------------------
Num Messages: 0, Next: ["__start__"]
--------------------------------------------------------------------------------
```

:::

Checkpoints are saved for every step of the graph. This **spans invocations** so you can rewind across a full thread's history.

### Source References

- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`get_state`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L1235) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
