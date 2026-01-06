## Disable parallel calls

:::python
For supported providers, you can disable parallel tool calling by setting `parallel_tool_calls=False` via the `model.bind_tools()` method:

```python
model.bind_tools(
    tools,
    # highlight-next-line
    parallel_tool_calls=False
)
```

:::

:::js
For supported providers, you can disable parallel tool calling by setting `parallel_tool_calls: false` via the `model.bindTools()` method:

```typescript
model.bindTools(
  tools,
  // highlight-next-line
  { parallel_tool_calls: false }
);
```

:::

??? example "Extended example: disable parallel tool calls in a prebuilt agent"

    :::python
    ```python
    from langchain.chat_models import init_chat_model

    def add(a: int, b: int) -> int:
        """Add two numbers"""
        return a + b

    def multiply(a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b

    model = init_chat_model("anthropic:claude-3-5-sonnet-latest", temperature=0)
    tools = [add, multiply]
    agent = create_react_agent(
        # disable parallel tool calls
        # highlight-next-line
        model=model.bind_tools(tools, parallel_tool_calls=False),
        tools=tools
    )

    agent.invoke(
        {"messages": [{"role": "user", "content": "what's 3 + 5 and 4 * 7?"}]}
    )
    ```
    :::

    :::js
    ```typescript
    import { ChatOpenAI } from "@langchain/openai";
    import { tool } from "@langchain/core/tools";
    import { z } from "zod";
    import { createReactAgent } from "@langchain/langgraph/prebuilt";

    const add = tool(
      (input) => {
        return input.a + input.b;
      },
      {
        name: "add",
        description: "Add two numbers",
        schema: z.object({
          a: z.number(),
          b: z.number(),
        }),
      }
    );

    const multiply = tool(
      (input) => {
        return input.a * input.b;
      },
      {
        name: "multiply",
        description: "Multiply two numbers.",
        schema: z.object({
          a: z.number(),
          b: z.number(),
        }),
      }
    );

    const model = new ChatOpenAI({ model: "gpt-4o", temperature: 0 });
    const tools = [add, multiply];

    const agent = createReactAgent({
      // disable parallel tool calls
      // highlight-next-line
      llm: model.bindTools(tools, { parallel_tool_calls: false }),
      tools: tools
    });

    await agent.invoke({
      messages: [{ role: "user", content: "what's 3 + 5 and 4 * 7?" }]
    });
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`multiply`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6341) (function in langgraph)
- [`bind_tools`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/react_agent.py#L19) (function in langgraph)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`set`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L84) (function in checkpoint)
