## 1. Add resource authorization

:::python
Recall that in the last tutorial, the [`Auth`](../../cloud/reference/sdk/python_sdk_ref.md#langgraph_sdk.auth.Auth) object lets you register an [authentication function](../../concepts/auth.md#authentication), which LangGraph Platform uses to validate the bearer tokens in incoming requests. Now you'll use it to register an **authorization** handler.
:::

:::js
Recall that in the last tutorial, the @[`Auth`][Auth] object lets you register an [authentication function](../../concepts/auth.md#authentication), which LangGraph Platform uses to validate the bearer tokens in incoming requests. Now you'll use it to register an **authorization** handler.
:::

Authorization handlers are functions that run **after** authentication succeeds. These handlers can add [metadata](../../concepts/auth.md#filter-operations) to resources (like who owns them) and filter what each user can see.

:::python
Update your `src/security/auth.py` and add one authorization handler to run on every request:

```python hl_lines="29-39" title="src/security/auth.py"
from langgraph_sdk import Auth

### Source References

- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`Handler`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L446) (class in prebuilt)
- [`handler`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_client_stream.py#L234) (function in sdk-py)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`Auth`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/__init__.py#L13) (class in sdk-py)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
