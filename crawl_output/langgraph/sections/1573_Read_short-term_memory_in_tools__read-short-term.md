## Read short-term memory in tools { #read-short-term }

LangGraph allows agents to access their short-term memory (state) inside the tools.

:::python

```python
from typing import Annotated
from langgraph.prebuilt import InjectedState, create_react_agent

class CustomState(AgentState):
    # highlight-next-line
    user_id: str

def get_user_info(
    # highlight-next-line
    state: Annotated[CustomState, InjectedState]
) -> str:
    """Look up user info."""
    # highlight-next-line
    user_id = state["user_id"]
    return "User is John Smith" if user_id == "user_123" else "Unknown user"

agent = create_react_agent(
    model="anthropic:claude-3-7-sonnet-latest",
    tools=[get_user_info],
    # highlight-next-line
    state_schema=CustomState,
)

agent.invoke({
    "messages": "look up user information",
    # highlight-next-line
    "user_id": "user_123"
})
```

:::

:::js

```typescript
import { tool } from "@langchain/core/tools";
import { z } from "zod";
import {
  MessagesZodState,
  LangGraphRunnableConfig,
} from "@langchain/langgraph";
import { createReactAgent } from "@langchain/langgraph/prebuilt";

const CustomState = z.object({
  messages: MessagesZodState.shape.messages,
  userId: z.string(),
});

const getUserInfo = tool(
  async (_, config: LangGraphRunnableConfig) => {
    const userId = config.configurable?.userId;
    return userId === "user_123" ? "User is John Smith" : "Unknown user";
  },
  {
    name: "get_user_info",
    description: "Look up user info.",
    schema: z.object({}),
  }
);

const agent = createReactAgent({
  llm: model,
  tools: [getUserInfo],
  stateSchema: CustomState,
});

await agent.invoke({
  messages: [{ role: "user", content: "look up user information" }],
  userId: "user_123",
});
```

:::

See the [Context](../../agents/context.md) guide for more information.

### Source References

- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`CustomState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L525) (class in prebuilt)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`InjectedState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1584) (class in prebuilt)
- [`AgentState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/example_app/example_graph.py#L12) (class in langgraph)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
