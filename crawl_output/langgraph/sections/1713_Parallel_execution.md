## Parallel execution

Tasks can be executed in parallel by invoking them concurrently and waiting for the results. This is useful for improving performance in IO bound tasks (e.g., calling APIs for LLMs).

:::python

```python
@task
def add_one(number: int) -> int:
    return number + 1

@entrypoint(checkpointer=checkpointer)
def graph(numbers: list[int]) -> list[str]:
    futures = [add_one(i) for i in numbers]
    return [f.result() for f in futures]
```

:::

:::js

```typescript
const addOne = task("addOne", async (number: number) => {
  return number + 1;
});

const graph = entrypoint(
  { checkpointer, name: "graph" },
  async (numbers: number[]) => {
    return await Promise.all(numbers.map(addOne));
  }
);
```

:::

??? example "Extended example: parallel LLM calls"

    This example demonstrates how to run multiple LLM calls in parallel using `@task`. Each call generates a paragraph on a different topic, and results are joined into a single text output.

    :::python
    ```python
    import uuid
    from langchain.chat_models import init_chat_model
    from langgraph.func import entrypoint, task
    from langgraph.checkpoint.memory import InMemorySaver

    # Initialize the LLM model
    llm = init_chat_model("openai:gpt-3.5-turbo")

    # Task that generates a paragraph about a given topic
    @task
    def generate_paragraph(topic: str) -> str:
        response = llm.invoke([
            {"role": "system", "content": "You are a helpful assistant that writes educational paragraphs."},
            {"role": "user", "content": f"Write a paragraph about {topic}."}
        ])
        return response.content

    # Create a checkpointer for persistence
    checkpointer = InMemorySaver()

    @entrypoint(checkpointer=checkpointer)
    def workflow(topics: list[str]) -> str:
        """Generates multiple paragraphs in parallel and combines them."""
        futures = [generate_paragraph(topic) for topic in topics]
        paragraphs = [f.result() for f in futures]
        return "\n\n".join(paragraphs)

    # Run the workflow
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    result = workflow.invoke(["quantum computing", "climate change", "history of aviation"], config=config)
    print(result)
    ```
    :::

    :::js
    ```typescript
    import { v4 as uuidv4 } from "uuid";
    import { ChatOpenAI } from "@langchain/openai";
    import { entrypoint, task, MemorySaver } from "@langchain/langgraph";

    // Initialize the LLM model
    const llm = new ChatOpenAI({ model: "gpt-3.5-turbo" });

    // Task that generates a paragraph about a given topic
    const generateParagraph = task("generateParagraph", async (topic: string) => {
      const response = await llm.invoke([
        { role: "system", content: "You are a helpful assistant that writes educational paragraphs." },
        { role: "user", content: `Write a paragraph about ${topic}.` }
      ]);
      return response.content as string;
    });

    // Create a checkpointer for persistence
    const checkpointer = new MemorySaver();

    const workflow = entrypoint(
      { checkpointer, name: "workflow" },
      async (topics: string[]) => {
        // Generates multiple paragraphs in parallel and combines them
        const paragraphs = await Promise.all(topics.map(generateParagraph));
        return paragraphs.join("\n\n");
      }
    );

    // Run the workflow
    const config = { configurable: { thread_id: uuidv4() } };
    const result = await workflow.invoke(["quantum computing", "climate change", "history of aviation"], config);
    console.log(result);
    ```
    :::

    This example uses LangGraph's concurrency model to improve execution time, especially when tasks involve I/O like LLM completions.

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`execute`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1174) (function in prebuilt)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`list`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L174) (function in checkpoint)
- [`join`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L6114) (function in sdk-py)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
