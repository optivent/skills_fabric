## Handoffs as tools

One of the most common agent types is a [tool-calling agent](../agents/overview.md). For those types of agents, a common pattern is wrapping a handoff in a tool call:

:::python

```python
from langchain_core.tools import tool

@tool
def transfer_to_bob():
    """Transfer to bob."""
    return Command(
        # name of the agent (node) to go to
        goto="bob",
        # data to send to the agent
        update={"my_state_key": "my_state_value"},
        # indicate to LangGraph that we need to navigate to
        # agent node in a parent graph
        graph=Command.PARENT,
    )
```

:::

:::js

```typescript
import { tool } from "@langchain/core/tools";
import { Command } from "@langchain/langgraph";
import { z } from "zod";

const transferToBob = tool(
  async () => {
    return new Command({
      // name of the agent (node) to go to
      goto: "bob",
      // data to send to the agent
      update: { myStateKey: "myStateValue" },
      // indicate to LangGraph that we need to navigate to
      // agent node in a parent graph
      graph: Command.PARENT,
    });
  },
  {
    name: "transfer_to_bob",
    description: "Transfer to bob.",
    schema: z.object({}),
  }
);
```

:::

This is a special case of updating the graph state from tools where, in addition to the state update, the control flow is included as well.

!!! important

      :::python
      If you want to use tools that return `Command`, you can use the prebuilt @[`create_react_agent`][create_react_agent] / @[`ToolNode`][ToolNode] components, or else implement your own logic:

      ```python
      def call_tools(state):
          ...
          commands = [tools_by_name[tool_call["name"]].invoke(tool_call) for tool_call in tool_calls]
          return commands
      ```
      :::

      :::js
      If you want to use tools that return `Command`, you can use the prebuilt @[`createReactAgent`][create_react_agent] / @[ToolNode] components, or else implement your own logic:

      ```typescript
      graph.addNode("call_tools", async (state) => {
        // ... tool execution logic
        const commands = toolCalls.map((toolCall) =>
          toolsByName[toolCall.name].invoke(toolCall)
        );
        return commands;
      });
      ```
      :::

Let's now take a closer look at the different multi-agent architectures.

### Source References

- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`transfer_to_bob`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_tool_node.py#L1215) (function in prebuilt)
- [`ToolNode`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L610) (class in prebuilt)
- [`tools_by_name`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L777) (function in prebuilt)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`close`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L573) (function in checkpoint)
