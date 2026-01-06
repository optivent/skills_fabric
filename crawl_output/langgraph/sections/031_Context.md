## Context

**Context engineering** is the practice of building dynamic systems that provide the right information and tools, in the right format, so that an AI application can accomplish a task. Context can be characterized along two key dimensions:

1. By **mutability**:
    - **Static context**: Immutable data that doesn't change during execution (e.g., user metadata, database connections, tools)
    - **Dynamic context**: Mutable data that evolves as the application runs (e.g., conversation history, intermediate results, tool call observations)
2. By **lifetime**:
    - **Runtime context**: Data scoped to a single run or invocation
    - **Cross-conversation context**: Data that persists across multiple conversations or sessions

!!! tip "Runtime context vs LLM context"

    Runtime context refers to local context: data and dependencies your code needs to run. It does **not** refer to:

    * The LLM context, which is the data passed into the LLM's prompt.
    * The "context window", which is the maximum number of tokens that can be passed to the LLM.

    Runtime context can be used to optimize the LLM context. For example, you can use user metadata
    in the runtime context to fetch user preferences and feed them into the context window.

LangGraph provides three ways to manage context, which combines the mutability and lifetime dimensions:

:::python

| Context type                                                                                | Description                                            | Mutability | Lifetime           | Access method                           |
| ------------------------------------------------------------------------------------------- | ------------------------------------------------------ | ---------- | ------------------ | --------------------------------------- |
| [**Static runtime context**](#static-runtime-context)                                       | User metadata, tools, db connections passed at startup | Static     | Single run         | `context` argument to `invoke`/`stream` |
| [**Dynamic runtime context (state)**](#dynamic-runtime-context-state)                       | Mutable data that evolves during a single run          | Dynamic    | Single run         | LangGraph state object                  |
| [**Dynamic cross-conversation context (store)**](#dynamic-cross-conversation-context-store) | Persistent data shared across conversations            | Dynamic    | Cross-conversation | LangGraph store                         |

### Source References

- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`prompt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L566) (function in prebuilt)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`store`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/test_store.py#L34) (function in checkpoint-postgres)
- [`context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L387) (function in sdk-py)
- [`conn`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/conftest.py#L15) (function in checkpoint-postgres)
