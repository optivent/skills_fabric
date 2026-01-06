## Next Steps

Review the `README.md` file in the root of your new LangGraph app for more information about the template and how to customize it.

After configuring the app properly and adding your API keys, you can start the app using the LangGraph CLI:

:::python

```bash
langgraph dev
```

Or via [`uv`](https://docs.astral.sh/uv/getting-started/installation/) (recommended):

```bash
uvx --from "langgraph-cli[inmem]" --with-editable . langgraph dev
```

!!! info "Missing Local Package?"

    If you are not using `uv` and run into a "`ModuleNotFoundError`" or "`ImportError`", even after installing the local package (`pip install -e .`), it is likely the case that you need to install the CLI into your local virtual environment to make the CLI "aware" of the local package. You can do this by running `python -m pip install "langgraph-cli[inmem]"` and re-activating your virtual environment before running `langgraph dev`.

:::

:::js

```bash
npx @langchain/langgraph-cli dev
```

:::

See the following guides for more information on how to deploy your app:

- **[Launch Local LangGraph Server](../tutorials/langgraph-platform/local-server.md)**: This quick start guide shows how to start a LangGraph Server locally for the **ReAct Agent** template. The steps are similar for other templates.
- **[Deploy to LangGraph Platform](../cloud/quick_start.md)**: Deploy your LangGraph app using LangGraph Platform.

### Source References

- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`NotFoundError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L120) (class in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`read`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1044) (class in sdk-py)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`cli`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L164) (function in cli)
- [`dev`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L685) (function in cli)
