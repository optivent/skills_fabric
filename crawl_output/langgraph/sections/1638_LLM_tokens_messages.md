## LLM tokens {#messages}

Use the `messages` streaming mode to stream Large Language Model (LLM) outputs **token by token** from any part of your graph, including nodes, tools, subgraphs, or tasks.

:::python
The streamed output from [`messages` mode](#supported-stream-modes) is a tuple `(message_chunk, metadata)` where:

- `message_chunk`: the token or message segment from the LLM.
- `metadata`: a dictionary containing details about the graph node and LLM invocation.

> If your LLM is not available as a LangChain integration, you can stream its outputs using `custom` mode instead. See [use with any LLM](#use-with-any-llm) for details.

!!! warning "Manual config required for async in Python < 3.11"

    When using Python < 3.11 with async code, you must explicitly pass `RunnableConfig` to `ainvoke()` to enable proper streaming. See [Async with Python < 3.11](#async) for details or upgrade to Python 3.11+.

```python
from dataclasses import dataclass

from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START


@dataclass
class MyState:
    topic: str
    joke: str = ""


llm = init_chat_model(model="openai:gpt-4o-mini")

def call_model(state: MyState):
    """Call the LLM to generate a joke about a topic"""
    # highlight-next-line
    llm_response = llm.invoke( # (1)!
        [
            {"role": "user", "content": f"Generate a joke about {state.topic}"}
        ]
    )
    return {"joke": llm_response.content}

graph = (
    StateGraph(MyState)
    .add_node(call_model)
    .add_edge(START, "call_model")
    .compile()
)

for message_chunk, metadata in graph.stream( # (2)!
    {"topic": "ice cream"},
    # highlight-next-line
    stream_mode="messages",
):
    if message_chunk.content:
        print(message_chunk.content, end="|", flush=True)
```

1. Note that the message events are emitted even when the LLM is run using `.invoke` rather than `.stream`.
2. The "messages" stream mode returns an iterator of tuples `(message_chunk, metadata)` where `message_chunk` is the token streamed by the LLM and `metadata` is a dictionary with information about the graph node where the LLM was called and other information.
   :::

:::js
The streamed output from [`messages` mode](#supported-stream-modes) is a tuple `[message_chunk, metadata]` where:

- `message_chunk`: the token or message segment from the LLM.
- `metadata`: a dictionary containing details about the graph node and LLM invocation.

> If your LLM is not available as a LangChain integration, you can stream its outputs using `custom` mode instead. See [use with any LLM](#use-with-any-llm) for details.

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { StateGraph, START } from "@langchain/langgraph";
import { z } from "zod";

const MyState = z.object({
  topic: z.string(),
  joke: z.string().default(""),
});

const llm = new ChatOpenAI({ model: "gpt-4o-mini" });

const callModel = async (state: z.infer<typeof MyState>) => {
  // Call the LLM to generate a joke about a topic
  const llmResponse = await llm.invoke([
    { role: "user", content: `Generate a joke about ${state.topic}` },
  ]); // (1)!
  return { joke: llmResponse.content };
};

const graph = new StateGraph(MyState)
  .addNode("callModel", callModel)
  .addEdge(START, "callModel")
  .compile();

for await (const [messageChunk, metadata] of await graph.stream(
  // (2)!
  { topic: "ice cream" },
  { streamMode: "messages" }
)) {
  if (messageChunk.content) {
    console.log(messageChunk.content + "|");
  }
}
```

1. Note that the message events are emitted even when the LLM is run using `.invoke` rather than `.stream`.
2. The "messages" stream mode returns an iterator of tuples `[messageChunk, metadata]` where `messageChunk` is the token streamed by the LLM and `metadata` is a dictionary with information about the graph node where the LLM was called and other information.
   :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`call_model`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6930) (function in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`flush`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/sse.py#L68) (function in sdk-py)
