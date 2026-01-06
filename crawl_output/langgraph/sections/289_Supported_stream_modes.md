## Supported stream modes

| Mode                             | Description                                                                                                                                                                         | LangGraph Library Method                                                                                 |
|----------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|
| [`values`](#stream-graph-state)  | Stream the full graph state after each [super-step](../../concepts/low_level.md#graphs).                                                                                            | `.stream()` / `.astream()` with [`stream_mode="values"`](../../how-tos/streaming.md#stream-graph-state)  |
| [`updates`](#stream-graph-state) | Streams the updates to the state after each step of the graph. If multiple updates are made in the same step (e.g., multiple nodes are run), those updates are streamed separately. | `.stream()` / `.astream()` with [`stream_mode="updates"`](../../how-tos/streaming.md#stream-graph-state) |
| [`messages-tuple`](#messages)    | Streams LLM tokens and metadata for the graph node where the LLM is invoked (useful for chat apps).                                                                                 | `.stream()` / `.astream()` with [`stream_mode="messages"`](../../how-tos/streaming.md#messages)          |
| [`debug`](#debug)                | Streams as much information as possible throughout the execution of the graph.                                                                                                      | `.stream()` / `.astream()` with [`stream_mode="debug"`](../../how-tos/streaming.md#stream-graph-state)   |
| [`custom`](#stream-custom-data)  | Streams custom data from inside your graph                                                                                                                                          | `.stream()` / `.astream()` with [`stream_mode="custom"`](../../how-tos/streaming.md#stream-custom-data)  |
| [`events`](#stream-events)       | Stream all events (including the state of the graph); mainly useful when migrating large LCEL apps.                                                                                 | `.astream_events()`                                                                                      |

### Source References

- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`main`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6527) (function in langgraph)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`up`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L3118) (function in langgraph)
- [`run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/_branch.py#L122) (function in langgraph)
- [`a`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4642) (function in langgraph)
