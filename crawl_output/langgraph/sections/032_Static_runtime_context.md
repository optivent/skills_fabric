## Static runtime context

**Static runtime context** represents immutable data like user metadata, tools, and database connections that are passed to an application at the start of a run via the `context` argument to `invoke`/`stream`. This data does not change during execution.

!!! version-added "Added in version 0.6.0: `context` replaces `config['configurable']`"

    Runtime context is now passed to the `context` argument of `invoke`/`stream`,
    which replaces the previous pattern of passing application configuration to `config['configurable']`.

```python
@dataclass
class ContextSchema:
    user_name: str

graph.invoke( # (1)!
    {"messages": [{"role": "user", "content": "hi!"}]}, # (2)!
    # highlight-next-line
    context={"user_name": "John Smith"} # (3)!
)
```

1. This is the invocation of the agent or graph. The `invoke` method runs the underlying graph with the provided input.
2. This example uses messages as an input, which is common, but your application may use different input structures.
3. This is where you pass the runtime data. The `context` parameter allows you to provide additional dependencies that the agent can use during its execution.

=== "Agent prompt"

    ```python
    from langchain_core.messages import AnyMessage
    from langgraph.runtime import get_runtime
    from langgraph.prebuilt.chat_agent_executor import AgentState
    from langgraph.prebuilt import create_react_agent

    # highlight-next-line
    def prompt(state: AgentState) -> list[AnyMessage]:
        runtime = get_runtime(ContextSchema)
        system_msg = f"You are a helpful assistant. Address the user as {runtime.context.user_name}."
        return [{"role": "system", "content": system_msg}] + state["messages"]

    agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=[get_weather],
        prompt=prompt,
        context_schema=ContextSchema
    )

    agent.invoke(
        {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
        # highlight-next-line
        context={"user_name": "John Smith"}
    )
    ```

    * See [Agents](../agents/agents.md) for details.

=== "Workflow node"

    ```python
    from langgraph.runtime import Runtime

    # highlight-next-line
    def node(state: State, runtime: Runtime[ContextSchema]):
        user_name = runtime.context.user_name
        ...
    ```

    * See [the Graph API](https://langchain-ai.github.io/langgraph/how-tos/graph-api/#add-runtime-configuration) for details.

=== "In a tool"

    ```python
    from langgraph.runtime import get_runtime

    @tool
    # highlight-next-line
    def get_user_email() -> str:
        """Retrieve user information based on user ID."""
        # simulate fetching user info from a database
        runtime = get_runtime(ContextSchema)
        email = get_user_email_from_db(runtime.context.user_name)
        return email
    ```

    See the [tool calling guide](../how-tos/tool-calling.md#configuration) for details.

!!! tip

    The `Runtime` object can be used to access static context and other utilities like the active store and stream writer.
    See the [Runtime][langgraph.runtime.Runtime] documentation for details.

:::

:::js

| Context type                                                                                | Description                                   | Mutability | Lifetime           |
| ------------------------------------------------------------------------------------------- | --------------------------------------------- | ---------- | ------------------ |
| [**Config**](#config-static-context)                                                        | data passed at the start of a run             | Static     | Single run         |
| [**Dynamic runtime context (state)**](#dynamic-runtime-context-state)                       | Mutable data that evolves during a single run | Dynamic    | Single run         |
| [**Dynamic cross-conversation context (store)**](#dynamic-cross-conversation-context-store) | Persistent data shared across conversations   | Dynamic    | Cross-conversation |

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`prompt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L566) (function in prebuilt)
- [`get_weather`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L6455) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`_run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/batch.py#L326) (function in checkpoint)
