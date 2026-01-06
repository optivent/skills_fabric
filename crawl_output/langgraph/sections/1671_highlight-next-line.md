## highlight-next-line

tool_node = ToolNode([get_weather, get_coolest_cities])
tool_node.invoke({"messages": [...]})
```

:::

:::js
To execute tools in custom workflows, use the prebuilt [`ToolNode`](https://js.langchain.com/docs/api/langgraph_prebuilt/classes/ToolNode.html) or implement your own custom node.

`ToolNode` is a specialized node for executing tools in a workflow. It provides the following features:

- Supports both synchronous and asynchronous tools.
- Executes multiple tools concurrently.
- Handles errors during tool execution (`handleToolErrors: true`, enabled by default). See [handling tool errors](#handle-errors) for more details.

- **Input**: `MessagesZodState`, where the last message is an `AIMessage` containing the `tool_calls` parameter.
- **Output**: `MessagesZodState` updated with the resulting [`ToolMessage`](https://js.langchain.com/docs/concepts/messages/#toolmessage) from executed tools.

```typescript
// highlight-next-line
import { ToolNode } from "@langchain/langgraph/prebuilt";

const getWeather = tool(
  (input) => {
    if (["sf", "san francisco"].includes(input.location.toLowerCase())) {
      return "It's 60 degrees and foggy.";
    } else {
      return "It's 90 degrees and sunny.";
    }
  },
  {
    name: "get_weather",
    description: "Call to get the current weather.",
    schema: z.object({
      location: z.string().describe("Location to get the weather for."),
    }),
  }
);

const getCoolestCities = tool(
  () => {
    return "nyc, sf";
  },
  {
    name: "get_coolest_cities",
    description: "Get a list of coolest cities",
    schema: z.object({
      noOp: z.string().optional().describe("No-op parameter."),
    }),
  }
);

