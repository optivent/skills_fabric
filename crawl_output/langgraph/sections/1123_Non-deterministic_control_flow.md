## Non-deterministic control flow

Operations that might give different results each time (like getting current time or random numbers) should be encapsulated in tasks to ensure that on resume, the same result is returned.

- In a task: Get random number (5) → interrupt → resume → (returns 5 again) → ...
- Not in a task: Get random number (5) → interrupt → resume → get new random number (7) → ...

:::python
This is especially important when using **human-in-the-loop** workflows with multiple interrupts calls. LangGraph keeps a list of resume values for each task/entrypoint. When an interrupt is encountered, it's matched with the corresponding resume value. This matching is strictly **index-based**, so the order of the resume values should match the order of the interrupts.
:::

:::js
This is especially important when using **human-in-the-loop** workflows with multiple interrupt calls. LangGraph keeps a list of resume values for each task/entrypoint. When an interrupt is encountered, it's matched with the corresponding resume value. This matching is strictly **index-based**, so the order of the resume values should match the order of the interrupts.
:::

If order of execution is not maintained when resuming, one `interrupt` call may be matched with the wrong `resume` value, leading to incorrect results.

Please read the section on [determinism](#determinism) for more details.

=== "Incorrect"

    In this example, the workflow uses the current time to determine which task to execute. This is non-deterministic because the result of the workflow depends on the time at which it is executed.

    :::python
    ```python
    from langgraph.func import entrypoint

    @entrypoint(checkpointer=checkpointer)
    def my_workflow(inputs: dict) -> int:
        t0 = inputs["t0"]
        # highlight-next-line
        t1 = time.time()

        delta_t = t1 - t0

        if delta_t > 1:
            result = slow_task(1).result()
            value = interrupt("question")
        else:
            result = slow_task(2).result()
            value = interrupt("question")

        return {
            "result": result,
            "value": value
        }
    ```
    :::

    :::js
    ```typescript
    import { entrypoint, interrupt } from "@langchain/langgraph";

    const myWorkflow = entrypoint(
      { checkpointer, name: "workflow" },
      async (inputs: { t0: number }) => {
        const t1 = Date.now();

        const deltaT = t1 - inputs.t0;

        if (deltaT > 1000) {
          const result = await slowTask(1);
          const value = interrupt("question");
          return { result, value };
        } else {
          const result = await slowTask(2);
          const value = interrupt("question");
          return { result, value };
        }
      }
    );
    ```
    :::

=== "Correct"

    :::python
    In this example, the workflow uses the input `t0` to determine which task to execute. This is deterministic because the result of the workflow depends only on the input.

    ```python
    import time

    from langgraph.func import task

    # highlight-next-line
    @task
    # highlight-next-line
    def get_time() -> float:
        return time.time()

    @entrypoint(checkpointer=checkpointer)
    def my_workflow(inputs: dict) -> int:
        t0 = inputs["t0"]
        # highlight-next-line
        t1 = get_time().result()

        delta_t = t1 - t0

        if delta_t > 1:
            result = slow_task(1).result()
            value = interrupt("question")
        else:
            result = slow_task(2).result()
            value = interrupt("question")

        return {
            "result": result,
            "value": value
        }
    ```
    :::

    :::js
    In this example, the workflow uses the input `t0` to determine which task to execute. This is deterministic because the result of the workflow depends only on the input.

    ```typescript
    import { entrypoint, task, interrupt } from "@langchain/langgraph";

    const getTime = task("getTime", () => Date.now());

    const myWorkflow = entrypoint(
      { checkpointer, name: "workflow" },
      async (inputs: { t0: number }): Promise<any> => {
        const t1 = await getTime();

        const deltaT = t1 - inputs.t0;

        if (deltaT > 1000) {
          const result = await slowTask(1);
          const value = interrupt("question");
          return { result, value };
        } else {
          const result = await slowTask(2);
          const value = interrupt("question");
          return { result, value };
        }
      }
    );
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`execute`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1174) (function in prebuilt)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`count`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L6530) (function in sdk-py)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`list`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L174) (function in checkpoint)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`Interrupt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L157) (class in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`read`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1044) (class in sdk-py)
