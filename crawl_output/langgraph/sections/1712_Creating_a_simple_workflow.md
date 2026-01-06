## Creating a simple workflow

When defining an `entrypoint`, input is restricted to the first argument of the function. To pass multiple inputs, you can use a dictionary.

:::python

```python
@entrypoint(checkpointer=checkpointer)
def my_workflow(inputs: dict) -> int:
    value = inputs["value"]
    another_value = inputs["another_value"]
    ...

my_workflow.invoke({"value": 1, "another_value": 2})
```

:::

:::js

```typescript
const checkpointer = new MemorySaver();

const myWorkflow = entrypoint(
  { checkpointer, name: "myWorkflow" },
  async (inputs: { value: number; anotherValue: number }) => {
    const value = inputs.value;
    const anotherValue = inputs.anotherValue;
    // ...
  }
);

await myWorkflow.invoke({ value: 1, anotherValue: 2 });
```

:::

??? example "Extended example: simple workflow"

    :::python
    ```python
    import uuid
    from langgraph.func import entrypoint, task
    from langgraph.checkpoint.memory import InMemorySaver

    # Task that checks if a number is even
    @task
    def is_even(number: int) -> bool:
        return number % 2 == 0

    # Task that formats a message
    @task
    def format_message(is_even: bool) -> str:
        return "The number is even." if is_even else "The number is odd."

    # Create a checkpointer for persistence
    checkpointer = InMemorySaver()

    @entrypoint(checkpointer=checkpointer)
    def workflow(inputs: dict) -> str:
        """Simple workflow to classify a number."""
        even = is_even(inputs["number"]).result()
        return format_message(even).result()

    # Run the workflow with a unique thread ID
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    result = workflow.invoke({"number": 7}, config=config)
    print(result)
    ```
    :::

    :::js
    ```typescript
    import { v4 as uuidv4 } from "uuid";
    import { entrypoint, task, MemorySaver } from "@langchain/langgraph";

    // Task that checks if a number is even
    const isEven = task("isEven", async (number: number) => {
      return number % 2 === 0;
    });

    // Task that formats a message
    const formatMessage = task("formatMessage", async (isEven: boolean) => {
      return isEven ? "The number is even." : "The number is odd.";
    });

    // Create a checkpointer for persistence
    const checkpointer = new MemorySaver();

    const workflow = entrypoint(
      { checkpointer, name: "workflow" },
      async (inputs: { number: number }) => {
        // Simple workflow to classify a number
        const even = await isEven(inputs.number);
        return await formatMessage(even);
      }
    );

    // Run the workflow with a unique thread ID
    const config = { configurable: { thread_id: uuidv4() } };
    const result = await workflow.invoke({ number: 7 }, config);
    console.log(result);
    ```
    :::

??? example "Extended example: Compose an essay with an LLM"

    This example demonstrates how to use the `@task` and `@entrypoint` decorators
    syntactically. Given that a checkpointer is provided, the workflow results will
    be persisted in the checkpointer.

    :::python
    ```python
    import uuid
    from langchain.chat_models import init_chat_model
    from langgraph.func import entrypoint, task
    from langgraph.checkpoint.memory import InMemorySaver

    llm = init_chat_model('openai:gpt-3.5-turbo')

    # Task: generate essay using an LLM
    @task
    def compose_essay(topic: str) -> str:
        """Generate an essay about the given topic."""
        return llm.invoke([
            {"role": "system", "content": "You are a helpful assistant that writes essays."},
            {"role": "user", "content": f"Write an essay about {topic}."}
        ]).content

    # Create a checkpointer for persistence
    checkpointer = InMemorySaver()

    @entrypoint(checkpointer=checkpointer)
    def workflow(topic: str) -> str:
        """Simple workflow that generates an essay with an LLM."""
        return compose_essay(topic).result()

    # Execute the workflow
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    result = workflow.invoke("the history of flight", config=config)
    print(result)
    ```
    :::

    :::js
    ```typescript
    import { v4 as uuidv4 } from "uuid";
    import { ChatOpenAI } from "@langchain/openai";
    import { entrypoint, task, MemorySaver } from "@langchain/langgraph";

    const llm = new ChatOpenAI({ model: "gpt-3.5-turbo" });

    // Task: generate essay using an LLM
    const composeEssay = task("composeEssay", async (topic: string) => {
      // Generate an essay about the given topic
      const response = await llm.invoke([
        { role: "system", content: "You are a helpful assistant that writes essays." },
        { role: "user", content: `Write an essay about ${topic}.` }
      ]);
      return response.content as string;
    });

    // Create a checkpointer for persistence
    const checkpointer = new MemorySaver();

    const workflow = entrypoint(
      { checkpointer, name: "workflow" },
      async (topic: string) => {
        // Simple workflow that generates an essay with an LLM
        return await composeEssay(topic);
      }
    );

    // Execute the workflow
    const config = { configurable: { thread_id: uuidv4() } };
    const result = await workflow.invoke("the history of flight", config);
    console.log(result);
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`execute`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1174) (function in prebuilt)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`Assistant`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L242) (class in sdk-py)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
