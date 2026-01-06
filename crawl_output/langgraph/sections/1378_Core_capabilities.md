## Core capabilities

These capabilities are available in both LangGraph OSS and the LangGraph Platform.

- [Streaming](../concepts/streaming.md): Stream outputs from a LangGraph graph.
- [Persistence](../concepts/persistence.md): Persist the state of a LangGraph graph.
- [Durable execution](../concepts/durable_execution.md): Save progress at key points in the graph execution.
- [Memory](../concepts/memory.md): Remember information about previous interactions.
- [Context](../agents/context.md): Pass outside data to a LangGraph graph to provide context for the graph execution.
- [Models](../agents/models.md): Integrate various LLMs into your LangGraph application.
- [Tools](../concepts/tools.md): Interface directly with external systems.
- [Human-in-the-loop](../concepts/human_in_the_loop.md): Pause a graph and wait for human input at any point in a workflow.
- [Time travel](../concepts/time-travel.md): Travel back in time to a specific point in the execution of a LangGraph graph.
- [Subgraphs](../concepts/subgraphs.md): Build modular graphs.
- [Multi-agent](../concepts/multi_agent.md): Break down a complex workflow into multiple agents.
- [MCP](../concepts/mcp.md): Use MCP servers in a LangGraph graph.
- [Evaluation](../agents/evals.md): Use LangSmith to evaluate your graph's performance.

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L387) (function in sdk-py)
- [`time`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/id.py#L61) (function in checkpoint)
