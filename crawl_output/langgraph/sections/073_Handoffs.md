## Handoffs

A common pattern in multi-agent interactions is **handoffs**, where one agent _hands off_ control to another. Handoffs allow you to specify:

- **destination**: target agent to navigate to
- **payload**: information to pass to that agent

:::python
This is used both by `langgraph-supervisor` (supervisor hands off to individual agents) and `langgraph-swarm` (an individual agent can hand off to other agents).

To implement handoffs with `create_react_agent`, you need to:

1.  Create a special tool that can transfer control to a different agent

    ```python
    def transfer_to_bob():
        """Transfer to bob."""
        return Command(
            # name of the agent (node) to go to
            # highlight-next-line
            goto="bob",
            # data to send to the agent
            # highlight-next-line
            update={"messages": [...]},
            # indicate to LangGraph that we need to navigate to
            # agent node in a parent graph
            # highlight-next-line
            graph=Command.PARENT,
        )
    ```

2.  Create individual agents that have access to handoff tools:

    ```python
    flight_assistant = create_react_agent(
        ..., tools=[book_flight, transfer_to_hotel_assistant]
    )
    hotel_assistant = create_react_agent(
        ..., tools=[book_hotel, transfer_to_flight_assistant]
    )
    ```

3.  Define a parent graph that contains individual agents as nodes:

    ```python
    from langgraph.graph import StateGraph, MessagesState
    multi_agent_graph = (
        StateGraph(MessagesState)
        .add_node(flight_assistant)
        .add_node(hotel_assistant)
        ...
    )
    ```

:::

:::js
This is used both by `@langchain/langgraph-supervisor` (supervisor hands off to individual agents) and `@langchain/langgraph-swarm` (an individual agent can hand off to other agents).

To implement handoffs with `createReactAgent`, you need to:

1.  Create a special tool that can transfer control to a different agent

    ```typescript
    function transferToBob() {
      /**Transfer to bob.*/
      return new Command({
        // name of the agent (node) to go to
        // highlight-next-line
        goto: "bob",
        // data to send to the agent
        // highlight-next-line
        update: { messages: [...] },
        // indicate to LangGraph that we need to navigate to
        // agent node in a parent graph
        // highlight-next-line
        graph: Command.PARENT,
      });
    }
    ```

2.  Create individual agents that have access to handoff tools:

    ```typescript
    const flightAssistant = createReactAgent({
      ..., tools: [bookFlight, transferToHotelAssistant]
    });
    const hotelAssistant = createReactAgent({
      ..., tools: [bookHotel, transferToFlightAssistant]
    });
    ```

3.  Define a parent graph that contains individual agents as nodes:

    ```typescript
    import { StateGraph, MessagesZodState } from "@langchain/langgraph";
    const multiAgentGraph = new StateGraph(MessagesZodState)
      .addNode("flight_assistant", flightAssistant)
      .addNode("hotel_assistant", hotelAssistant)
      // ...
    ```

    :::

Putting this together, here is how you can implement a simple multi-agent system with two agents — a flight booking assistant and a hotel booking assistant:

:::python

```python
from typing import Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langgraph.prebuilt import create_react_agent, InjectedState
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.types import Command

def create_handoff_tool(*, agent_name: str, description: str | None = None):
    name = f"transfer_to_{agent_name}"
    description = description or f"Transfer to {agent_name}"

    @tool(name, description=description)
    def handoff_tool(
        # highlight-next-line
        state: Annotated[MessagesState, InjectedState], # (1)!
        # highlight-next-line
        tool_call_id: Annotated[str, InjectedToolCallId],
    ) -> Command:
        tool_message = {
            "role": "tool",
            "content": f"Successfully transferred to {agent_name}",
            "name": name,
            "tool_call_id": tool_call_id,
        }
        return Command(  # (2)!
            # highlight-next-line
            goto=agent_name,  # (3)!
            # highlight-next-line
            update={"messages": state["messages"] + [tool_message]},  # (4)!
            # highlight-next-line
            graph=Command.PARENT,  # (5)!
        )
    return handoff_tool

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`transfer_to_bob`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_tool_node.py#L1215) (function in prebuilt)
- [`InjectedState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1584) (class in prebuilt)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
