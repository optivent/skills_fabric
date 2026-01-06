## Default error handling (enabled by default)

tool_node = ToolNode([multiply])

message = AIMessage(
    content="",
    tool_calls=[{
        "name": "multiply",
        "args": {"a": 42, "b": 7},
        "id": "tool_call_id",
        "type": "tool_call"
    }]
)

result = tool_node.invoke({"messages": [message]})
```

Output:

```pycon
{'messages': [
    ToolMessage(
        content="Error: ValueError('The ultimate error')\n Please fix your mistakes.",
        name='multiply',
        tool_call_id='tool_call_id',
        status='error'
    )
]}
```

:::

:::js
LangGraph provides built-in error handling for tool execution through the prebuilt [ToolNode](https://js.langchain.com/docs/api/langgraph_prebuilt/classes/ToolNode.html) component, used both independently and in prebuilt agents.

By **default**, `ToolNode` catches exceptions raised during tool execution and returns them as `ToolMessage` objects with a status indicating an error.

```typescript
import { AIMessage } from "@langchain/core/messages";
import { ToolNode } from "@langchain/langgraph/prebuilt";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const multiply = tool(
  (input) => {
    if (input.a === 42) {
      throw new Error("The ultimate error");
    }
    return input.a * input.b;
  },
  {
    name: "multiply",
    description: "Multiply two numbers",
    schema: z.object({
      a: z.number(),
      b: z.number(),
    }),
  }
);

// Default error handling (enabled by default)
const toolNode = new ToolNode([multiply]);

const message = new AIMessage({
  content: "",
  tool_calls: [
    {
      name: "multiply",
      args: { a: 42, b: 7 },
      id: "tool_call_id",
      type: "tool_call",
    },
  ],
});

const result = await toolNode.invoke({ messages: [message] });
```

Output:

```
{ messages: [
  ToolMessage {
    content: "Error: The ultimate error\n Please fix your mistakes.",
    name: "multiply",
    tool_call_id: "tool_call_id",
    status: "error"
  }
]}
```

:::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`multiply`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6341) (function in langgraph)
- [`ToolNode`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L610) (class in prebuilt)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`Row`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L1163) (class in checkpoint-postgres)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`new`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L779) (function in cli)
