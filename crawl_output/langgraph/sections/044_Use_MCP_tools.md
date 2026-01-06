## Use MCP tools

:::python
The `langchain-mcp-adapters` package enables agents to use tools defined across one or more MCP servers.

=== "In an agent"

    ```python title="Agent using tools defined on MCP servers"
    # highlight-next-line
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langgraph.prebuilt import create_react_agent

    # highlight-next-line
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                # Replace with absolute path to your math_server.py file
                "args": ["/path/to/math_server.py"],
                "transport": "stdio",
            },
            "weather": {
                # Ensure you start your weather server on port 8000
                "url": "http://localhost:8000/mcp",
                "transport": "streamable_http",
            }
        }
    )
    # highlight-next-line
    tools = await client.get_tools()
    agent = create_react_agent(
        "anthropic:claude-3-7-sonnet-latest",
        # highlight-next-line
        tools
    )
    math_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
    )
    weather_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
    )
    ```

=== "In a workflow"

    ```python title="Workflow using MCP tools with ToolNode"
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain.chat_models import init_chat_model
    from langgraph.graph import StateGraph, MessagesState, START, END
    from langgraph.prebuilt import ToolNode

    # Initialize the model
    model = init_chat_model("anthropic:claude-3-5-sonnet-latest")

    # Set up MCP client
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                # Make sure to update to the full absolute path to your math_server.py file
                "args": ["./examples/math_server.py"],
                "transport": "stdio",
            },
            "weather": {
                # make sure you start your weather server on port 8000
                "url": "http://localhost:8000/mcp/",
                "transport": "streamable_http",
            }
        }
    )
    tools = await client.get_tools()

    # Bind tools to model
    model_with_tools = model.bind_tools(tools)

    # Create ToolNode
    tool_node = ToolNode(tools)

    def should_continue(state: MessagesState):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    # Define call_model function
    async def call_model(state: MessagesState):
        messages = state["messages"]
        response = await model_with_tools.ainvoke(messages)
        return {"messages": [response]}

    # Build the graph
    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", tool_node)

    builder.add_edge(START, "call_model")
    builder.add_conditional_edges(
        "call_model",
        should_continue,
    )
    builder.add_edge("tools", "call_model")

    # Compile the graph
    graph = builder.compile()

    # Test the graph
    math_response = await graph.ainvoke(
        {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
    )
    weather_response = await graph.ainvoke(
        {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
    )
    ```

:::

:::js
The `@langchain/mcp-adapters` package enables agents to use tools defined across one or more MCP servers.

=== "In an agent"

    ```typescript title="Agent using tools defined on MCP servers"
    // highlight-next-line
    import { MultiServerMCPClient } from "langchain-mcp-adapters/client";
    import { ChatAnthropic } from "@langchain/langgraph/prebuilt";
    import { createReactAgent } from "@langchain/langgraph/prebuilt";

    // highlight-next-line
    const client = new MultiServerMCPClient({
      math: {
        command: "node",
        // Replace with absolute path to your math_server.js file
        args: ["/path/to/math_server.js"],
        transport: "stdio",
      },
      weather: {
        // Ensure you start your weather server on port 8000
        url: "http://localhost:8000/mcp",
        transport: "streamable_http",
      },
    });

    // highlight-next-line
    const tools = await client.getTools();
    const agent = createReactAgent({
      llm: new ChatAnthropic({ model: "claude-3-7-sonnet-latest" }),
      // highlight-next-line
      tools,
    });

    const mathResponse = await agent.invoke({
      messages: [{ role: "user", content: "what's (3 + 5) x 12?" }],
    });

    const weatherResponse = await agent.invoke({
      messages: [{ role: "user", content: "what is the weather in nyc?" }],
    });
    ```

=== "In a workflow"

    ```typescript
    import { MultiServerMCPClient } from "langchain-mcp-adapters/client";
    import { StateGraph, MessagesZodState, START } from "@langchain/langgraph";
    import { ToolNode } from "@langchain/langgraph/prebuilt";
    import { ChatOpenAI } from "@langchain/openai";
    import { AIMessage } from "@langchain/core/messages";
    import { z } from "zod";

    const model = new ChatOpenAI({ model: "gpt-4" });

    const client = new MultiServerMCPClient({
      math: {
        command: "node",
        // Make sure to update to the full absolute path to your math_server.js file
        args: ["./examples/math_server.js"],
        transport: "stdio",
      },
      weather: {
        // make sure you start your weather server on port 8000
        url: "http://localhost:8000/mcp/",
        transport: "streamable_http",
      },
    });

    const tools = await client.getTools();

    const builder = new StateGraph(MessagesZodState)
      .addNode("callModel", async (state) => {
        const response = await model.bindTools(tools).invoke(state.messages);
        return { messages: [response] };
      })
      .addNode("tools", new ToolNode(tools))
      .addEdge(START, "callModel")
      .addConditionalEdges("callModel", (state) => {
        const lastMessage = state.messages.at(-1) as AIMessage | undefined;
        if (!lastMessage?.tool_calls?.length) {
          return "__end__";
        }
        return "tools";
      })
      .addEdge("tools", "callModel");

    const graph = builder.compile();

    const mathResponse = await graph.invoke({
      messages: [{ role: "user", content: "what's (3 + 5) x 12?" }],
    });

    const weatherResponse = await graph.invoke({
      messages: [{ role: "user", content: "what is the weather in nyc?" }],
    });
    ```

:::

### Source References

- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`WeatherResponse`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1994) (class in prebuilt)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`call_model`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6930) (function in langgraph)
- [`bind_tools`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/react_agent.py#L19) (function in langgraph)
- [`ToolNode`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L610) (class in prebuilt)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`should_continue`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L3162) (function in langgraph)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
