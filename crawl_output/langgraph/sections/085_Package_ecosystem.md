## Package ecosystem

The high-level components are organized into several packages, each with a specific focus.

| Package                  | Description                                                                 | Installation                                       |
| ------------------------ | --------------------------------------------------------------------------- | -------------------------------------------------- |
| `langgraph`              | Prebuilt components to [**create agents**](./agents.md)                     | `npm install @langchain/langgraph @langchain/core` |
| `langgraph-supervisor`   | Tools for building [**supervisor**](./multi-agent.md#supervisor) agents     | `npm install @langchain/langgraph-supervisor`      |
| `langgraph-swarm`        | Tools for building a [**swarm**](./multi-agent.md#swarm) multi-agent system | `npm install @langchain/langgraph-swarm`           |
| `langchain-mcp-adapters` | Interfaces to [**MCP servers**](./mcp.md) for tool and resource integration | `npm install @langchain/mcp-adapters`              |
| `agentevals`             | Utilities to [**evaluate agent performance**](./evals.md)                   | `npm install agentevals`                           |

### Source References

- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`up`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L3118) (function in langgraph)
- [`build`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L310) (function in langgraph)
- [`a`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4642) (function in langgraph)
- [`A`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L124) (class in langgraph)
- [`B`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L128) (class in langgraph)
