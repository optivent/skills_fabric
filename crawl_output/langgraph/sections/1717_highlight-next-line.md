## highlight-next-line

for mode, chunk in main.stream( # (5)!
    {"x": 5},
    stream_mode=["custom", "updates"], # (6)!
    config=config
):
    print(f"{mode}: {chunk}")
```

1. Import `get_stream_writer` from `langgraph.config`.
2. Obtain a stream writer instance within the entrypoint.
3. Emit custom data before computation begins.
4. Emit another custom message after computing the result.
5. Use `.stream()` to process streamed output.
6. Specify which streaming modes to use.

```pycon
('updates', {'add_one': 2})
('updates', {'add_two': 3})
('custom', 'hello')
('custom', 'world')
('updates', {'main': 5})
```

!!! important "Async with Python < 3.11"

    If using Python < 3.11 and writing async code, using `get_stream_writer()` will not work. Instead please
    use the `StreamWriter` class directly. See [Async with Python < 3.11](../how-tos/streaming.md#async) for more details.

    ```python
    from langgraph.types import StreamWriter

    @entrypoint(checkpointer=checkpointer)
    # highlight-next-line
    async def main(inputs: dict, writer: StreamWriter) -> int:
        ...
    ```

:::

:::js

```typescript
import {
  entrypoint,
  MemorySaver,
  LangGraphRunnableConfig,
} from "@langchain/langgraph";

const checkpointer = new MemorySaver();

const main = entrypoint(
  { checkpointer, name: "main" },
  async (
    inputs: { x: number },
    config: LangGraphRunnableConfig
  ): Promise<number> => {
    config.writer?.("Started processing"); // (1)!
    const result = inputs.x * 2;
    config.writer?.(`Result is ${result}`); // (2)!
    return result;
  }
);

const config = { configurable: { thread_id: "abc" } };

// (3)!
for await (const [mode, chunk] of await main.stream(
  { x: 5 },
  { streamMode: ["custom", "updates"], ...config } // (4)!
)) {
  console.log(`${mode}: ${JSON.stringify(chunk)}`);
}
```

1. Emit custom data before computation begins.
2. Emit another custom message after computing the result.
3. Use `.stream()` to process streamed output.
4. Specify which streaming modes to use.

```
updates: {"addOne": 2}
updates: {"addTwo": 3}
custom: "hello"
custom: "world"
updates: {"main": 5}
```

:::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
