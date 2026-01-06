## Stream multiple modes

:::python
You can specify multiple streaming modes by passing stream mode as a list: `stream_mode=["updates", "messages", "custom"]`:

=== "Sync"

    ```python
    agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=[get_weather],
    )

    for stream_mode, chunk in agent.stream(
        {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
        # highlight-next-line
        stream_mode=["updates", "messages", "custom"]
    ):
        print(chunk)
        print("\n")
    ```

=== "Async"

    ```python
    agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=[get_weather],
    )

    async for stream_mode, chunk in agent.astream(
        {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
        # highlight-next-line
        stream_mode=["updates", "messages", "custom"]
    ):
        print(chunk)
        print("\n")
    ```

:::

:::js
You can specify multiple streaming modes by passing streamMode as an array: `streamMode: ["updates", "messages", "custom"]`:

```typescript
const agent = createReactAgent({
  llm: model,
  tools: [getWeather],
});

for await (const chunk of await agent.stream(
  { messages: [{ role: "user", content: "what is the weather in sf" }] },
  { streamMode: ["updates", "messages", "custom"] }
)) {
  console.log(chunk);
  console.log("\n");
}
```

:::

### Source References

- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`get_weather`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L6455) (function in langgraph)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`list`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L174) (function in checkpoint)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
