## and connect it to the relevant nodes.

graph_builder.add_node("human_approval", human_approval)
graph = graph_builder.compile(checkpointer=checkpointer)

### Source References

- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`conn`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/conftest.py#L15) (function in checkpoint-postgres)
- [`checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L124) (function in langgraph)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`_build`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L295) (function in cli)
- [`build`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L310) (function in langgraph)
- [`a`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4642) (function in langgraph)
- [`A`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L124) (class in langgraph)
