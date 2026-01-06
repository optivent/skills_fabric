## ✨ Contributing Your Library

Have you built an awesome open-source library using LangGraph? We'd love to feature 
your project on the official LangGraph documentation pages! 🏆

To share your project, simply open a Pull Request adding an entry for your package in our [packages.yml](https://github.com/langchain-ai/langgraph/blob/main/docs/_scripts/third_party_page/packages.yml) file.

**Guidelines**

- Your repo must be distributed as an installable package on PyPI 📦
- The repo should either use the Graph API (exposing a `StateGraph` instance) or 
  the Functional API (exposing an `entrypoint`).
- The package must include documentation (e.g., a `README.md` or docs site) 
  explaining how to use it.

We'll review your contribution and merge it in!

Thanks for contributing! 🚀
:::

:::js
| Name | GitHub URL | Description | Weekly Downloads | Stars |
| --- | --- | --- | --- | --- |
| **@langchain/mcp-adapters** | https://github.com/langchain-ai/langchainjs | Make Anthropic Model Context Protocol (MCP) tools compatible with LangGraph agents. | -12345 | ![GitHub stars](https://img.shields.io/github/stars/langchain-ai/langchainjs?style=social)
| **@langchain/langgraph-supervisor** | https://github.com/langchain-ai/langgraphjs/tree/main/libs/langgraph-supervisor | Build supervisor multi-agent systems with LangGraph | -12345 | ![GitHub stars](https://img.shields.io/github/stars/langchain-ai/langgraphjs?style=social)
| **@langchain/langgraph-swarm** | https://github.com/langchain-ai/langgraphjs/tree/main/libs/langgraph-swarm | Build multi-agent swarms with LangGraph | -12345 | ![GitHub stars](https://img.shields.io/github/stars/langchain-ai/langgraphjs?style=social)
| **@langchain/langgraph-cua** | https://github.com/langchain-ai/langgraphjs/tree/main/libs/langgraph-cua | Build computer use agents with LangGraph | -12345 | ![GitHub stars](https://img.shields.io/github/stars/langchain-ai/langgraphjs?style=social)

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`read`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1044) (class in sdk-py)
- [`blob`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L144) (function in sdk-py)
- [`context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L387) (function in sdk-py)
