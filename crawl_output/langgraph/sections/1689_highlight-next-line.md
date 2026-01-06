## highlight-next-line

from langgraph.config import get_store

@tool
def save_user_info(user_info: str, config: RunnableConfig) -> str:
    """Save user info."""
    # Same as that provided to `builder.compile(store=store)`
    # or `create_react_agent`
    # highlight-next-line
    store = get_store()
    user_id = config["configurable"].get("user_id")
    # highlight-next-line
    store.put(("users",), user_id, user_info)
    return "Successfully saved user info."

builder = StateGraph(...)
...
graph = builder.compile(store=store)
```

:::

:::js
To **update** information in the store:

```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";
import type { LangGraphRunnableConfig } from "@langchain/langgraph";

const saveUserInfo = tool(
  async (input, config: LangGraphRunnableConfig) => {
    // Same as that provided to `builder.compile({ store })`
    // or `createReactAgent`
    // highlight-next-line
    const store = config.store;
    if (!store) throw new Error("Store not provided");

    const userId = config?.configurable?.user_id;
    // highlight-next-line
    await store.put(["users"], userId, input.userInfo);
    return "Successfully saved user info.";
  },
  {
    name: "save_user_info",
    description: "Save user info.",
    schema: z.object({
      userInfo: z.string().describe("User information to save"),
    }),
  }
);
```

:::

??? example "Update long-term memory"

    :::python
    ```python
    from typing_extensions import TypedDict

    from langchain_core.tools import tool
    from langgraph.config import get_store
    from langchain_core.runnables import RunnableConfig
    from langgraph.prebuilt import create_react_agent
    from langgraph.store.memory import InMemoryStore

    store = InMemoryStore() # (1)!

    class UserInfo(TypedDict): # (2)!
        name: str

    @tool
    def save_user_info(user_info: UserInfo, config: RunnableConfig) -> str: # (3)!
        """Save user info."""
        # Same as that provided to `create_react_agent`
        # highlight-next-line
        store = get_store() # (4)!
        user_id = config["configurable"].get("user_id")
        # highlight-next-line
        store.put(("users",), user_id, user_info) # (5)!
        return "Successfully saved user info."

    agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=[save_user_info],
        # highlight-next-line
        store=store
    )

    # Run the agent
    agent.invoke(
        {"messages": [{"role": "user", "content": "My name is John Smith"}]},
        # highlight-next-line
        config={"configurable": {"user_id": "user_123"}} # (6)!
    )

    # You can access the store directly to get the value
    store.get(("users",), "user_123").value
    ```

    1. The `InMemoryStore` is a store that stores data in memory. In a production setting, you would typically use a database or other persistent storage. Please review the [store documentation](../reference/store.md) for more options. If you're deploying with **LangGraph Platform**, the platform will provide a production-ready store for you.
    2. The `UserInfo` class is a `TypedDict` that defines the structure of the user information. The LLM will use this to format the response according to the schema.
    3. The `save_user_info` function is a tool that allows an agent to update user information. This could be useful for a chat application where the user wants to update their profile information.
    4. The `get_store` function is used to access the store. You can call it from anywhere in your code, including tools and prompts. This function returns the store that was passed to the agent when it was created.
    5. The `put` method is used to store data in the store. The first argument is the namespace, and the second argument is the key. This will store the user information in the store.
    6. The `user_id` is passed in the config. This is used to identify the user whose information is being updated.
    :::

    :::js
    ```typescript
    import { tool } from "@langchain/core/tools";
    import { z } from "zod";
    import { createReactAgent } from "@langchain/langgraph/prebuilt";
    import { InMemoryStore } from "@langchain/langgraph";
    import { ChatAnthropic } from "@langchain/anthropic";
    import type { LangGraphRunnableConfig } from "@langchain/langgraph";

    const store = new InMemoryStore(); // (1)!

    const UserInfoSchema = z.object({ // (2)!
      name: z.string(),
    });

    const saveUserInfo = tool(
      async (input, config: LangGraphRunnableConfig) => { // (3)!
        // Same as that provided to `createReactAgent`
        // highlight-next-line
        const store = config.store; // (4)!
        if (!store) throw new Error("Store not provided");

        const userId = config?.configurable?.user_id;
        // highlight-next-line
        await store.put(["users"], userId, input); // (5)!
        return "Successfully saved user info.";
      },
      {
        name: "save_user_info",
        description: "Save user info.",
        schema: UserInfoSchema,
      }
    );

    const agent = createReactAgent({
      llm: new ChatAnthropic({ model: "claude-3-5-sonnet-20240620" }),
      tools: [saveUserInfo],
      // highlight-next-line
      store: store
    });

    // Run the agent
    await agent.invoke(
      { messages: [{ role: "user", content: "My name is John Smith" }] },
      // highlight-next-line
      { configurable: { user_id: "user_123" } } // (6)!
    );

    // You can access the store directly to get the value
    const userInfo = await store.get(["users"], "user_123");
    console.log(userInfo?.value);
    ```

    1. The `InMemoryStore` is a store that stores data in memory. In production, you would typically use a database or other persistent storage. Please review the [store documentation](../reference/store.md) for more options. If you're deploying with **LangGraph Platform**, the platform will provide a production-ready store for you.
    2. The `UserInfoSchema` is a Zod schema that defines the structure of the user information. The LLM will use this to format the response according to the schema.
    3. The `saveUserInfo` function is a tool that allows an agent to update user information. This could be useful for a chat application where the user wants to update their profile information.
    4. The store is accessible from the config object that is passed to the tool. This enables the tool to access the store when running.
    5. The `put` method is used to store data in the store. The first argument is the namespace, and the second argument is the key. This will store the user information in the store.
    6. The `user_id` is passed in the config. This is used to identify the user whose information is being updated.
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`prompt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L566) (function in prebuilt)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
