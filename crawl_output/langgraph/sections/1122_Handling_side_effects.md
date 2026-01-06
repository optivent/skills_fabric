## Handling side effects

Encapsulate side effects (e.g., writing to a file, sending an email) in tasks to ensure they are not executed multiple times when resuming a workflow.

=== "Incorrect"

    In this example, a side effect (writing to a file) is directly included in the workflow, so it will be executed a second time when resuming the workflow.

    :::python
    ```python
    @entrypoint(checkpointer=checkpointer)
    def my_workflow(inputs: dict) -> int:
        # This code will be executed a second time when resuming the workflow.
        # Which is likely not what you want.
        # highlight-next-line
        with open("output.txt", "w") as f:
            # highlight-next-line
            f.write("Side effect executed")
        value = interrupt("question")
        return value
    ```
    :::

    :::js
    ```typescript
    import { entrypoint, interrupt } from "@langchain/langgraph";
    import fs from "fs";

    const myWorkflow = entrypoint(
      { checkpointer, name: "workflow },
      async (inputs: Record<string, any>) => {
        // This code will be executed a second time when resuming the workflow.
        // Which is likely not what you want.
        fs.writeFileSync("output.txt", "Side effect executed");
        const value = interrupt("question");
        return value;
      }
    );
    ```
    :::

=== "Correct"

    In this example, the side effect is encapsulated in a task, ensuring consistent execution upon resumption.

    :::python
    ```python
    from langgraph.func import task

    # highlight-next-line
    @task
    # highlight-next-line
    def write_to_file():
        with open("output.txt", "w") as f:
            f.write("Side effect executed")

    @entrypoint(checkpointer=checkpointer)
    def my_workflow(inputs: dict) -> int:
        # The side effect is now encapsulated in a task.
        write_to_file().result()
        value = interrupt("question")
        return value
    ```
    :::

    :::js
    ```typescript
    import { entrypoint, task, interrupt } from "@langchain/langgraph";
    import * as fs from "fs";

    const writeToFile = task("writeToFile", async () => {
      fs.writeFileSync("output.txt", "Side effect executed");
    });

    const myWorkflow = entrypoint(
      { checkpointer, name: "workflow" },
      async (inputs: Record<string, any>) => {
        // The side effect is now encapsulated in a task.
        await writeToFile();
        const value = interrupt("question");
        return value;
      }
    );
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`execute`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1174) (function in prebuilt)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`Interrupt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L157) (class in langgraph)
- [`Send`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L285) (class in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`dict`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L151) (function in checkpoint)
- [`sync`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L556) (function in checkpoint)
