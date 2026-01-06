## Stream subgraph outputs

:::python
To include outputs from [subgraphs](../concepts/subgraphs.md) in the streamed outputs, you can set `subgraphs=True` in the `.stream()` method of the parent graph. This will stream outputs from both the parent graph and any subgraphs.

The outputs will be streamed as tuples `(namespace, data)`, where `namespace` is a tuple with the path to the node where a subgraph is invoked, e.g. `("parent_node:<task_id>", "child_node:<task_id>")`.

```python
for chunk in graph.stream(
    {"foo": "foo"},
    # highlight-next-line
    subgraphs=True, # (1)!
    stream_mode="updates",
):
    print(chunk)
```

1. Set `subgraphs=True` to stream outputs from subgraphs.
   :::

:::js
To include outputs from [subgraphs](../concepts/subgraphs.md) in the streamed outputs, you can set `subgraphs: true` in the `.stream()` method of the parent graph. This will stream outputs from both the parent graph and any subgraphs.

The outputs will be streamed as tuples `[namespace, data]`, where `namespace` is a tuple with the path to the node where a subgraph is invoked, e.g. `["parent_node:<task_id>", "child_node:<task_id>"]`.

```typescript
for await (const chunk of await graph.stream(
  { foo: "foo" },
  {
    subgraphs: true, // (1)!
    streamMode: "updates",
  }
)) {
  console.log(chunk);
}
```

1. Set `subgraphs: true` to stream outputs from subgraphs.
   :::

??? example "Extended example: streaming from subgraphs"

      :::python
      ```python
      from langgraph.graph import START, StateGraph
      from typing import TypedDict

      # Define subgraph
      class SubgraphState(TypedDict):
          foo: str  # note that this key is shared with the parent graph state
          bar: str

      def subgraph_node_1(state: SubgraphState):
          return {"bar": "bar"}

      def subgraph_node_2(state: SubgraphState):
          return {"foo": state["foo"] + state["bar"]}

      subgraph_builder = StateGraph(SubgraphState)
      subgraph_builder.add_node(subgraph_node_1)
      subgraph_builder.add_node(subgraph_node_2)
      subgraph_builder.add_edge(START, "subgraph_node_1")
      subgraph_builder.add_edge("subgraph_node_1", "subgraph_node_2")
      subgraph = subgraph_builder.compile()

      # Define parent graph
      class ParentState(TypedDict):
          foo: str

      def node_1(state: ParentState):
          return {"foo": "hi! " + state["foo"]}

      builder = StateGraph(ParentState)
      builder.add_node("node_1", node_1)
      builder.add_node("node_2", subgraph)
      builder.add_edge(START, "node_1")
      builder.add_edge("node_1", "node_2")
      graph = builder.compile()

      for chunk in graph.stream(
          {"foo": "foo"},
          stream_mode="updates",
          # highlight-next-line
          subgraphs=True, # (1)!
      ):
          print(chunk)
      ```

      1. Set `subgraphs=True` to stream outputs from subgraphs.
      :::

      :::js
      ```typescript
      import { StateGraph, START } from "@langchain/langgraph";
      import { z } from "zod";

      // Define subgraph
      const SubgraphState = z.object({
        foo: z.string(), // note that this key is shared with the parent graph state
        bar: z.string(),
      });

      const subgraphBuilder = new StateGraph(SubgraphState)
        .addNode("subgraphNode1", (state) => {
          return { bar: "bar" };
        })
        .addNode("subgraphNode2", (state) => {
          return { foo: state.foo + state.bar };
        })
        .addEdge(START, "subgraphNode1")
        .addEdge("subgraphNode1", "subgraphNode2");
      const subgraph = subgraphBuilder.compile();

      // Define parent graph
      const ParentState = z.object({
        foo: z.string(),
      });

      const builder = new StateGraph(ParentState)
        .addNode("node1", (state) => {
          return { foo: "hi! " + state.foo };
        })
        .addNode("node2", subgraph)
        .addEdge(START, "node1")
        .addEdge("node1", "node2");
      const graph = builder.compile();

      for await (const chunk of await graph.stream(
        { foo: "foo" },
        {
          streamMode: "updates",
          subgraphs: true, // (1)!
        }
      )) {
        console.log(chunk);
      }
      ```

      1. Set `subgraphs: true` to stream outputs from subgraphs.
      :::

      :::python
      ```
      ((), {'node_1': {'foo': 'hi! foo'}})
      (('node_2:dfddc4ba-c3c5-6887-5012-a243b5b377c2',), {'subgraph_node_1': {'bar': 'bar'}})
      (('node_2:dfddc4ba-c3c5-6887-5012-a243b5b377c2',), {'subgraph_node_2': {'foo': 'hi! foobar'}})
      ((), {'node_2': {'foo': 'hi! foobar'}})
      ```
      :::

      :::js
      ```
      [[], {'node1': {'foo': 'hi! foo'}}]
      [['node2:dfddc4ba-c3c5-6887-5012-a243b5b377c2'], {'subgraphNode1': {'bar': 'bar'}}]
      [['node2:dfddc4ba-c3c5-6887-5012-a243b5b377c2'], {'subgraphNode2': {'foo': 'hi! foobar'}}]
      [[], {'node2': {'foo': 'hi! foobar'}}]
      ```
      :::

      **Note** that we are receiving not just the node updates, but we also the namespaces which tell us what graph (or subgraph) we are streaming from.

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
