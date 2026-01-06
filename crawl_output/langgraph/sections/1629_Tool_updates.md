## Tool updates

:::python
To stream updates from tools as they are executed, you can use @[get_stream_writer][get_stream_writer].

=== "Sync"

    ```python
    # highlight-next-line
    from langgraph.config import get_stream_writer

    def get_weather(city: str) -> str:
        """Get weather for a given city."""
        # highlight-next-line
        writer = get_stream_writer()
        # stream any arbitrary data
        # highlight-next-line
        writer(f"Looking up data for city: {city}")
        return f"It's always sunny in {city}!"

    agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=[get_weather],
    )

    for chunk in agent.stream(
        {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
        # highlight-next-line
        stream_mode="custom"
    ):
        print(chunk)
        print("\n")
    ```

=== "Async"

    ```python
    # highlight-next-line
    from langgraph.config import get_stream_writer

    def get_weather(city: str) -> str:
        """Get weather for a given city."""
        # highlight-next-line
        writer = get_stream_writer()
        # stream any arbitrary data
        # highlight-next-line
        writer(f"Looking up data for city: {city}")
        return f"It's always sunny in {city}!"

    agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=[get_weather],
    )

    async for chunk in agent.astream(
        {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
        # highlight-next-line
        stream_mode="custom"
    ):
        print(chunk)
        print("\n")
    ```

!!! Note

      If you add `get_stream_writer` inside your tool, you won't be able to invoke the tool outside of a LangGraph execution context.

:::

:::js
To stream updates from tools as they are executed, you can use the `writer` parameter from the configuration.

```typescript
import { LangGraphRunnableConfig } from "@langchain/langgraph";

const getWeather = tool(
  async (input, config: LangGraphRunnableConfig) => {
    // Stream any arbitrary data
    config.writer?.("Looking up data for city: " + input.city);
    return `It's always sunny in ${input.city}!`;
  },
  {
    name: "get_weather",
    description: "Get weather for a given city.",
    schema: z.object({
      city: z.string().describe("The city to get weather for."),
    }),
  }
);

const agent = createReactAgent({
  llm: model,
  tools: [getWeather],
});

for await (const chunk of await agent.stream(
  { messages: [{ role: "user", content: "what is the weather in sf" }] },
  { streamMode: "custom" }
)) {
  console.log(chunk);
  console.log("\n");
}
```

!!! Note
      If you add the `writer` parameter to your tool, you won't be able to invoke the tool outside of a LangGraph execution context without providing a writer function.
:::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`get_weather`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L6455) (function in langgraph)
- [`execute`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1174) (function in prebuilt)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
