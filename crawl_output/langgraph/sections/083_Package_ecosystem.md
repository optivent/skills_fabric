## Package ecosystem

The high-level components are organized into several packages, each with a specific focus.

| Package                                    | Description                                                                              | Installation                            |
| ------------------------------------------ | ---------------------------------------------------------------------------------------- | --------------------------------------- |
| `langgraph-prebuilt` (part of `langgraph`) | Prebuilt components to [**create agents**](./agents.md)                                  | `pip install -U langgraph langchain`    |
| `langgraph-supervisor`                     | Tools for building [**supervisor**](./multi-agent.md#supervisor) agents                  | `pip install -U langgraph-supervisor`   |
| `langgraph-swarm`                          | Tools for building a [**swarm**](./multi-agent.md#swarm) multi-agent system              | `pip install -U langgraph-swarm`        |
| `langchain-mcp-adapters`                   | Interfaces to [**MCP servers**](./mcp.md) for tool and resource integration              | `pip install -U langchain-mcp-adapters` |
| `langmem`                                  | Agent memory management: [**short-term and long-term**](../how-tos/memory/add-memory.md) | `pip install -U langmem`                |
| `agentevals`                               | Utilities to [**evaluate agent performance**](./evals.md)                                | `pip install -U agentevals`             |

### Source References

- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`up`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L3118) (function in langgraph)
- [`build`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L310) (function in langgraph)
- [`a`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4642) (function in langgraph)
- [`A`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L124) (class in langgraph)
