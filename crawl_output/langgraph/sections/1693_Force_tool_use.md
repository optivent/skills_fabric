## Force tool use

If you need to force a specific tool to be used, you will need to configure this at the **model** level using the `tool_choice` parameter in the bind_tools method.

Force specific tool usage via tool_choice:

:::python

```python
@tool(return_direct=True)
def greet(user_name: str) -> int:
    """Greet user."""
    return f"Hello {user_name}!"

tools = [greet]

configured_model = model.bind_tools(
    tools,
    # Force the use of the 'greet' tool
    # highlight-next-line
    tool_choice={"type": "tool", "name": "greet"}
)
```

:::

:::js

```typescript
const greet = tool(
  (input) => {
    return `Hello ${input.userName}!`;
  },
  {
    name: "greet",
    description: "Greet user.",
    schema: z.object({
      userName: z.string(),
    }),
    returnDirect: true,
  }
);

const tools = [greet];

const configuredModel = model.bindTools(
  tools,
  // Force the use of the 'greet' tool
  // highlight-next-line
  { tool_choice: { type: "tool", name: "greet" } }
);
```

:::

??? example "Extended example: Force tool usage in an agent"

    :::python
    To force the agent to use specific tools, you can set the `tool_choice` option in `model.bind_tools()`:

    ```python
    from langchain_core.tools import tool

    # highlight-next-line
    @tool(return_direct=True)
    def greet(user_name: str) -> int:
        """Greet user."""
        return f"Hello {user_name}!"

    tools = [greet]

    agent = create_react_agent(
        # highlight-next-line
        model=model.bind_tools(tools, tool_choice={"type": "tool", "name": "greet"}),
        tools=tools
    )

    agent.invoke(
        {"messages": [{"role": "user", "content": "Hi, I am Bob"}]}
    )
    ```
    :::

    :::js
    To force the agent to use specific tools, you can set the `tool_choice` option in `model.bindTools()`:

    ```typescript
    import { tool } from "@langchain/core/tools";
    import { z } from "zod";
    import { createReactAgent } from "@langchain/langgraph/prebuilt";
    import { ChatOpenAI } from "@langchain/openai";

    // highlight-next-line
    const greet = tool(
      (input) => {
        return `Hello ${input.userName}!`;
      },
      {
        name: "greet",
        description: "Greet user.",
        schema: z.object({
          userName: z.string(),
        }),
        // highlight-next-line
        returnDirect: true,
      }
    );

    const tools = [greet];
    const model = new ChatOpenAI({ model: "gpt-4o" });

    const agent = createReactAgent({
      // highlight-next-line
      llm: model.bindTools(tools, { tool_choice: { type: "tool", name: "greet" } }),
      tools: tools
    });

    await agent.invoke({
      messages: [{ role: "user", content: "Hi, I am Bob" }]
    });
    ```
    :::

!!! Warning "Avoid infinite loops"

    :::python
    Forcing tool usage without stopping conditions can create infinite loops. Use one of the following safeguards:

    - Mark the tool with [`return_direct=True`](#immediate-return) to end the loop after execution.
    - Set [`recursion_limit`](../concepts/low_level.md#recursion-limit) to restrict the number of execution steps.
    :::

    :::js
    Forcing tool usage without stopping conditions can create infinite loops. Use one of the following safeguards:

    - Mark the tool with [`returnDirect: true`](#immediate-return) to end the loop after execution.
    - Set [`recursionLimit`](../concepts/low_level.md#recursion-limit) to restrict the number of execution steps.
    :::

!!! tip "Tool choice configuration"

    The `tool_choice` parameter is used to configure which tool should be used by the model when it decides to call a tool. This is useful when you want to ensure that a specific tool is always called for a particular task or when you want to override the model's default behavior of choosing a tool based on its internal logic.

    Note that not all models support this feature, and the exact configuration may vary depending on the model you are using.

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`bind_tools`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/react_agent.py#L19) (function in langgraph)
- [`override`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/runtime.py#L117) (function in langgraph)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
