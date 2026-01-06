## Define multi-agent graph

multi_agent_graph = (
    StateGraph(MessagesState)
    # highlight-next-line
    .add_node(flight_assistant)
    # highlight-next-line
    .add_node(hotel_assistant)
    .add_edge(START, "flight_assistant")
    .compile()
)
```
:::

:::js
```typescript
import { createReactAgent } from "@langchain/langgraph/prebuilt";
import { StateGraph, START, MessagesZodState } from "@langchain/langgraph";
import { z } from "zod";

function createHandoffTool({
  agentName,
  description,
}: {
  agentName: string;
  description?: string;
}) {
  // same implementation as above
  // ...
  return new Command(/* ... */);
}

// Handoffs
const transferToHotelAssistant = createHandoffTool({
  agentName: "hotel_assistant",
});
const transferToFlightAssistant = createHandoffTool({
  agentName: "flight_assistant",
});

// Define agents
const flightAssistant = createReactAgent({
  llm: model,
  // highlight-next-line
  tools: [/* ... */, transferToHotelAssistant],
  // highlight-next-line
  name: "flight_assistant",
});

const hotelAssistant = createReactAgent({
  llm: model,
  // highlight-next-line
  tools: [/* ... */, transferToFlightAssistant],
  // highlight-next-line
  name: "hotel_assistant",
});

// Define multi-agent graph
const multiAgentGraph = new StateGraph(MessagesZodState)
  // highlight-next-line
  .addNode("flight_assistant", flightAssistant)
  // highlight-next-line
  .addNode("hotel_assistant", hotelAssistant)
  .addEdge(START, "flight_assistant")
  .compile();
