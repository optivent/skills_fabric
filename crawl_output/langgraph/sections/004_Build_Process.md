## Build Process

Docs are built following these steps:

1. **Content Processing:**
   - `_scripts/notebook_hooks.py` - Main processing pipeline that:
     - Converts how-tos/tutorial Jupyter notebooks to markdown using `notebook_convert.py`
     - Adds automatic API reference links to code blocks using `generate_api_reference_links.py`
     - Handles conditional rendering for Python/JS versions
     - Processes highlight comments and custom syntax

2. **API Reference Generation:**
   - **mkdocstrings** plugin extracts docstrings from Python source code
   - Manual `::: module.Class` directives in reference pages (`/docs/docs/*`) specify what to document
   - Cross-references are automatically generated between docs and API

3. **Site Generation:**
   - **MkDocs** processes all markdown files and generates static HTML
   - Custom hooks handle redirects and inject additional functionality

4. **Deployment:**
   - Site is deployed with Vercel
   - `make build-docs` generates production build (also usable for local testing)
   - Automatic redirects handle URL changes between versions

### Source References

- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`main`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6527) (function in langgraph)
- [`up`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L3118) (function in langgraph)
- [`build`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L310) (function in langgraph)
- [`Version`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/docker.py#L16) (class in cli)
- [`func`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_utils.py#L37) (function in langgraph)
