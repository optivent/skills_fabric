## Pause using `interrupt`

:::python
[Dynamic interrupts](../../concepts/human_in_the_loop.md#key-capabilities) (also known as dynamic breakpoints) are triggered based on the current state of the graph. You can set dynamic interrupts by calling @[`interrupt` function][interrupt] in the appropriate place. The graph will pause, which allows for human intervention, and then resumes the graph with their input. It's useful for tasks like approvals, edits, or gathering additional context.

!!! note

    As of v1.0, `interrupt` is the recommended way to pause a graph. `NodeInterrupt` is deprecated and will be removed in v2.0.

:::

:::js
[Dynamic interrupts](../../concepts/human_in_the_loop.md#key-capabilities) (also known as dynamic breakpoints) are triggered based on the current state of the graph. You can set dynamic interrupts by calling @[`interrupt` function][interrupt] in the appropriate place. The graph will pause, which allows for human intervention, and then resumes the graph with their input. It's useful for tasks like approvals, edits, or gathering additional context.
:::

To use `interrupt` in your graph, you need to:

1. [**Specify a checkpointer**](../../concepts/persistence.md#checkpoints) to save the graph state after each step.
2. **Call `interrupt()`** in the appropriate place. See the [Common Patterns](#common-patterns) section for examples.
3. **Run the graph** with a [**thread ID**](../../concepts/persistence.md#threads) until the `interrupt` is hit.
4. **Resume execution** using `invoke`/`stream` (see [**The `Command` primitive**](#resume-using-the-command-primitive)).

:::python

```python

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`Interrupt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L157) (class in langgraph)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
