## Using `llms-full.txt`

The LangGraph `llms-full.txt` file typically contains several hundred thousand tokens, exceeding the context window limitations of most LLMs. To effectively use this file:

1. **With IDEs (e.g., Cursor, Windsurf)**:
    - Add the `llms-full.txt` as custom documentation. The IDE will automatically chunk and index the content, implementing Retrieval-Augmented Generation (RAG).

2. **Without IDE support**:
    - Use a chat model with a large context window.
    - Implement a RAG strategy to manage and query the documentation efficiently.

### Source References

- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L387) (function in sdk-py)
- [`cursor`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/__init__.py#L162) (function in checkpoint-sqlite)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`up`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L3118) (function in langgraph)
- [`a`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4642) (function in langgraph)
- [`A`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L124) (class in langgraph)
- [`gen`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_utils.py#L71) (function in langgraph)
