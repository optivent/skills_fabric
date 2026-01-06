## Call other entrypoints

You can call other **entrypoints** from within an **entrypoint** or a **task**.

:::python

```python
@entrypoint() # Will automatically use the checkpointer from the parent entrypoint
def some_other_workflow(inputs: dict) -> int:
    return inputs["value"]

@entrypoint(checkpointer=checkpointer)
def my_workflow(inputs: dict) -> int:
    value = some_other_workflow.invoke({"value": 1})
    return value
```

:::

:::js

```typescript
// Will automatically use the checkpointer from the parent entrypoint
const someOtherWorkflow = entrypoint(
  { name: "someOtherWorkflow" },
  async (inputs: { value: number }) => {
    return inputs.value;
  }
);

const myWorkflow = entrypoint(
  { checkpointer, name: "myWorkflow" },
  async (inputs: { value: number }) => {
    const value = await someOtherWorkflow.invoke({ value: 1 });
    return value;
  }
);
```

:::

??? example "Extended example: calling another entrypoint"

    :::python
    ```python
    import uuid
    from langgraph.func import entrypoint
    from langgraph.checkpoint.memory import InMemorySaver

    # Initialize a checkpointer
    checkpointer = InMemorySaver()

    # A reusable sub-workflow that multiplies a number
    @entrypoint()
    def multiply(inputs: dict) -> int:
        return inputs["a"] * inputs["b"]

    # Main workflow that invokes the sub-workflow
    @entrypoint(checkpointer=checkpointer)
    def main(inputs: dict) -> dict:
        result = multiply.invoke({"a": inputs["x"], "b": inputs["y"]})
        return {"product": result}

    # Execute the main workflow
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    print(main.invoke({"x": 6, "y": 7}, config=config))  # Output: {'product': 42}
    ```
    :::

    :::js
    ```typescript
    import { v4 as uuidv4 } from "uuid";
    import { entrypoint, MemorySaver } from "@langchain/langgraph";

    // Initialize a checkpointer
    const checkpointer = new MemorySaver();

    // A reusable sub-workflow that multiplies a number
    const multiply = entrypoint(
      { name: "multiply" },
      async (inputs: { a: number; b: number }) => {
        return inputs.a * inputs.b;
      }
    );

    // Main workflow that invokes the sub-workflow
    const main = entrypoint(
      { checkpointer, name: "main" },
      async (inputs: { x: number; y: number }) => {
        const result = await multiply.invoke({ a: inputs.x, b: inputs.y });
        return { product: result };
      }
    );

    // Execute the main workflow
    const config = { configurable: { thread_id: uuidv4() } };
    console.log(await main.invoke({ x: 6, y: 7 }, config)); // Output: { product: 42 }
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`multiply`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6341) (function in langgraph)
- [`execute`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1174) (function in prebuilt)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`read`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1044) (class in sdk-py)