```
:::

??? example "Full example: Multi-agent system for booking travel"

    :::python
    ```python
    from typing import Annotated
    from langchain_core.messages import convert_to_messages
    from langchain_core.tools import tool, InjectedToolCallId
    from langgraph.prebuilt import create_react_agent, InjectedState
    from langgraph.graph import StateGraph, START, MessagesState
    from langgraph.types import Command
    
    # We'll use `pretty_print_messages` helper to render the streamed agent outputs nicely
    
    def pretty_print_message(message, indent=False):
        pretty_message = message.pretty_repr(html=True)
        if not indent:
            print(pretty_message)
            return
    
        indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
        print(indented)
    
    
    def pretty_print_messages(update, last_message=False):
        is_subgraph = False
        if isinstance(update, tuple):
            ns, update = update
            # skip parent graph updates in the printouts
            if len(ns) == 0:
                return
    
            graph_id = ns[-1].split(":")[0]
            print(f"Update from subgraph {graph_id}:")
            print("\n")
            is_subgraph = True
    
        for node_name, node_update in update.items():
            update_label = f"Update from node {node_name}:"
            if is_subgraph:
                update_label = "\t" + update_label
    
            print(update_label)
            print("\n")
    
            messages = convert_to_messages(node_update["messages"])
            if last_message:
                messages = messages[-1:]
    
            for m in messages:
                pretty_print_message(m, indent=is_subgraph)
            print("\n")


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
    
    # Handoffs
    transfer_to_hotel_assistant = create_handoff_tool(
        agent_name="hotel_assistant",
        description="Transfer user to the hotel-booking assistant.",
    )
    transfer_to_flight_assistant = create_handoff_tool(
        agent_name="flight_assistant",
        description="Transfer user to the flight-booking assistant.",
    )
    
    # Simple agent tools
    def book_hotel(hotel_name: str):
        """Book a hotel"""
        return f"Successfully booked a stay at {hotel_name}."
    
    def book_flight(from_airport: str, to_airport: str):
        """Book a flight"""
        return f"Successfully booked a flight from {from_airport} to {to_airport}."
    
    # Define agents
    flight_assistant = create_react_agent(
        model="anthropic:claude-3-5-sonnet-latest",
        # highlight-next-line
        tools=[book_flight, transfer_to_hotel_assistant],
        prompt="You are a flight booking assistant",
        # highlight-next-line
        name="flight_assistant"
    )
    hotel_assistant = create_react_agent(
        model="anthropic:claude-3-5-sonnet-latest",
        # highlight-next-line
        tools=[book_hotel, transfer_to_flight_assistant],
        prompt="You are a hotel booking assistant",
        # highlight-next-line
        name="hotel_assistant"
    )
    
    # Define multi-agent graph
    multi_agent_graph = (
        StateGraph(MessagesState)
        .add_node(flight_assistant)
        .add_node(hotel_assistant)
        .add_edge(START, "flight_assistant")
        .compile()
    )
    
    # Run the multi-agent graph
    for chunk in multi_agent_graph.stream(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "book a flight from BOS to JFK and a stay at McKittrick Hotel"
                }
            ]
        },
        # highlight-next-line
        subgraphs=True
    ):
        pretty_print_messages(chunk)
    ```

    1. Access agent's state
    2. The `Command` primitive allows specifying a state update and a node transition as a single operation, making it useful for implementing handoffs.
    3. Name of the agent or node to hand off to.
    4. Take the agent's messages and **add** them to the parent's **state** as part of the handoff. The next agent will see the parent state.
    5. Indicate to LangGraph that we need to navigate to agent node in a **parent** multi-agent graph.
    :::

    :::js
    ```typescript
    import { tool } from "@langchain/core/tools";
    import { createReactAgent } from "@langchain/langgraph/prebuilt";
    import { StateGraph, START, MessagesZodState, Command } from "@langchain/langgraph";
    import { ChatAnthropic } from "@langchain/anthropic";
    import { isBaseMessage } from "@langchain/core/messages";
    import { z } from "zod";

    // We'll use a helper to render the streamed agent outputs nicely
    const prettyPrintMessages = (update: Record<string, any>) => {
      // Handle tuple case with namespace
      if (Array.isArray(update)) {
        const [ns, updateData] = update;
        // Skip parent graph updates in the printouts
        if (ns.length === 0) {
          return;
        }

        const graphId = ns[ns.length - 1].split(":")[0];
        console.log(`Update from subgraph ${graphId}:\n`);
        update = updateData;
      }

      for (const [nodeName, updateValue] of Object.entries(update)) {
        console.log(`Update from node ${nodeName}:\n`);

        const messages = updateValue.messages || [];
        for (const message of messages) {
          if (isBaseMessage(message)) {
            const textContent =
              typeof message.content === "string"
                ? message.content
                : JSON.stringify(message.content);
            console.log(`${message.getType()}: ${textContent}`);
          }
        }
        console.log("\n");
      }
    };

    function createHandoffTool({
      agentName,
      description,
    }: {
      agentName: string;
      description?: string;
    }) {
      const name = `transfer_to_${agentName}`;
      const toolDescription = description || `Transfer to ${agentName}`;

      return tool(
        async (_, config) => {
          // highlight-next-line
          const state = config.state; // (1)!
          const toolCallId = config.toolCall.id;

          const toolMessage = {
            role: "tool" as const,
            content: `Successfully transferred to ${agentName}`,
            name: name,
            tool_call_id: toolCallId,
          };

          return new Command({
            // highlight-next-line
            goto: agentName, // (3)!
            // highlight-next-line
            update: { messages: [...state.messages, toolMessage] }, // (4)!
            // highlight-next-line
            graph: Command.PARENT, // (5)!
          });
        },
        {
          name,
          description: toolDescription,
          schema: z.object({}),
        }
      );
    }

    // Handoffs
    const transferToHotelAssistant = createHandoffTool({
      agentName: "hotel_assistant",
      description: "Transfer user to the hotel-booking assistant.",
    });

    const transferToFlightAssistant = createHandoffTool({
      agentName: "flight_assistant",
      description: "Transfer user to the flight-booking assistant.",
    });

    // Simple agent tools
    const bookHotel = tool(
      async ({ hotelName }) => {
        return `Successfully booked a stay at ${hotelName}.`;
      },
      {
        name: "book_hotel",
        description: "Book a hotel",
        schema: z.object({
          hotelName: z.string(),
        }),
      }
    );

    const bookFlight = tool(
      async ({ fromAirport, toAirport }) => {
        return `Successfully booked a flight from ${fromAirport} to ${toAirport}.`;
      },
      {
        name: "book_flight",
        description: "Book a flight",
        schema: z.object({
          fromAirport: z.string(),
          toAirport: z.string(),
        }),
      }
    );

    const model = new ChatAnthropic({
      model: "claude-3-5-sonnet-latest",
    });

    // Define agents
    const flightAssistant = createReactAgent({
      llm: model,
      // highlight-next-line
      tools: [bookFlight, transferToHotelAssistant],
      prompt: "You are a flight booking assistant",
      // highlight-next-line
      name: "flight_assistant",
    });

    const hotelAssistant = createReactAgent({
      llm: model,
      // highlight-next-line
      tools: [bookHotel, transferToFlightAssistant],
      prompt: "You are a hotel booking assistant",
      // highlight-next-line
      name: "hotel_assistant",
    });

    // Define multi-agent graph
    const multiAgentGraph = new StateGraph(MessagesZodState)
      .addNode("flight_assistant", flightAssistant)
      .addNode("hotel_assistant", hotelAssistant)
      .addEdge(START, "flight_assistant")
      .compile();

    // Run the multi-agent graph
    const stream = await multiAgentGraph.stream(
      {
        messages: [
          {
            role: "user",
            content: "book a flight from BOS to JFK and a stay at McKittrick Hotel",
          },
        ],
      },
      // highlight-next-line
      { subgraphs: true }
    );

    for await (const chunk of stream) {
      prettyPrintMessages(chunk);
    }
    ```

    1. Access agent's state
    2. The `Command` primitive allows specifying a state update and a node transition as a single operation, making it useful for implementing handoffs.
    3. Name of the agent or node to hand off to.
    4. Take the agent's messages and **add** them to the parent's **state** as part of the handoff. The next agent will see the parent state.
    5. Indicate to LangGraph that we need to navigate to agent node in a **parent** multi-agent graph.
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`prompt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L566) (function in prebuilt)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`InjectedState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1584) (class in prebuilt)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
