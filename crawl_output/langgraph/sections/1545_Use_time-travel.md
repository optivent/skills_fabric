## Use time-travel

To use [time-travel](../../concepts/time-travel.md) in LangGraph:

:::python

1. [Run the graph](#1-run-the-graph) with initial inputs using @[`invoke`][CompiledStateGraph.invoke] or @[`stream`][CompiledStateGraph.stream] methods.
2. [Identify a checkpoint in an existing thread](#2-identify-a-checkpoint): Use the @[`get_state_history()`][get_state_history] method to retrieve the execution history for a specific `thread_id` and locate the desired `checkpoint_id`.  
   Alternatively, set an [interrupt](../../how-tos/human_in_the_loop/add-human-in-the-loop.md) before the node(s) where you want execution to pause. You can then find the most recent checkpoint recorded up to that interrupt.
3. [Update the graph state (optional)](#3-update-the-state-optional): Use the @[`update_state`][update_state] method to modify the graph's state at the checkpoint and resume execution from alternative state.
4. [Resume execution from the checkpoint](#4-resume-execution-from-the-checkpoint): Use the `invoke` or `stream` methods with an input of `None` and a configuration containing the appropriate `thread_id` and `checkpoint_id`.
   :::

:::js

1. [Run the graph](#1-run-the-graph) with initial inputs using @[`invoke`][CompiledStateGraph.invoke] or @[`stream`][CompiledStateGraph.stream] methods.
2. [Identify a checkpoint in an existing thread](#2-identify-a-checkpoint): Use the @[`getStateHistory()`][get_state_history] method to retrieve the execution history for a specific `thread_id` and locate the desired `checkpoint_id`.  
   Alternatively, set a [breakpoint](../../concepts/breakpoints.md) before the node(s) where you want execution to pause. You can then find the most recent checkpoint recorded up to that breakpoint.
3. [Update the graph state (optional)](#3-update-the-state-optional): Use the @[`updateState`][update_state] method to modify the graph's state at the checkpoint and resume execution from alternative state.
4. [Resume execution from the checkpoint](#4-resume-execution-from-the-checkpoint): Use the `invoke` or `stream` methods with an input of `null` and a configuration containing the appropriate `thread_id` and `checkpoint_id`.
   :::

!!! tip

    For a conceptual overview of time-travel, see [Time travel](../../concepts/time-travel.md).

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`get_state`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L1235) (function in langgraph)
- [`update_state`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L2309) (function in langgraph)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
