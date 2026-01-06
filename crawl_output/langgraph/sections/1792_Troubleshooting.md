## Troubleshooting

To resolve this, you can do one of the following:

1. Don't invoke the graph with a malformed list of messages
2. In case of an interrupt (manual or due to an error) you can:

:::python

- provide ToolMessages that match existing tool calls and call `graph.invoke({'messages': [ToolMessage(...)]})`.
  **NOTE**: this will append the messages to the history and run the graph from the START node.

  - manually update the state and resume the graph from the interrupt:

          1. get the list of most recent messages from the graph state with `graph.get_state(config)`
          2. modify the list of messages to either remove unanswered tool calls from AIMessages

or add ToolMessages with tool_call_ids that match unanswered tool calls 3. call `graph.update_state(config, {'messages': ...})` with the modified list of messages 4. resume the graph, e.g. call `graph.invoke(None, config)`
:::

:::js

- provide ToolMessages that match existing tool calls and call `graph.invoke({messages: [new ToolMessage(...)]})`.
  **NOTE**: this will append the messages to the history and run the graph from the START node.

  - manually update the state and resume the graph from the interrupt:

          1. get the list of most recent messages from the graph state with `graph.getState(config)`
          2. modify the list of messages to either remove unanswered tool calls from AIMessages

or add ToolMessages with `toolCallId`s that match unanswered tool calls 3. call `graph.updateState(config, {messages: ...})` with the modified list of messages 4. resume the graph, e.g. call `graph.invoke(null, config)`
:::

### Source References

- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`get_state`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L1235) (function in langgraph)
- [`update_state`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L2309) (function in langgraph)
- [`list`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L174) (function in checkpoint)
- [`Interrupt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L157) (class in langgraph)
