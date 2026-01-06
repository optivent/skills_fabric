## highlight-next-line

@tool(return_direct=True)
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
```

:::

:::js
Use `returnDirect: true` to immediately return a tool's result without executing additional logic.

This is useful for tools that should not trigger further processing or tool calls, allowing you to return results directly to the user.

```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";

// highlight-next-line
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
    // highlight-next-line
    returnDirect: true,
  }
);
```

:::

??? example "Extended example: Using return_direct in a prebuilt agent"

    :::python
    ```python
    from langchain_core.tools import tool
    from langgraph.prebuilt import create_react_agent

    # highlight-next-line
    @tool(return_direct=True)
    def add(a: int, b: int) -> int:
        """Add two numbers"""
        return a + b

    agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=[add]
    )

    agent.invoke(
        {"messages": [{"role": "user", "content": "what's 3 + 5?"}]}
    )
    ```
    :::

    :::js
    ```typescript
    import { tool } from "@langchain/core/tools";
    import { z } from "zod";
    import { createReactAgent } from "@langchain/langgraph/prebuilt";
    import { ChatAnthropic } from "@langchain/anthropic";

    // highlight-next-line
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
        // highlight-next-line
        returnDirect: true,
      }
    );

    const agent = createReactAgent({
      llm: new ChatAnthropic({ model: "claude-3-5-sonnet-20240620" }),
      tools: [add]
    });

    await agent.invoke({
      messages: [{ role: "user", content: "what's 3 + 5?" }]
    });
    ```
    :::

!!! important "Using without prebuilt components"

    :::python
    If you are building a custom workflow and are not relying on `create_react_agent` or `ToolNode`, you will also
    need to implement the control flow to handle `return_direct=True`.
    :::

    :::js
    If you are building a custom workflow and are not relying on `createReactAgent` or `ToolNode`, you will also
    need to implement the control flow to handle `returnDirect: true`.
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`ToolNode`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L610) (class in prebuilt)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
