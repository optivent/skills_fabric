## highlight-next-line

agent = create_react_agent(
    model="anthropic:claude-3-7-sonnet",
    tools=[multiply]
)
agent.invoke({"messages": [{"role": "user", "content": "what's 42 x 7?"}]})
```

:::

:::js
To create a tool-calling agent, you can use the prebuilt [createReactAgent](https://js.langchain.com/docs/api/langgraph_prebuilt/functions/createReactAgent.html):

```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";
// highlight-next-line
import { createReactAgent } from "@langchain/langgraph/prebuilt";

const multiply = tool(
  (input) => {
    return input.a * input.b;
  },
  {
    name: "multiply",
    description: "Multiply two numbers.",
    schema: z.object({
      a: z.number().describe("First operand"),
      b: z.number().describe("Second operand"),
    }),
  }
);

// highlight-next-line
const agent = createReactAgent({
  llm: new ChatAnthropic({ model: "claude-3-5-sonnet-20240620" }),
  tools: [multiply],
});

await agent.invoke({
  messages: [{ role: "user", content: "what's 42 x 7?" }],
});
```

:::

:::python

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`multiply`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6341) (function in langgraph)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`new`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L779) (function in cli)
- [`func`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_utils.py#L37) (function in langgraph)
