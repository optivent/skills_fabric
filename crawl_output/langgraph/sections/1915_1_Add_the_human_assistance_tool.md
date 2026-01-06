## 1. Add the `human_assistance` tool

Starting with the existing code from the [Add memory to the chatbot](./3-add-memory.md) tutorial, add the `human_assistance` tool to the chatbot. This tool uses `interrupt` to receive information from a human.

Let's first select a chat model:

:::python
{% include-markdown "../../../snippets/chat_model_tabs.md" %}

<!---
```python
from langchain.chat_models import init_chat_model

llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")
```
-->

:::

:::js

```typescript
// Add your API key here
process.env.ANTHROPIC_API_KEY = "YOUR_API_KEY";
```

:::

We can now incorporate it into our `StateGraph` with an additional tool:

:::python

```python hl_lines="12 19 20 21 22 23"
from typing import Annotated

from langchain_tavily import TavilySearch
from langchain_core.tools import tool
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from langgraph.types import Command, interrupt

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]

tool = TavilySearch(max_results=2)
tools = [tool, human_assistance]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    # Because we will be interrupting during tool execution,
    # we disable parallel tool calling to avoid repeating any
    # tool invocations when we resume.
    assert len(message.tool_calls) <= 1
    return {"messages": [message]}

graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
```

:::

:::js

```typescript hl_lines="1 7-19"
import { interrupt, MessagesZodState } from "@langchain/langgraph";
import { ChatAnthropic } from "@langchain/anthropic";
import { TavilySearch } from "@langchain/tavily";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const humanAssistance = tool(
  async ({ query }) => {
    const humanResponse = interrupt({ query });
    return humanResponse.data;
  },
  {
    name: "humanAssistance",
    description: "Request assistance from a human.",
    schema: z.object({
      query: z.string().describe("Human readable question for the human"),
    }),
  }
);

const searchTool = new TavilySearch({ maxResults: 2 });
const searchTool = new TavilySearch({ maxResults: 2 });
const tools = [searchTool, humanAssistance];

const llmWithTools = new ChatAnthropic({
  model: "claude-3-5-sonnet-latest",
}).bindTools(tools);
const llmWithTools = new ChatAnthropic({
  model: "claude-3-5-sonnet-latest",
}).bindTools(tools);

async function chatbot(state: z.infer<typeof MessagesZodState>) {
async function chatbot(state: z.infer<typeof MessagesZodState>) {
  const message = await llmWithTools.invoke(state.messages);


  // Because we will be interrupting during tool execution,
  // we disable parallel tool calling to avoid repeating any
  // tool invocations when we resume.
  if (message.tool_calls && message.tool_calls.length > 1) {
    throw new Error("Multiple tool calls not supported with interrupts");
  }

  return { messages: message };
}
```

:::

!!! tip

    For more information and examples of human-in-the-loop workflows, see [Human-in-the-loop](../../concepts/human_in_the_loop.md).

### Source References

- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`human_assistance`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L605) (function in prebuilt)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`bind_tools`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/react_agent.py#L19) (function in langgraph)
- [`HumanResponse`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/interrupt.py#L87) (class in prebuilt)
- [`ToolNode`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L610) (class in prebuilt)
- [`tools_condition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L8365) (function in langgraph)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
