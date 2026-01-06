## Channels

Channels are used to communicate between actors (PregelNodes). Each channel has a value type, an update type, and an update function – which takes a sequence of updates and modifies the stored value. Channels can be used to send data from one chain to another, or to send data from a chain to itself in a future step. LangGraph provides a number of built-in channels:

:::python

- @[LastValue][LastValue]: The default channel, stores the last value sent to the channel, useful for input and output values, or for sending data from one step to the next.
- @[Topic][Topic]: A configurable PubSub Topic, useful for sending multiple values between **actors**, or for accumulating output. Can be configured to deduplicate values or to accumulate values over the course of multiple steps.
- @[BinaryOperatorAggregate][BinaryOperatorAggregate]: stores a persistent value, updated by applying a binary operator to the current value and each update sent to the channel, useful for computing aggregates over multiple steps; e.g.,`total = BinaryOperatorAggregate(int, operator.add)`
  :::

:::js

- @[LastValue]: The default channel, stores the last value sent to the channel, useful for input and output values, or for sending data from one step to the next.
- @[Topic]: A configurable PubSub Topic, useful for sending multiple values between **actors**, or for accumulating output. Can be configured to deduplicate values or to accumulate values over the course of multiple steps.
- @[BinaryOperatorAggregate]: stores a persistent value, updated by applying a binary operator to the current value and each update sent to the channel, useful for computing aggregates over multiple steps; e.g.,`total = BinaryOperatorAggregate(int, operator.add)`
  :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`dup`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_encryption.py#L51) (function in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`Send`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L285) (class in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`store`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/test_store.py#L34) (function in checkpoint-postgres)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
