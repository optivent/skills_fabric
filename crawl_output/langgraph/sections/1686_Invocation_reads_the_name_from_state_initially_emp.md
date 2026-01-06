## Invocation: reads the name from state (initially empty)

agent.invoke({"messages": "what's my name?"})
```

:::

:::js
To **access** (read) the graph state inside the tools, you can use the @[`getContextVariable`][getContextVariable] function:

```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";
import { getContextVariable } from "@langchain/core/context";
import { MessagesZodState } from "@langchain/langgraph";
import type { LangGraphRunnableConfig } from "@langchain/langgraph";

const getUserName = tool(
  // highlight-next-line
  async (_, config: LangGraphRunnableConfig) => {
    // highlight-next-line
    const currentState = getContextVariable("currentState") as z.infer<
      typeof MessagesZodState
    > & { userName?: string };
    return currentState?.userName || "Unknown user";
  },
  {
    name: "get_user_name",
    description: "Retrieve the current user name from state.",
    schema: z.object({}),
  }
);
```

:::

:::python
Use a tool that returns a `Command` to **update** `user_name` and append a confirmation message:

```python
from typing import Annotated
from langgraph.types import Command
from langchain_core.messages import ToolMessage
from langchain_core.tools import tool, InjectedToolCallId

@tool
def update_user_name(
    new_name: str,
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Update user-name in short-term memory."""
    # highlight-next-line
    return Command(update={
        # highlight-next-line
        "user_name": new_name,
        # highlight-next-line
        "messages": [
            # highlight-next-line
            ToolMessage(f"Updated user name to {new_name}", tool_call_id=tool_call_id)
            # highlight-next-line
        ]
        # highlight-next-line
    })
```

:::

:::js
To **update** short-term memory, you can use tools that return a `Command` to update state:

```typescript
import { Command } from "@langchain/langgraph";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const updateUserName = tool(
  async (input) => {
    // highlight-next-line
    return new Command({
      // highlight-next-line
      update: {
        // highlight-next-line
        userName: input.newName,
        // highlight-next-line
        messages: [
          // highlight-next-line
          {
            // highlight-next-line
            role: "assistant",
            // highlight-next-line
            content: `Updated user name to ${input.newName}`,
            // highlight-next-line
          },
          // highlight-next-line
        ],
        // highlight-next-line
      },
      // highlight-next-line
    });
  },
  {
    name: "update_user_name",
    description: "Update user name in short-term memory.",
    schema: z.object({
      newName: z.string().describe("The new user name"),
    }),
  }
);
```

:::

!!! important

    :::python
    If you want to use tools that return `Command` and update graph state, you can either use prebuilt @[`create_react_agent`][create_react_agent] / @[`ToolNode`][ToolNode] components, or implement your own tool-executing node that collects `Command` objects returned by the tools and returns a list of them, e.g.:

    ```python
    def call_tools(state):
        ...
        commands = [tools_by_name[tool_call["name"]].invoke(tool_call) for tool_call in tool_calls]
        return commands
    ```
    :::

    :::js
    If you want to use tools that return `Command` and update graph state, you can either use prebuilt @[`createReactAgent`][create_react_agent] / @[ToolNode] components, or implement your own tool-executing node that collects `Command` objects returned by the tools and returns a list of them, e.g.:

    ```typescript
    const callTools = async (state: State) => {
      // ...
      const commands = await Promise.all(
        toolCalls.map(toolCall => toolsByName[toolCall.name].invoke(toolCall))
      );
      return commands;
    };
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`get_user_name`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4731) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`ToolNode`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L610) (class in prebuilt)
- [`tools_by_name`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L777) (function in prebuilt)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
