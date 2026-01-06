## highlight-next-line

input_message = {"role": "user", "content": "Hi"}

result = graph.invoke({"messages": [input_message]})

for message in result["messages"]:
    message.pretty_print()
```

```
================================ Human Message ================================

Hi
================================== Ai Message ==================================

Hello!
```

This is a versatile representation of state for applications involving [chat models](https://python.langchain.com/docs/concepts/chat_models/). LangGraph includes a pre-built `MessagesState` for convenience, so that we can have:

```python
from langgraph.graph import MessagesState

class State(MessagesState):
    extra_field: int
```
:::

:::js
LangGraph includes a built-in `MessagesZodState` that handles these considerations:

```typescript
import { MessagesZodState } from "@langchain/langgraph";

const State = z.object({
  // highlight-next-line
  messages: MessagesZodState.shape.messages,
  extraField: z.number(),
});

const graph = new StateGraph(State)
  .addNode("node", (state) => {
    const newMessage = new AIMessage("Hello!");
    return { messages: [newMessage], extraField: 10 };
  })
  .addEdge(START, "node")
  .compile();
```

```typescript
// highlight-next-line
const inputMessage = { role: "user", content: "Hi" };

const result = await graph.invoke({ messages: [inputMessage] });

for (const message of result.messages) {
  console.log(`${message.getType()}: ${message.content}`);
}
```

```
human: Hi
ai: Hello!
```

This is a versatile representation of state for applications involving [chat models](https://js.langchain.com/docs/concepts/chat_models/). LangGraph includes this pre-built `MessagesZodState` for convenience, so that we can have:

```typescript
import { MessagesZodState } from "@langchain/langgraph";

const State = MessagesZodState.extend({
  extraField: z.number(),
});
```
:::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`new`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L779) (function in cli)
- [`Cat`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel_async.py#L4123) (class in langgraph)
