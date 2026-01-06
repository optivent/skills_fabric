## Max iterations

:::python
To control agent execution and avoid infinite loops, set a recursion limit. This defines the maximum number of steps the agent can take before raising a `GraphRecursionError`. You can configure `recursion_limit` at runtime or when defining agent via `.with_config()`:
:::

:::js
To control agent execution and avoid infinite loops, set a recursion limit. This defines the maximum number of steps the agent can take before raising a `GraphRecursionError`. You can configure `recursionLimit` at runtime or when defining agent via `.withConfig()`:
:::

:::python
=== "Runtime"

    ```python
    from langgraph.errors import GraphRecursionError
    from langgraph.prebuilt import create_react_agent

    max_iterations = 3
    # highlight-next-line
    recursion_limit = 2 * max_iterations + 1
    agent = create_react_agent(
        model="anthropic:claude-3-5-haiku-latest",
        tools=[get_weather]
    )

    try:
        response = agent.invoke(
            {"messages": [{"role": "user", "content": "what's the weather in sf"}]},
            # highlight-next-line
            {"recursion_limit": recursion_limit},
        )
    except GraphRecursionError:
        print("Agent stopped due to max iterations.")
    ```

=== "`.with_config()`"

    ```python
    from langgraph.errors import GraphRecursionError
    from langgraph.prebuilt import create_react_agent

    max_iterations = 3
    # highlight-next-line
    recursion_limit = 2 * max_iterations + 1
    agent = create_react_agent(
        model="anthropic:claude-3-5-haiku-latest",
        tools=[get_weather]
    )
    # highlight-next-line
    agent_with_recursion_limit = agent.with_config(recursion_limit=recursion_limit)

    try:
        response = agent_with_recursion_limit.invoke(
            {"messages": [{"role": "user", "content": "what's the weather in sf"}]},
        )
    except GraphRecursionError:
        print("Agent stopped due to max iterations.")
    ```

:::

:::js
=== "Runtime"

    ```typescript
    import { GraphRecursionError } from "@langchain/langgraph";
    import { ChatAnthropic } from "@langchain/langgraph/prebuilt";
    import { createReactAgent } from "@langchain/langgraph/prebuilt";

    const maxIterations = 3;
    // highlight-next-line
    const recursionLimit = 2 * maxIterations + 1;
    const agent = createReactAgent({
        llm: new ChatAnthropic({ model: "claude-3-5-haiku-latest" }),
        tools: [getWeather]
    });

    try {
        const response = await agent.invoke(
            {"messages": [{"role": "user", "content": "what's the weather in sf"}]},
            // highlight-next-line
            { recursionLimit }
        );
    } catch (error) {
        if (error instanceof GraphRecursionError) {
            console.log("Agent stopped due to max iterations.");
        }
    }
    ```

=== "`.withConfig()`"

    ```typescript
    import { GraphRecursionError } from "@langchain/langgraph";
    import { ChatAnthropic } from "@langchain/langgraph/prebuilt";
    import { createReactAgent } from "@langchain/langgraph/prebuilt";

    const maxIterations = 3;
    // highlight-next-line
    const recursionLimit = 2 * maxIterations + 1;
    const agent = createReactAgent({
        llm: new ChatAnthropic({ model: "claude-3-5-haiku-latest" }),
        tools: [getWeather]
    });
    // highlight-next-line
    const agentWithRecursionLimit = agent.withConfig({ recursionLimit });

    try {
        const response = await agentWithRecursionLimit.invoke(
            {"messages": [{"role": "user", "content": "what's the weather in sf"}]},
        );
    } catch (error) {
        if (error instanceof GraphRecursionError) {
            console.log("Agent stopped due to max iterations.");
        }
    }
    ```

:::

:::python

### Source References

- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`get_weather`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L6455) (function in langgraph)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`set`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L84) (function in checkpoint)
