## Input format

Agent input must be a dictionary with a `messages` key. Supported formats are:

:::python
| Format | Example |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------|
| String | `{"messages": "Hello"}` — Interpreted as a [HumanMessage](https://python.langchain.com/docs/concepts/messages/#humanmessage) |
| Message dictionary | `{"messages": {"role": "user", "content": "Hello"}}` |
| List of messages | `{"messages": [{"role": "user", "content": "Hello"}]}` |
| With custom state | `{"messages": [{"role": "user", "content": "Hello"}], "user_name": "Alice"}` — If using a custom `state_schema` |
:::

:::js
| Format | Example |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------|
| String | `{"messages": "Hello"}` — Interpreted as a [HumanMessage](https://js.langchain.com/docs/concepts/messages/#humanmessage) |
| Message dictionary | `{"messages": {"role": "user", "content": "Hello"}}` |
| List of messages | `{"messages": [{"role": "user", "content": "Hello"}]}` |
| With custom state | `{"messages": [{"role": "user", "content": "Hello"}], "user_name": "Alice"}` — If using a custom state definition |
:::

:::python
Messages are automatically converted into LangChain's internal message format. You can read
more about [LangChain messages](https://python.langchain.com/docs/concepts/messages/#langchain-messages) in the LangChain documentation.
:::

:::js
Messages are automatically converted into LangChain's internal message format. You can read
more about [LangChain messages](https://js.langchain.com/docs/concepts/messages/#langchain-messages) in the LangChain documentation.
:::

!!! tip "Using custom agent state"

    :::python
    You can provide additional fields defined in your agent's state schema directly in the input dictionary. This allows dynamic behavior based on runtime data or prior tool outputs.
    See the [context guide](./context.md) for full details.
    :::

    :::js
    You can provide additional fields defined in your agent's state directly in the state definition. This allows dynamic behavior based on runtime data or prior tool outputs.
    See the [context guide](./context.md) for full details.
    :::

!!! note

    :::python
    A string input for `messages` is converted to a [HumanMessage](https://python.langchain.com/docs/concepts/messages/#humanmessage). This behavior differs from the `prompt` parameter in `create_react_agent`, which is interpreted as a [SystemMessage](https://python.langchain.com/docs/concepts/messages/#systemmessage) when passed as a string.
    :::

    :::js
    A string input for `messages` is converted to a [HumanMessage](https://js.langchain.com/docs/concepts/messages/#humanmessage). This behavior differs from the `prompt` parameter in `createReactAgent`, which is interpreted as a [SystemMessage](https://js.langchain.com/docs/concepts/messages/#systemmessage) when passed as a string.
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`prompt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L566) (function in prebuilt)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
