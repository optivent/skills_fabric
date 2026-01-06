## INVALID_CHAT_HISTORY

:::python
This error is raised in the prebuilt @[create_react_agent][create_react_agent] when the `call_model` graph node receives a malformed list of messages. Specifically, it is malformed when there are `AIMessages` with `tool_calls` (LLM requesting to call a tool) that do not have a corresponding `ToolMessage` (result of a tool invocation to return to the LLM).
:::

:::js
This error is raised in the prebuilt @[createReactAgent][create_react_agent] when the `callModel` graph node receives a malformed list of messages. Specifically, it is malformed when there are `AIMessage`s with `tool_calls` (LLM requesting to call a tool) that do not have a corresponding `ToolMessage` (result of a tool invocation to return to the LLM).
:::

There could be a few reasons you're seeing this error:

:::python

1. You manually passed a malformed list of messages when invoking the graph, e.g. `graph.invoke({'messages': [AIMessage(..., tool_calls=[...])]})`
2. The graph was interrupted before receiving updates from the `tools` node (i.e. a list of ToolMessages)
   and you invoked it with an input that is not None or a ToolMessage,
   e.g. `graph.invoke({'messages': [HumanMessage(...)]}, config)`.

   This interrupt could have been triggered in one of the following ways:

   - You manually set `interrupt_before = ['tools']` in `create_react_agent`
   - One of the tools raised an error that wasn't handled by the @[ToolNode][ToolNode] (`"tools"`)

:::

:::js

1. You manually passed a malformed list of messages when invoking the graph, e.g. `graph.invoke({messages: [new AIMessage({..., tool_calls: [...]})]})`
2. The graph was interrupted before receiving updates from the `tools` node (i.e. a list of ToolMessages)
   and you invoked it with an input that is not null or a ToolMessage,
   e.g. `graph.invoke({messages: [new HumanMessage(...)]}, config)`.

   This interrupt could have been triggered in one of the following ways:

   - You manually set `interruptBefore: ['tools']` in `createReactAgent`
   - One of the tools raised an error that wasn't handled by the @[ToolNode][ToolNode] (`"tools"`)

:::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`call_model`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6930) (function in langgraph)
- [`ToolNode`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L610) (class in prebuilt)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`list`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L174) (function in checkpoint)
