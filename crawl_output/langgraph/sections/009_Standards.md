## Standards

**Docstring Format:**
The API reference uses **Google-style docstrings** with Markdown markup. The `mkdocstrings` plugin processes these to generate documentation.

**Required format:**

```python
def example_function(param1: str, param2: int = 5) -> bool:
    """Brief description of the function.

    Longer description can go here. Use Markdown syntax for
    rich formatting like **bold** and *italic*.

    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter with default value.

    Returns:
        Description of the return value.

    Raises:
        ValueError: When param1 is empty.
        TypeError: When param2 is not an integer.

    !!! warning
        This function is experimental and may change.

    !!! version-added "Added in version 0.2.0"
    """
```

**Special Markers:**

- **MkDocs admonitions**: `!!! warning`, `!!! note`, `!!! version-added`
- **Code blocks**: Standard markdown ``` syntax
- **Cross-references**: Automatic linking via `generate_api_reference_links.py`

### Source References

- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`_func`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_validator.py#L184) (function in prebuilt)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`up`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L3118) (function in langgraph)
- [`Version`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/docker.py#L16) (class in cli)
- [`func`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_utils.py#L37) (function in langgraph)
- [`a`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4642) (function in langgraph)
- [`A`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L124) (class in langgraph)
- [`B`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L128) (class in langgraph)
- [`b`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4645) (function in langgraph)