// highlight-next-line
const toolNode = new ToolNode([getWeather, getCoolestCities]);
await toolNode.invoke({ messages: [...] });
```

:::

??? example "Single tool call"

    :::python
    ```python
    from langchain_core.messages import AIMessage
    from langgraph.prebuilt import ToolNode

    # Define tools
    @tool
    def get_weather(location: str):
        """Call to get the current weather."""
        if location.lower() in ["sf", "san francisco"]:
            return "It's 60 degrees and foggy."
        else:
            return "It's 90 degrees and sunny."

    # highlight-next-line
    tool_node = ToolNode([get_weather])

    message_with_single_tool_call = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "get_weather",
                "args": {"location": "sf"},
                "id": "tool_call_id",
                "type": "tool_call",
            }
        ],
    )

    tool_node.invoke({"messages": [message_with_single_tool_call]})
    ```

    ```
    {'messages': [ToolMessage(content="It's 60 degrees and foggy.", name='get_weather', tool_call_id='tool_call_id')]}
    ```
    :::

    :::js
    ```typescript
    import { AIMessage } from "@langchain/core/messages";
    import { ToolNode } from "@langchain/langgraph/prebuilt";
    import { tool } from "@langchain/core/tools";
    import { z } from "zod";

    // Define tools
    const getWeather = tool(
      (input) => {
        if (["sf", "san francisco"].includes(input.location.toLowerCase())) {
          return "It's 60 degrees and foggy.";
        } else {
          return "It's 90 degrees and sunny.";
        }
      },
      {
        name: "get_weather",
        description: "Call to get the current weather.",
        schema: z.object({
          location: z.string().describe("Location to get the weather for."),
        }),
      }
    );

    // highlight-next-line
    const toolNode = new ToolNode([getWeather]);

    const messageWithSingleToolCall = new AIMessage({
      content: "",
      tool_calls: [
        {
          name: "get_weather",
          args: { location: "sf" },
          id: "tool_call_id",
          type: "tool_call",
        }
      ],
    });

    await toolNode.invoke({ messages: [messageWithSingleToolCall] });
    ```

    ```
    { messages: [ToolMessage { content: "It's 60 degrees and foggy.", name: "get_weather", tool_call_id: "tool_call_id" }] }
    ```
    :::

??? example "Multiple tool calls"

    :::python
    ```python
    from langchain_core.messages import AIMessage
    from langgraph.prebuilt import ToolNode

    # Define tools

    def get_weather(location: str):
        """Call to get the current weather."""
        if location.lower() in ["sf", "san francisco"]:
            return "It's 60 degrees and foggy."
        else:
            return "It's 90 degrees and sunny."

    def get_coolest_cities():
        """Get a list of coolest cities"""
        return "nyc, sf"

    # highlight-next-line
    tool_node = ToolNode([get_weather, get_coolest_cities])

    message_with_multiple_tool_calls = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "get_coolest_cities",
                "args": {},
                "id": "tool_call_id_1",
                "type": "tool_call",
            },
            {
                "name": "get_weather",
                "args": {"location": "sf"},
                "id": "tool_call_id_2",
                "type": "tool_call",
            },
        ],
    )

    # highlight-next-line
    tool_node.invoke({"messages": [message_with_multiple_tool_calls]})  # (1)!
    ```

    1. `ToolNode` will execute both tools in parallel

    ```
    {
        'messages': [
            ToolMessage(content='nyc, sf', name='get_coolest_cities', tool_call_id='tool_call_id_1'),
            ToolMessage(content="It's 60 degrees and foggy.", name='get_weather', tool_call_id='tool_call_id_2')
        ]
    }
    ```
    :::

    :::js
    ```typescript
    import { AIMessage } from "@langchain/core/messages";
    import { ToolNode } from "@langchain/langgraph/prebuilt";
    import { tool } from "@langchain/core/tools";
    import { z } from "zod";

    // Define tools
    const getWeather = tool(
      (input) => {
        if (["sf", "san francisco"].includes(input.location.toLowerCase())) {
          return "It's 60 degrees and foggy.";
        } else {
          return "It's 90 degrees and sunny.";
        }
      },
      {
        name: "get_weather",
        description: "Call to get the current weather.",
        schema: z.object({
          location: z.string().describe("Location to get the weather for."),
        }),
      }
    );

    const getCoolestCities = tool(
      () => {
        return "nyc, sf";
      },
      {
        name: "get_coolest_cities",
        description: "Get a list of coolest cities",
        schema: z.object({
          noOp: z.string().optional().describe("No-op parameter."),
        }),
      }
    );

    // highlight-next-line
    const toolNode = new ToolNode([getWeather, getCoolestCities]);

    const messageWithMultipleToolCalls = new AIMessage({
      content: "",
      tool_calls: [
        {
          name: "get_coolest_cities",
          args: {},
          id: "tool_call_id_1",
          type: "tool_call",
        },
        {
          name: "get_weather",
          args: { location: "sf" },
          id: "tool_call_id_2",
          type: "tool_call",
        },
      ],
    });

    // highlight-next-line
    await toolNode.invoke({ messages: [messageWithMultipleToolCalls] }); // (1)!
    ```

    1. `ToolNode` will execute both tools in parallel

    ```
    {
      messages: [
        ToolMessage { content: "nyc, sf", name: "get_coolest_cities", tool_call_id: "tool_call_id_1" },
        ToolMessage { content: "It's 60 degrees and foggy.", name: "get_weather", tool_call_id: "tool_call_id_2" }
      ]
    }
    ```
    :::

??? example "Use with a chat model"

    :::python
    ```python
    from langchain.chat_models import init_chat_model
    from langgraph.prebuilt import ToolNode

    def get_weather(location: str):
        """Call to get the current weather."""
        if location.lower() in ["sf", "san francisco"]:
            return "It's 60 degrees and foggy."
        else:
            return "It's 90 degrees and sunny."

    # highlight-next-line
    tool_node = ToolNode([get_weather])

    model = init_chat_model(model="claude-3-5-haiku-latest")
    # highlight-next-line
    model_with_tools = model.bind_tools([get_weather])  # (1)!


    # highlight-next-line
    response_message = model_with_tools.invoke("what's the weather in sf?")
    tool_node.invoke({"messages": [response_message]})
    ```

    1. Use `.bind_tools()` to attach the tool schema to the chat model

    ```
    {'messages': [ToolMessage(content="It's 60 degrees and foggy.", name='get_weather', tool_call_id='toolu_01Pnkgw5JeTRxXAU7tyHT4UW')]}
    ```
    :::

    :::js
    ```typescript
    import { ChatOpenAI } from "@langchain/openai";
    import { ToolNode } from "@langchain/langgraph/prebuilt";
    import { tool } from "@langchain/core/tools";
    import { z } from "zod";

    const getWeather = tool(
      (input) => {
        if (["sf", "san francisco"].includes(input.location.toLowerCase())) {
          return "It's 60 degrees and foggy.";
        } else {
          return "It's 90 degrees and sunny.";
        }
      },
      {
        name: "get_weather",
        description: "Call to get the current weather.",
        schema: z.object({
          location: z.string().describe("Location to get the weather for."),
        }),
      }
    );

    // highlight-next-line
    const toolNode = new ToolNode([getWeather]);

    const model = new ChatOpenAI({ model: "gpt-4o" });
    // highlight-next-line
    const modelWithTools = model.bindTools([getWeather]); // (1)!

    // highlight-next-line
    const responseMessage = await modelWithTools.invoke("what's the weather in sf?");
    await toolNode.invoke({ messages: [responseMessage] });
    ```

    1. Use `.bindTools()` to attach the tool schema to the chat model

    ```
    { messages: [ToolMessage { content: "It's 60 degrees and foggy.", name: "get_weather", tool_call_id: "toolu_01Pnkgw5JeTRxXAU7tyHT4UW" }] }
    ```
    :::

??? example "Use in a tool-calling agent"

    This is an example of creating a tool-calling agent from scratch using `ToolNode`. You can also use LangGraph's prebuilt [agent](../agents/agents.md).

    :::python
    ```python
    from langchain.chat_models import init_chat_model
    from langgraph.prebuilt import ToolNode
    from langgraph.graph import StateGraph, MessagesState, START, END

    def get_weather(location: str):
        """Call to get the current weather."""
        if location.lower() in ["sf", "san francisco"]:
            return "It's 60 degrees and foggy."
        else:
            return "It's 90 degrees and sunny."

    # highlight-next-line
    tool_node = ToolNode([get_weather])

    model = init_chat_model(model="claude-3-5-haiku-latest")
    # highlight-next-line
    model_with_tools = model.bind_tools([get_weather])

    def should_continue(state: MessagesState):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    def call_model(state: MessagesState):
        messages = state["messages"]
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)

    # Define the two nodes we will cycle between
    builder.add_node("call_model", call_model)
    # highlight-next-line
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", should_continue, ["tools", END])
    builder.add_edge("tools", "call_model")

    graph = builder.compile()

    graph.invoke({"messages": [{"role": "user", "content": "what's the weather in sf?"}]})
    ```

    ```
    {
        'messages': [
            HumanMessage(content="what's the weather in sf?"),
            AIMessage(
                content=[{'text': "I'll help you check the weather in San Francisco right now.", 'type': 'text'}, {'id': 'toolu_01A4vwUEgBKxfFVc5H3v1CNs', 'input': {'location': 'San Francisco'}, 'name': 'get_weather', 'type': 'tool_use'}],
                tool_calls=[{'name': 'get_weather', 'args': {'location': 'San Francisco'}, 'id': 'toolu_01A4vwUEgBKxfFVc5H3v1CNs', 'type': 'tool_call'}]
            ),
            ToolMessage(content="It's 60 degrees and foggy."),
            AIMessage(content="The current weather in San Francisco is 60 degrees and foggy. Typical San Francisco weather with its famous marine layer!")
        ]
    }
    ```
    :::

    :::js
    ```typescript
    import { ChatOpenAI } from "@langchain/openai";
    import { ToolNode } from "@langchain/langgraph/prebuilt";
    import { StateGraph, MessagesZodState, START, END } from "@langchain/langgraph";
    import { tool } from "@langchain/core/tools";
    import { z } from "zod";
    import { isAIMessage } from "@langchain/core/messages";

    const getWeather = tool(
      (input) => {
        if (["sf", "san francisco"].includes(input.location.toLowerCase())) {
          return "It's 60 degrees and foggy.";
        } else {
          return "It's 90 degrees and sunny.";
        }
      },
      {
        name: "get_weather",
        description: "Call to get the current weather.",
        schema: z.object({
          location: z.string().describe("Location to get the weather for."),
        }),
      }
    );

    // highlight-next-line
    const toolNode = new ToolNode([getWeather]);

    const model = new ChatOpenAI({ model: "gpt-4o" });
    // highlight-next-line
    const modelWithTools = model.bindTools([getWeather]);

    const shouldContinue = (state: z.infer<typeof MessagesZodState>) => {
      const messages = state.messages;
      const lastMessage = messages.at(-1);
      if (lastMessage && isAIMessage(lastMessage) && lastMessage.tool_calls?.length) {
        return "tools";
      }
      return END;
    };

    const callModel = async (state: z.infer<typeof MessagesZodState>) => {
      const messages = state.messages;
      const response = await modelWithTools.invoke(messages);
      return { messages: [response] };
    };

    const builder = new StateGraph(MessagesZodState)
      // Define the two nodes we will cycle between
      .addNode("agent", callModel)
      // highlight-next-line
      .addNode("tools", toolNode)
      .addEdge(START, "agent")
      .addConditionalEdges("agent", shouldContinue, ["tools", END])
      .addEdge("tools", "agent");

    const graph = builder.compile();

    await graph.invoke({
      messages: [{ role: "user", content: "what's the weather in sf?" }]
    });
    ```

    ```
    {
      messages: [
        HumanMessage { content: "what's the weather in sf?" },
        AIMessage {
          content: [{ text: "I'll help you check the weather in San Francisco right now.", type: "text" }, { id: "toolu_01A4vwUEgBKxfFVc5H3v1CNs", input: { location: "San Francisco" }, name: "get_weather", type: "tool_use" }],
          tool_calls: [{ name: "get_weather", args: { location: "San Francisco" }, id: "toolu_01A4vwUEgBKxfFVc5H3v1CNs", type: "tool_call" }]
        },
        ToolMessage { content: "It's 60 degrees and foggy." },
        AIMessage { content: "The current weather in San Francisco is 60 degrees and foggy. Typical San Francisco weather with its famous marine layer!" }
      ]
    }
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`get_weather`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L6455) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`call_model`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6930) (function in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`bind_tools`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/react_agent.py#L19) (function in langgraph)
- [`ToolNode`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L610) (class in prebuilt)
