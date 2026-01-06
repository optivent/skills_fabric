## Custom error messages

Provide a custom error message by setting the error handling parameter to a string:

:::python

```python
tool_node = ToolNode(
    [multiply],
    handle_tool_errors="Can't use 42 as the first operand, please switch operands!"
)
```

Example output:

```python
{'messages': [
    ToolMessage(
        content="Can't use 42 as the first operand, please switch operands!",
        name='multiply',
        tool_call_id='tool_call_id',
        status='error'
    )
]}
```

:::

:::js

```typescript
const toolNode = new ToolNode([multiply], {
  handleToolErrors:
    "Can't use 42 as the first operand, please switch operands!",
});
```

Example output:

```typescript
{ messages: [
  ToolMessage {
    content: "Can't use 42 as the first operand, please switch operands!",
    name: "multiply",
    tool_call_id: "tool_call_id",
    status: "error"
  }
]}
```

:::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`multiply`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6341) (function in langgraph)
- [`ToolNode`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L610) (class in prebuilt)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`set`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L84) (function in checkpoint)
- [`new`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L779) (function in cli)
- [`a`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4642) (function in langgraph)
