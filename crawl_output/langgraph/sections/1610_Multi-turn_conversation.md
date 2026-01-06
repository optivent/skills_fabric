## Multi-turn conversation

Users might want to engage in a *multi-turn conversation* with one or more agents. To build a system that can handle this, you can create a node that uses an @[`interrupt`][interrupt] to collect user input and routes back to the **active** agent.

The agents can then be implemented as nodes in a graph that executes agent steps and determines the next action:

1. **Wait for user input** to continue the conversation, or  
2. **Route to another agent** (or back to itself, such as in a loop) via a [handoff](#handoffs)

:::python
```python
def human(state) -> Command[Literal["agent", "another_agent"]]:
    """A node for collecting user input."""
    user_input = interrupt(value="Ready for user input.")

    # Determine the active agent.
    active_agent = ...

    ...
    return Command(
        update={
            "messages": [{
                "role": "human",
                "content": user_input,
            }]
        },
        goto=active_agent
    )

def agent(state) -> Command[Literal["agent", "another_agent", "human"]]:
    # The condition for routing/halting can be anything, e.g. LLM tool call / structured output, etc.
    goto = get_next_agent(...)  # 'agent' / 'another_agent'
    if goto:
        return Command(goto=goto, update={"my_state_key": "my_state_value"})
    else:
        return Command(goto="human") # Go to human node
```
:::

:::js
```typescript
import { interrupt, Command } from "@langchain/langgraph";

function human(state: MessagesState): Command {
  const userInput: string = interrupt("Ready for user input.");

  // Determine the active agent
  const activeAgent = /* ... */;

  return new Command({
    update: {
      messages: [{
        role: "human",
        content: userInput,
      }]
    },
    goto: activeAgent,
  });
}

function agent(state: MessagesState): Command {
  // The condition for routing/halting can be anything, e.g. LLM tool call / structured output, etc.
  const goto = getNextAgent(/* ... */); // 'agent' / 'anotherAgent'

  if (goto) {
    return new Command({
      goto,
      update: { myStateKey: "myStateValue" }
    });
  }

  return new Command({ goto: "human" });
}
```
:::

??? example "Full example: multi-agent system for travel recommendations"

    In this example, we will build a team of travel assistant agents that can communicate with each other via handoffs.
    
    We will create 2 agents:
    
    * travel_advisor: can help with travel destination recommendations. Can ask hotel_advisor for help.
    * hotel_advisor: can help with hotel recommendations. Can ask travel_advisor for help.

    :::python
    ```python
    from langchain_anthropic import ChatAnthropic
    from langgraph.graph import MessagesState, StateGraph, START
    from langgraph.prebuilt import create_react_agent, InjectedState
    from langgraph.types import Command, interrupt
    from langgraph.checkpoint.memory import InMemorySaver
    
    
    model = ChatAnthropic(model="claude-3-5-sonnet-latest")

    class MultiAgentState(MessagesState):
        last_active_agent: str
    
    
    # Define travel advisor tools and ReAct agent
    travel_advisor_tools = [
        get_travel_recommendations,
        make_handoff_tool(agent_name="hotel_advisor"),
    ]
    travel_advisor = create_react_agent(
        model,
        travel_advisor_tools,
        prompt=(
            "You are a general travel expert that can recommend travel destinations (e.g. countries, cities, etc). "
            "If you need hotel recommendations, ask 'hotel_advisor' for help. "
            "You MUST include human-readable response before transferring to another agent."
        ),
    )
    
    
    def call_travel_advisor(
        state: MultiAgentState,
    ) -> Command[Literal["hotel_advisor", "human"]]:
        # You can also add additional logic like changing the input to the agent / output from the agent, etc.
        # NOTE: we're invoking the ReAct agent with the full history of messages in the state
        response = travel_advisor.invoke(state)
        update = {**response, "last_active_agent": "travel_advisor"}
        return Command(update=update, goto="human")
    
    
    # Define hotel advisor tools and ReAct agent
    hotel_advisor_tools = [
        get_hotel_recommendations,
        make_handoff_tool(agent_name="travel_advisor"),
    ]
    hotel_advisor = create_react_agent(
        model,
        hotel_advisor_tools,
        prompt=(
            "You are a hotel expert that can provide hotel recommendations for a given destination. "
            "If you need help picking travel destinations, ask 'travel_advisor' for help."
            "You MUST include human-readable response before transferring to another agent."
        ),
    )
    
    
    def call_hotel_advisor(
        state: MultiAgentState,
    ) -> Command[Literal["travel_advisor", "human"]]:
        response = hotel_advisor.invoke(state)
        update = {**response, "last_active_agent": "hotel_advisor"}
        return Command(update=update, goto="human")
    
    
    def human_node(
        state: MultiAgentState, config
    ) -> Command[Literal["hotel_advisor", "travel_advisor", "human"]]:
        """A node for collecting user input."""
    
        user_input = interrupt(value="Ready for user input.")
        active_agent = state["last_active_agent"]
    
        return Command(
            update={
                "messages": [
                    {
                        "role": "human",
                        "content": user_input,
                    }
                ]
            },
            goto=active_agent,
        )
    
    
    builder = StateGraph(MultiAgentState)
    builder.add_node("travel_advisor", call_travel_advisor)
    builder.add_node("hotel_advisor", call_hotel_advisor)
    
    # This adds a node to collect human input, which will route
    # back to the active agent.
    builder.add_node("human", human_node)
    
    # We'll always start with a general travel advisor.
    builder.add_edge(START, "travel_advisor")
    
    
    checkpointer = InMemorySaver()
    graph = builder.compile(checkpointer=checkpointer)
    ```
    
    Let's test a multi turn conversation with this application.

    ```python
    import uuid
    
    thread_config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    
    inputs = [
        # 1st round of conversation,
        {
            "messages": [
                {"role": "user", "content": "i wanna go somewhere warm in the caribbean"}
            ]
        },
        # Since we're using `interrupt`, we'll need to resume using the Command primitive.
        # 2nd round of conversation,
        Command(
            resume="could you recommend a nice hotel in one of the areas and tell me which area it is."
        ),
        # 3rd round of conversation,
        Command(
            resume="i like the first one. could you recommend something to do near the hotel?"
        ),
    ]
    
    for idx, user_input in enumerate(inputs):
        print()
        print(f"--- Conversation Turn {idx + 1} ---")
        print()
        print(f"User: {user_input}")
        print()
        for update in graph.stream(
            user_input,
            config=thread_config,
            stream_mode="updates",
        ):
            for node_id, value in update.items():
                if isinstance(value, dict) and value.get("messages", []):
                    last_message = value["messages"][-1]
                    if isinstance(last_message, dict) or last_message.type != "ai":
                        continue
                    print(f"{node_id}: {last_message.content}")
    ```
    
    ```
    --- Conversation Turn 1 ---
    
    User: {'messages': [{'role': 'user', 'content': 'i wanna go somewhere warm in the caribbean'}]}
    
    travel_advisor: Based on the recommendations, Aruba would be an excellent choice for your Caribbean getaway! Aruba is known as "One Happy Island" and offers:
    - Year-round warm weather with consistent temperatures around 82°F (28°C)
    - Beautiful white sand beaches like Eagle Beach and Palm Beach
    - Clear turquoise waters perfect for swimming and snorkeling
    - Minimal rainfall and location outside the hurricane belt
    - A blend of Caribbean and Dutch culture
    - Great dining options and nightlife
    - Various water sports and activities
    
    Would you like me to get some specific hotel recommendations in Aruba for your stay? I can transfer you to our hotel advisor who can help with accommodations.
    
    --- Conversation Turn 2 ---
    
    User: Command(resume='could you recommend a nice hotel in one of the areas and tell me which area it is.')
    
    hotel_advisor: Based on the recommendations, I can suggest two excellent options:
    
    1. The Ritz-Carlton, Aruba - Located in Palm Beach
    - This luxury resort is situated in the vibrant Palm Beach area
    - Known for its exceptional service and amenities
    - Perfect if you want to be close to dining, shopping, and entertainment
    - Features multiple restaurants, a casino, and a world-class spa
    - Located on a pristine stretch of Palm Beach
    
    2. Bucuti & Tara Beach Resort - Located in Eagle Beach
    - An adults-only boutique resort on Eagle Beach
    - Known for being more intimate and peaceful
    - Award-winning for its sustainability practices
    - Perfect for a romantic getaway or peaceful vacation
    - Located on one of the most beautiful beaches in the Caribbean
    
    Would you like more specific information about either of these properties or their locations?
    
    --- Conversation Turn 3 ---
    
    User: Command(resume='i like the first one. could you recommend something to do near the hotel?')
    
    travel_advisor: Near the Ritz-Carlton in Palm Beach, here are some highly recommended activities:
    
    1. Visit the Palm Beach Plaza Mall - Just a short walk from the hotel, featuring shopping, dining, and entertainment
    2. Try your luck at the Stellaris Casino - It's right in the Ritz-Carlton
    3. Take a sunset sailing cruise - Many depart from the nearby pier
    4. Visit the California Lighthouse - A scenic landmark just north of Palm Beach
    5. Enjoy water sports at Palm Beach:
       - Jet skiing
       - Parasailing
       - Snorkeling
       - Stand-up paddleboarding
    
    Would you like more specific information about any of these activities or would you like to know about other options in the area?
    ```
    :::

    :::js
    ```typescript
    import { ChatAnthropic } from "@langchain/anthropic";
    import { StateGraph, START, MessagesZodState, Command, interrupt, MemorySaver } from "@langchain/langgraph";
    import { createReactAgent } from "@langchain/langgraph/prebuilt";
    import { tool } from "@langchain/core/tools";
    import { z } from "zod";

    const model = new ChatAnthropic({ model: "claude-3-5-sonnet-latest" });

    const MultiAgentState = MessagesZodState.extend({
      lastActiveAgent: z.string().optional(),
    });

    // Define travel advisor tools
    const getTravelRecommendations = tool(
      async () => {
        // Placeholder implementation
        return "Based on current trends, I recommend visiting Japan, Portugal, or New Zealand.";
      },
      {
        name: "get_travel_recommendations",
        description: "Get current travel destination recommendations",
        schema: z.object({}),
      }
    );

    const makeHandoffTool = (agentName: string) => {
      return tool(
        async (_, config) => {
          const state = config.state;
          const toolCallId = config.toolCall.id;

          const toolMessage = {
            role: "tool" as const,
            content: `Successfully transferred to ${agentName}`,
            name: `transfer_to_${agentName}`,
            tool_call_id: toolCallId,
          };

          return new Command({
            goto: agentName,
            update: { messages: [...state.messages, toolMessage] },
            graph: Command.PARENT,
          });
        },
        {
          name: `transfer_to_${agentName}`,
          description: `Transfer to ${agentName}`,
          schema: z.object({}),
        }
      );
    };

    const travelAdvisorTools = [
      getTravelRecommendations,
      makeHandoffTool("hotel_advisor"),
    ];

    const travelAdvisor = createReactAgent({
      llm: model,
      tools: travelAdvisorTools,
      prompt: [
        "You are a general travel expert that can recommend travel destinations (e.g. countries, cities, etc). ",
        "If you need hotel recommendations, ask 'hotel_advisor' for help. ",
        "You MUST include human-readable response before transferring to another agent."
      ].join("")
    });

    const callTravelAdvisor = async (
      state: z.infer<typeof MultiAgentState>
    ): Promise<Command> => {
      const response = await travelAdvisor.invoke(state);
      const update = { ...response, lastActiveAgent: "travel_advisor" };
      return new Command({ update, goto: "human" });
    };

    // Define hotel advisor tools
    const getHotelRecommendations = tool(
      async () => {
        // Placeholder implementation
        return "I recommend the Ritz-Carlton for luxury stays or boutique hotels for unique experiences.";
      },
      {
        name: "get_hotel_recommendations",
        description: "Get hotel recommendations for destinations",
        schema: z.object({}),
      }
    );

    const hotelAdvisorTools = [
      getHotelRecommendations,
      makeHandoffTool("travel_advisor"),
    ];

    const hotelAdvisor = createReactAgent({
      llm: model,
      tools: hotelAdvisorTools,
      prompt: [
        "You are a hotel expert that can provide hotel recommendations for a given destination. ",
        "If you need help picking travel destinations, ask 'travel_advisor' for help.",
        "You MUST include human-readable response before transferring to another agent."
      ].join("")
    });

    const callHotelAdvisor = async (
      state: z.infer<typeof MultiAgentState>
    ): Promise<Command> => {
      const response = await hotelAdvisor.invoke(state);
      const update = { ...response, lastActiveAgent: "hotel_advisor" };
      return new Command({ update, goto: "human" });
    };

    const humanNode = async (
      state: z.infer<typeof MultiAgentState>
    ): Promise<Command> => {
      const userInput: string = interrupt("Ready for user input.");
      const activeAgent = state.lastActiveAgent || "travel_advisor";

      return new Command({
        update: {
          messages: [
            {
              role: "human",
              content: userInput,
            }
          ]
        },
        goto: activeAgent,
      });
    };

    const builder = new StateGraph(MultiAgentState)
      .addNode("travel_advisor", callTravelAdvisor)
      .addNode("hotel_advisor", callHotelAdvisor)
      .addNode("human", humanNode)
      .addEdge(START, "travel_advisor");

    const checkpointer = new MemorySaver();
    const graph = builder.compile({ checkpointer });
    ```
    
    Let's test a multi turn conversation with this application.

    ```typescript
    import { v4 as uuidv4 } from "uuid";
    import { Command } from "@langchain/langgraph";

    const threadConfig = { configurable: { thread_id: uuidv4() } };

    const inputs = [
      // 1st round of conversation
      {
        messages: [
          { role: "user", content: "i wanna go somewhere warm in the caribbean" }
        ]
      },
      // Since we're using `interrupt`, we'll need to resume using the Command primitive.
      // 2nd round of conversation
      new Command({
        resume: "could you recommend a nice hotel in one of the areas and tell me which area it is."
      }),
      // 3rd round of conversation
      new Command({
        resume: "i like the first one. could you recommend something to do near the hotel?"
      }),
    ];

    for (const [idx, userInput] of inputs.entries()) {
      console.log();
      console.log(`--- Conversation Turn ${idx + 1} ---`);
      console.log();
      console.log(`User: ${JSON.stringify(userInput)}`);
      console.log();
      
      for await (const update of await graph.stream(
        userInput,
        { ...threadConfig, streamMode: "updates" }
      )) {
        for (const [nodeId, value] of Object.entries(update)) {
          if (value?.messages?.length) {
            const lastMessage = value.messages.at(-1);
            if (lastMessage?.getType?.() === "ai") {
              console.log(`${nodeId}: ${lastMessage.content}`);
            }
          }
        }
      }
    }
    ```
    
    ```
    --- Conversation Turn 1 ---
    
    User: {"messages":[{"role":"user","content":"i wanna go somewhere warm in the caribbean"}]}
    
    travel_advisor: Based on the recommendations, Aruba would be an excellent choice for your Caribbean getaway! Aruba is known as "One Happy Island" and offers:
    - Year-round warm weather with consistent temperatures around 82°F (28°C)
    - Beautiful white sand beaches like Eagle Beach and Palm Beach
    - Clear turquoise waters perfect for swimming and snorkeling
    - Minimal rainfall and location outside the hurricane belt
    - A blend of Caribbean and Dutch culture
    - Great dining options and nightlife
    - Various water sports and activities
    
    Would you like me to get some specific hotel recommendations in Aruba for your stay? I can transfer you to our hotel advisor who can help with accommodations.
    
    --- Conversation Turn 2 ---
    
    User: Command { resume: 'could you recommend a nice hotel in one of the areas and tell me which area it is.' }
    
    hotel_advisor: Based on the recommendations, I can suggest two excellent options:
    
    1. The Ritz-Carlton, Aruba - Located in Palm Beach
    - This luxury resort is situated in the vibrant Palm Beach area
    - Known for its exceptional service and amenities
    - Perfect if you want to be close to dining, shopping, and entertainment
    - Features multiple restaurants, a casino, and a world-class spa
    - Located on a pristine stretch of Palm Beach
    
    2. Bucuti & Tara Beach Resort - Located in Eagle Beach
    - An adults-only boutique resort on Eagle Beach
    - Known for being more intimate and peaceful
    - Award-winning for its sustainability practices
    - Perfect for a romantic getaway or peaceful vacation
    - Located on one of the most beautiful beaches in the Caribbean
    
    Would you like more specific information about either of these properties or their locations?
    
    --- Conversation Turn 3 ---
    
    User: Command { resume: 'i like the first one. could you recommend something to do near the hotel?' }
    
    travel_advisor: Near the Ritz-Carlton in Palm Beach, here are some highly recommended activities:
    
    1. Visit the Palm Beach Plaza Mall - Just a short walk from the hotel, featuring shopping, dining, and entertainment
    2. Try your luck at the Stellaris Casino - It's right in the Ritz-Carlton
    3. Take a sunset sailing cruise - Many depart from the nearby pier
    4. Visit the California Lighthouse - A scenic landmark just north of Palm Beach
    5. Enjoy water sports at Palm Beach:
       - Jet skiing
       - Parasailing
       - Snorkeling
       - Stand-up paddleboarding
    
    Would you like more specific information about any of these activities or would you like to know about other options in the area?
    ```
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
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`InjectedState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1584) (class in prebuilt)
