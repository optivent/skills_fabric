## Filter by node

To stream tokens only from specific nodes, use `stream_mode="messages"` and filter the outputs by the `langgraph_node` field in the streamed metadata:

:::python

```python
for msg, metadata in graph.stream( # (1)!
    inputs,
    # highlight-next-line
    stream_mode="messages",
):
    # highlight-next-line
    if msg.content and metadata["langgraph_node"] == "some_node_name": # (2)!
        ...
```

1. The "messages" stream mode returns a tuple of `(message_chunk, metadata)` where `message_chunk` is the token streamed by the LLM and `metadata` is a dictionary with information about the graph node where the LLM was called and other information.
2. Filter the streamed tokens by the `langgraph_node` field in the metadata to only include the tokens from the `write_poem` node.
   :::

:::js

```typescript
for await (const [msg, metadata] of await graph.stream(
  // (1)!
  inputs,
  { streamMode: "messages" }
)) {
  if (msg.content && metadata.langgraph_node === "some_node_name") {
    // (2)!
    // ...
  }
}
```

1. The "messages" stream mode returns a tuple of `[messageChunk, metadata]` where `messageChunk` is the token streamed by the LLM and `metadata` is a dictionary with information about the graph node where the LLM was called and other information.
2. Filter the streamed tokens by the `langgraph_node` field in the metadata to only include the tokens from the `writePoem` node.
   :::

??? example "Extended example: streaming LLM tokens from specific nodes"

      :::python
      ```python
      from typing import TypedDict
      from langgraph.graph import START, StateGraph
      from langchain_openai import ChatOpenAI

      model = ChatOpenAI(model="gpt-4o-mini")


      class State(TypedDict):
            topic: str
            joke: str
            poem: str


      def write_joke(state: State):
            topic = state["topic"]
            joke_response = model.invoke(
                  [{"role": "user", "content": f"Write a joke about {topic}"}]
            )
            return {"joke": joke_response.content}


      def write_poem(state: State):
            topic = state["topic"]
            poem_response = model.invoke(
                  [{"role": "user", "content": f"Write a short poem about {topic}"}]
            )
            return {"poem": poem_response.content}


      graph = (
            StateGraph(State)
            .add_node(write_joke)
            .add_node(write_poem)
            # write both the joke and the poem concurrently
            .add_edge(START, "write_joke")
            .add_edge(START, "write_poem")
            .compile()
      )

      # highlight-next-line
      for msg, metadata in graph.stream( # (1)!
          {"topic": "cats"},
          stream_mode="messages",
      ):
          # highlight-next-line
          if msg.content and metadata["langgraph_node"] == "write_poem": # (2)!
              print(msg.content, end="|", flush=True)
      ```

      1. The "messages" stream mode returns a tuple of `(message_chunk, metadata)` where `message_chunk` is the token streamed by the LLM and `metadata` is a dictionary with information about the graph node where the LLM was called and other information.
      2. Filter the streamed tokens by the `langgraph_node` field in the metadata to only include the tokens from the `write_poem` node.
      :::

      :::js
      ```typescript
      import { ChatOpenAI } from "@langchain/openai";
      import { StateGraph, START } from "@langchain/langgraph";
      import { z } from "zod";

      const model = new ChatOpenAI({ model: "gpt-4o-mini" });

      const State = z.object({
        topic: z.string(),
        joke: z.string(),
        poem: z.string(),
      });

      const graph = new StateGraph(State)
        .addNode("writeJoke", async (state) => {
          const topic = state.topic;
          const jokeResponse = await model.invoke([
            { role: "user", content: `Write a joke about ${topic}` }
          ]);
          return { joke: jokeResponse.content };
        })
        .addNode("writePoem", async (state) => {
          const topic = state.topic;
          const poemResponse = await model.invoke([
            { role: "user", content: `Write a short poem about ${topic}` }
          ]);
          return { poem: poemResponse.content };
        })
        // write both the joke and the poem concurrently
        .addEdge(START, "writeJoke")
        .addEdge(START, "writePoem")
        .compile();

      for await (const [msg, metadata] of await graph.stream( // (1)!
        { topic: "cats" },
        { streamMode: "messages" }
      )) {
        if (msg.content && metadata.langgraph_node === "writePoem") { // (2)!
          console.log(msg.content + "|");
        }
      }
      ```

      1. The "messages" stream mode returns a tuple of `[messageChunk, metadata]` where `messageChunk` is the token streamed by the LLM and `metadata` is a dictionary with information about the graph node where the LLM was called and other information.
      2. Filter the streamed tokens by the `langgraph_node` field in the metadata to only include the tokens from the `writePoem` node.
      :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`flush`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/sse.py#L68) (function in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`dict`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L151) (function in checkpoint)
- [`sync`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L556) (function in checkpoint)
