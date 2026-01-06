## Invocation example with an agent

agent.invoke(
    {"messages": [{"role": "user", "content": "look up user info"}]},
    # highlight-next-line
    config={"configurable": {"user_id": "user_123"}}
)
```

:::

:::js
Use configuration when you have **immutable** runtime data that tools require, such as user identifiers. You pass these arguments via [`LangGraphRunnableConfig`](https://js.langchain.com/docs/api/langgraph/interfaces/LangGraphRunnableConfig.html) at invocation and access them in the tool:

```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";
import type { LangGraphRunnableConfig } from "@langchain/langgraph";

const getUserInfo = tool(
  // highlight-next-line
  async (_, config: LangGraphRunnableConfig) => {
    const userId = config?.configurable?.user_id;
    return userId === "user_123" ? "User is John Smith" : "Unknown user";
  },
  {
    name: "get_user_info",
    description: "Retrieve user information based on user ID.",
    schema: z.object({}),
  }
);

// Invocation example with an agent
await agent.invoke(
  { messages: [{ role: "user", content: "look up user info" }] },
  // highlight-next-line
  { configurable: { user_id: "user_123" } }
);
```

:::

??? example "Extended example: Access config in tools"

    :::python
    ```python
    from langchain_core.runnables import RunnableConfig
    from langchain_core.tools import tool
    from langgraph.prebuilt import create_react_agent

    def get_user_info(
        # highlight-next-line
        config: RunnableConfig,
    ) -> str:
        """Look up user info."""
        # highlight-next-line
        user_id = config["configurable"].get("user_id")
        return "User is John Smith" if user_id == "user_123" else "Unknown user"

    agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=[get_user_info],
    )

    agent.invoke(
        {"messages": [{"role": "user", "content": "look up user information"}]},
        # highlight-next-line
        config={"configurable": {"user_id": "user_123"}}
    )
    ```
    :::

    :::js
    ```typescript
    import { tool } from "@langchain/core/tools";
    import { z } from "zod";
    import { createReactAgent } from "@langchain/langgraph/prebuilt";
    import type { LangGraphRunnableConfig } from "@langchain/langgraph";
    import { ChatAnthropic } from "@langchain/anthropic";

    const getUserInfo = tool(
      // highlight-next-line
      async (_, config: LangGraphRunnableConfig) => {
        // highlight-next-line
        const userId = config?.configurable?.user_id;
        return userId === "user_123" ? "User is John Smith" : "Unknown user";
      },
      {
        name: "get_user_info",
        description: "Look up user info.",
        schema: z.object({}),
      }
    );

    const agent = createReactAgent({
      llm: new ChatAnthropic({ model: "claude-3-5-sonnet-20240620" }),
      tools: [getUserInfo],
    });

    await agent.invoke(
      { messages: [{ role: "user", content: "look up user information" }] },
      // highlight-next-line
      { configurable: { user_id: "user_123" } }
    );
    ```
    :::

### Source References

- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`sync`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L556) (function in checkpoint)
- [`time`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/id.py#L61) (function in checkpoint)
