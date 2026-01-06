## 6. View the new value

:::python
If you call `graph.get_state`, you can see the new value is reflected:

```python
snapshot = graph.get_state(config)

{k: v for k, v in snapshot.values.items() if k in ("name", "birthday")}
```

```
{'name': 'LangGraph (library)', 'birthday': 'Jan 17, 2024'}
```

:::

:::js
If you call `graph.getState`, you can see the new value is reflected:

```typescript
const updatedSnapshot = await graph.getState(config);

const updatedRelevantState = Object.fromEntries(
  Object.entries(updatedSnapshot.values).filter(([k]) =>
    ["name", "birthday"].includes(k)
  )
);
```

```typescript
{ name: 'LangGraph (library)', birthday: 'Jan 17, 2024' }
```

:::

Manual state updates will [generate a trace](https://smith.langchain.com/public/7ebb7827-378d-49fe-9f6c-5df0e90086c8/r) in LangSmith. If desired, they can also be used to [control human-in-the-loop workflows](../../how-tos/human_in_the_loop/add-human-in-the-loop.md). Use of the `interrupt` function is generally recommended instead, as it allows data to be transmitted in a human-in-the-loop interaction independently of state updates.

**Congratulations!** You've added custom keys to the state to facilitate a more complex workflow, and learned how to generate state updates from inside tools.

Check out the code snippet below to review the graph from this tutorial:

:::python

{% include-markdown "../../../snippets/chat_model_tabs.md" %}

<!---
```python
from langchain.chat_models import init_chat_model

llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")
```
-->

```python
from typing import Annotated

from langchain_tavily import TavilySearch
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from typing_extensions import TypedDict

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import Command, interrupt

class State(TypedDict):
    messages: Annotated[list, add_messages]
    name: str
    birthday: str

@tool
def human_assistance(
    name: str, birthday: str, tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """Request assistance from a human."""
    human_response = interrupt(
        {
            "question": "Is this correct?",
            "name": name,
            "birthday": birthday,
        },
    )
    if human_response.get("correct", "").lower().startswith("y"):
        verified_name = name
        verified_birthday = birthday
        response = "Correct"
    else:
        verified_name = human_response.get("name", name)
        verified_birthday = human_response.get("birthday", birthday)
        response = f"Made a correction: {human_response}"

    state_update = {
        "name": verified_name,
        "birthday": verified_birthday,
        "messages": [ToolMessage(response, tool_call_id=tool_call_id)],
    }
    return Command(update=state_update)


tool = TavilySearch(max_results=2)
tools = [tool, human_assistance]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    message = llm_with_tools.invoke(state["messages"])
    assert(len(message.tool_calls) <= 1)
    return {"messages": [message]}

graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)

tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

memory = InMemorySaver()
graph = graph_builder.compile(checkpointer=memory)
```

:::

:::js

```typescript
import {
  Command,
  interrupt,
  MessagesZodState,
  MemorySaver,
  StateGraph,
  END,
  START,
} from "@langchain/langgraph";
import { ToolNode, toolsCondition } from "@langchain/langgraph/prebuilt";
import { ChatAnthropic } from "@langchain/anthropic";
import { TavilySearch } from "@langchain/tavily";
import { ToolMessage } from "@langchain/core/messages";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const State = z.object({
  messages: MessagesZodState.shape.messages,
  name: z.string(),
  birthday: z.string(),
});

const humanAssistance = tool(
  async (input, config) => {
    // Note that because we are generating a ToolMessage for a state update, we
    // generally require the ID of the corresponding tool call. This is available
    // in the tool's config.
    const toolCallId = config?.toolCall?.id as string | undefined;
    if (!toolCallId) throw new Error("Tool call ID is required");

    const humanResponse = await interrupt({
      question: "Is this correct?",
      name: input.name,
      birthday: input.birthday,
    });

    // We explicitly update the state with a ToolMessage inside the tool.
    const stateUpdate = (() => {
      // If the information is correct, update the state as-is.
      if (humanResponse.correct?.toLowerCase().startsWith("y")) {
        return {
          name: input.name,
          birthday: input.birthday,
          messages: [
            new ToolMessage({ content: "Correct", tool_call_id: toolCallId }),
          ],
        };
      }

      // Otherwise, receive information from the human reviewer.
      return {
        name: humanResponse.name || input.name,
        birthday: humanResponse.birthday || input.birthday,
        messages: [
          new ToolMessage({
            content: `Made a correction: ${JSON.stringify(humanResponse)}`,
            tool_call_id: toolCallId,
          }),
        ],
      };
    })();

    // We return a Command object in the tool to update our state.
    return new Command({ update: stateUpdate });
  },
  {
    name: "humanAssistance",
    description: "Request assistance from a human.",
    schema: z.object({
      name: z.string().describe("The name of the entity"),
      birthday: z.string().describe("The birthday/release date of the entity"),
    }),
  }
);

const searchTool = new TavilySearch({ maxResults: 2 });

const tools = [searchTool, humanAssistance];
const llmWithTools = new ChatAnthropic({
  model: "claude-3-5-sonnet-latest",
}).bindTools(tools);

const memory = new MemorySaver();

const chatbot = async (state: z.infer<typeof State>) => {
  const message = await llmWithTools.invoke(state.messages);
  return { messages: message };
};

const graph = new StateGraph(State)
  .addNode("chatbot", chatbot)
  .addNode("tools", new ToolNode(tools))
  .addConditionalEdges("chatbot", toolsCondition, ["tools", END])
  .addEdge("tools", "chatbot")
  .addEdge(START, "chatbot")
  .compile({ checkpointer: memory });
```

:::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`human_assistance`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L605) (function in prebuilt)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`bind_tools`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/react_agent.py#L19) (function in langgraph)
- [`HumanResponse`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/interrupt.py#L87) (class in prebuilt)
- [`ToolNode`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L610) (class in prebuilt)
- [`tools_condition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L8365) (function in langgraph)
