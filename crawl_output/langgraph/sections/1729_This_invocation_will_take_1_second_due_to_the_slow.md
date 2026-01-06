## This invocation will take ~1 second due to the slow_task execution

try:
    # First invocation will raise an exception due to the `get_info` task failing
    main.invoke({'any_input': 'foobar'}, config=config)
except ValueError:
    pass  # Handle the failure gracefully
```

When we resume execution, we won't need to re-run the `slow_task` as its result is already saved in the checkpoint.

```python
main.invoke(None, config=config)
```

```pycon
'Ran slow task.'
```

:::

:::js

```typescript
import { entrypoint, task, MemorySaver } from "@langchain/langgraph";

// This variable is just used for demonstration purposes to simulate a network failure.
// It's not something you will have in your actual code.
let attempts = 0;

const getInfo = task("getInfo", async () => {
  /**
   * Simulates a task that fails once before succeeding.
   * Throws an exception on the first attempt, then returns "OK" on subsequent tries.
   */
  attempts += 1;

  if (attempts < 2) {
    throw new Error("Failure"); // Simulate a failure on the first attempt
  }
  return "OK";
});

// Initialize an in-memory checkpointer for persistence
const checkpointer = new MemorySaver();

const slowTask = task("slowTask", async () => {
  /**
   * Simulates a slow-running task by introducing a 1-second delay.
   */
  await new Promise((resolve) => setTimeout(resolve, 1000));
  return "Ran slow task.";
});

const main = entrypoint(
  { checkpointer, name: "main" },
  async (inputs: Record<string, any>) => {
    /**
     * Main workflow function that runs the slowTask and getInfo tasks sequentially.
     *
     * Parameters:
     * - inputs: Record<string, any> containing workflow input values.
     *
     * The workflow first executes `slowTask` and then attempts to execute `getInfo`,
     * which will fail on the first invocation.
     */
    const slowTaskResult = await slowTask(); // Blocking call to slowTask
    await getInfo(); // Exception will be raised here on the first attempt
    return slowTaskResult;
  }
);

// Workflow execution configuration with a unique thread identifier
const config = {
  configurable: {
    thread_id: "1", // Unique identifier to track workflow execution
  },
};

// This invocation will take ~1 second due to the slowTask execution
try {
  // First invocation will raise an exception due to the `getInfo` task failing
  await main.invoke({ any_input: "foobar" }, config);
} catch (err) {
  // Handle the failure gracefully
}
```

When we resume execution, we won't need to re-run the `slowTask` as its result is already saved in the checkpoint.

```typescript
await main.invoke(null, config);
```

```
'Ran slow task.'
```

:::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`execute`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1174) (function in prebuilt)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
