## Basic usage example

:::python
LangGraph graphs expose the @[`.stream()`][Pregel.stream] (sync) and @[`.astream()`][Pregel.astream] (async) methods to yield streamed outputs as iterators.

=== "Sync"

    ```python
    for chunk in graph.stream(inputs, stream_mode="updates"):
        print(chunk)
    ```

=== "Async"

    ```python
    async for chunk in graph.astream(inputs, stream_mode="updates"):
        print(chunk)
    ```

:::

:::js
LangGraph graphs expose the @[`.stream()`][Pregel.stream] method to yield streamed outputs as iterators.

```typescript
for await (const chunk of await graph.stream(inputs, {
  streamMode: "updates",
})) {
  console.log(chunk);
}
```

:::

??? example "Extended example: streaming updates"

      :::python
      ```python
      from typing import TypedDict
      from langgraph.graph import StateGraph, START, END

      class State(TypedDict):
          topic: str
          joke: str

      def refine_topic(state: State):
          return {"topic": state["topic"] + " and cats"}

      def generate_joke(state: State):
          return {"joke": f"This is a joke about {state['topic']}"}

      graph = (
          StateGraph(State)
          .add_node(refine_topic)
          .add_node(generate_joke)
          .add_edge(START, "refine_topic")
          .add_edge("refine_topic", "generate_joke")
          .add_edge("generate_joke", END)
          .compile()
      )

      # highlight-next-line
      for chunk in graph.stream( # (1)!
          {"topic": "ice cream"},
          # highlight-next-line
          stream_mode="updates", # (2)!
      ):
          print(chunk)
      ```

      1. The `stream()` method returns an iterator that yields streamed outputs.
      2. Set `stream_mode="updates"` to stream only the updates to the graph state after each node. Other stream modes are also available. See [supported stream modes](#supported-stream-modes) for details.
      :::

      :::js
      ```typescript
      import { StateGraph, START, END } from "@langchain/langgraph";
      import { z } from "zod";

      const State = z.object({
        topic: z.string(),
        joke: z.string(),
      });

      const graph = new StateGraph(State)
        .addNode("refineTopic", (state) => {
          return { topic: state.topic + " and cats" };
        })
        .addNode("generateJoke", (state) => {
          return { joke: `This is a joke about ${state.topic}` };
        })
        .addEdge(START, "refineTopic")
        .addEdge("refineTopic", "generateJoke")
        .addEdge("generateJoke", END)
        .compile();

      for await (const chunk of await graph.stream(
        { topic: "ice cream" },
        { streamMode: "updates" } // (1)!
      )) {
        console.log(chunk);
      }
      ```

      1. Set `streamMode: "updates"` to stream only the updates to the graph state after each node. Other stream modes are also available. See [supported stream modes](#supported-stream-modes) for details.
      :::

      ```output
      {'refineTopic': {'topic': 'ice cream and cats'}}
      {'generateJoke': {'joke': 'This is a joke about ice cream and cats'}}
      ```                                                                                                   |

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`set`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L84) (function in checkpoint)
- [`dict`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L151) (function in checkpoint)
