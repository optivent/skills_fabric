## Key features

LangGraph includes several capabilities essential for building robust, production-ready agentic systems:

- [**Memory integration**](../how-tos/memory/add-memory.md): Native support for _short-term_ (session-based) and _long-term_ (persistent across sessions) memory, enabling stateful behaviors in chatbots and assistants.
- [**Human-in-the-loop control**](../concepts/human_in_the_loop.md): Execution can pause _indefinitely_ to await human feedback—unlike websocket-based solutions limited to real-time interaction. This enables asynchronous approval, correction, or intervention at any point in the workflow.
- [**Streaming support**](../how-tos/streaming.md): Real-time streaming of agent state, model tokens, tool outputs, or combined streams.
- [**Deployment tooling**](../tutorials/langgraph-platform/local-server.md): Includes infrastructure-free deployment tools. [**LangGraph Platform**](https://langchain-ai.github.io/langgraph/concepts/langgraph_platform/) supports testing, debugging, and deployment.
  - **[Studio](https://langchain-ai.github.io/langgraph/concepts/langgraph_studio/)**: A visual IDE for inspecting and debugging workflows.
  - Supports multiple [**deployment options**](https://langchain-ai.github.io/langgraph/concepts/deployment_options.md) for production.

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Assistant`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L242) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`assistants`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L998) (class in sdk-py)
