## Bring your own model

If your desired LLM isn't officially supported by LangChain, consider these options:

:::python

1. **Implement a custom LangChain chat model**: Create a model conforming to the [LangChain chat model interface](https://python.langchain.com/docs/how_to/custom_chat_model/). This enables full compatibility with LangGraph's agents and workflows but requires understanding of the LangChain framework.

   :::

:::js

1. **Implement a custom LangChain chat model**: Create a model conforming to the [LangChain chat model interface](https://js.langchain.com/docs/how_to/custom_chat/). This enables full compatibility with LangGraph's agents and workflows but requires understanding of the LangChain framework.

   :::

2. **Direct invocation with custom streaming**: Use your model directly by [adding custom streaming logic](../how-tos/streaming.md#use-with-any-llm) with `StreamWriter`.
   Refer to the [custom streaming documentation](../how-tos/streaming.md#use-with-any-llm) for guidance. This approach suits custom workflows where prebuilt agent integration is not necessary.

### Source References

- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`up`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L3118) (function in langgraph)
- [`Cat`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel_async.py#L4123) (class in langgraph)
- [`a`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4642) (function in langgraph)
- [`A`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L124) (class in langgraph)
- [`B`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L128) (class in langgraph)
