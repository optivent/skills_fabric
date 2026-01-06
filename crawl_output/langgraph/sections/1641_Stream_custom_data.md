## Stream custom data

:::python
To send **custom user-defined data** from inside a LangGraph node or tool, follow these steps:

1. Use `get_stream_writer()` to access the stream writer and emit custom data.
2. Set `stream_mode="custom"` when calling `.stream()` or `.astream()` to get the custom data in the stream. You can combine multiple modes (e.g., `["updates", "custom"]`), but at least one must be `"custom"`.

!!! warning "No `get_stream_writer()` in async for Python < 3.11"

    In async code running on Python < 3.11, `get_stream_writer()` will not work.
    Instead, add a `writer` parameter to your node or tool and pass it manually.
    See [Async with Python < 3.11](#async) for usage examples.

=== "node"

      ```python
      from typing import TypedDict
      from langgraph.config import get_stream_writer
      from langgraph.graph import StateGraph, START

      class State(TypedDict):
          query: str
          answer: str

      def node(state: State):
          writer = get_stream_writer()  # (1)!
          writer({"custom_key": "Generating custom data inside node"}) # (2)!
          return {"answer": "some data"}

      graph = (
          StateGraph(State)
          .add_node(node)
          .add_edge(START, "node")
          .compile()
      )

      inputs = {"query": "example"}

      # Usage
      for chunk in graph.stream(inputs, stream_mode="custom"):  # (3)!
          print(chunk)
      ```

      1. Get the stream writer to send custom data.
      2. Emit a custom key-value pair (e.g., progress update).
      3. Set `stream_mode="custom"` to receive the custom data in the stream.

=== "tool"

      ```python
      from langchain_core.tools import tool
      from langgraph.config import get_stream_writer

      @tool
      def query_database(query: str) -> str:
          """Query the database."""
          writer = get_stream_writer() # (1)!
          # highlight-next-line
          writer({"data": "Retrieved 0/100 records", "type": "progress"}) # (2)!
          # perform query
          # highlight-next-line
          writer({"data": "Retrieved 100/100 records", "type": "progress"}) # (3)!
          return "some-answer"


      graph = ... # define a graph that uses this tool

      for chunk in graph.stream(inputs, stream_mode="custom"): # (4)!
          print(chunk)
      ```

      1. Access the stream writer to send custom data.
      2. Emit a custom key-value pair (e.g., progress update).
      3. Emit another custom key-value pair.
      4. Set `stream_mode="custom"` to receive the custom data in the stream.

:::

:::js
To send **custom user-defined data** from inside a LangGraph node or tool, follow these steps:

1. Use the `writer` parameter from the `LangGraphRunnableConfig` to emit custom data.
2. Set `streamMode: "custom"` when calling `.stream()` to get the custom data in the stream. You can combine multiple modes (e.g., `["updates", "custom"]`), but at least one must be `"custom"`.

=== "node"

      ```typescript
      import { StateGraph, START, LangGraphRunnableConfig } from "@langchain/langgraph";
      import { z } from "zod";

      const State = z.object({
        query: z.string(),
        answer: z.string(),
      });

      const graph = new StateGraph(State)
        .addNode("node", async (state, config) => {
          config.writer({ custom_key: "Generating custom data inside node" }); // (1)!
          return { answer: "some data" };
        })
        .addEdge(START, "node")
        .compile();

      const inputs = { query: "example" };

      // Usage
      for await (const chunk of await graph.stream(inputs, { streamMode: "custom" })) { // (2)!
        console.log(chunk);
      }
      ```

      1. Use the writer to emit a custom key-value pair (e.g., progress update).
      2. Set `streamMode: "custom"` to receive the custom data in the stream.

=== "tool"

      ```typescript
      import { tool } from "@langchain/core/tools";
      import { LangGraphRunnableConfig } from "@langchain/langgraph";
      import { z } from "zod";

      const queryDatabase = tool(
        async (input, config: LangGraphRunnableConfig) => {
          config.writer({ data: "Retrieved 0/100 records", type: "progress" }); // (1)!
          // perform query
          config.writer({ data: "Retrieved 100/100 records", type: "progress" }); // (2)!
          return "some-answer";
        },
        {
          name: "query_database",
          description: "Query the database.",
          schema: z.object({
            query: z.string().describe("The query to execute."),
          }),
        }
      );

      const graph = // ... define a graph that uses this tool

      for await (const chunk of await graph.stream(inputs, { streamMode: "custom" })) { // (3)!
        console.log(chunk);
      }
      ```

      1. Use the writer to emit a custom key-value pair (e.g., progress update).
      2. Emit another custom key-value pair.
      3. Set `streamMode: "custom"` to receive the custom data in the stream.

:::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`execute`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1174) (function in prebuilt)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
