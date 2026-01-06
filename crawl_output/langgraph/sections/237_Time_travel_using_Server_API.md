## Time travel using Server API

LangGraph provides the [**time travel**](../../concepts/time-travel.md) functionality to resume execution from a prior checkpoint, either replaying the same state or modifying it to explore alternatives. In all cases, resuming past execution produces a new fork in the history.

To time travel using the LangGraph Server API (via the LangGraph SDK):

1. **Run the graph** with initial inputs using [LangGraph SDK](https://langchain-ai.github.io/langgraph/cloud/reference/sdk/python_sdk_ref/)'s @[`client.runs.wait`][client.runs.wait] or @[`client.runs.stream`][client.runs.stream] APIs.
2. **Identify a checkpoint in an existing thread**: Use @[`client.threads.get_history`][client.threads.get_history] method to retrieve the execution history for a specific `thread_id` and locate the desired `checkpoint_id`.
   Alternatively, set a [breakpoint](./human_in_the_loop_breakpoint.md) before the node(s) where you want execution to pause. You can then find the most recent checkpoint recorded up to that breakpoint.
3. **(Optional) modify the graph state**: Use the @[`client.threads.update_state`][client.threads.update_state] method to modify the graph’s state at the checkpoint and resume execution from alternative state.
4. **Resume execution from the checkpoint**: Use the @[`client.runs.wait`][client.runs.wait] or @[`client.runs.stream`][client.runs.stream] APIs with an input of `None` and the appropriate `thread_id` and `checkpoint_id`.

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`update_state`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L2309) (function in langgraph)
- [`get_history`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel_async.py#L5975) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
