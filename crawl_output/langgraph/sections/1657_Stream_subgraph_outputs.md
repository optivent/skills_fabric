## Stream subgraph outputs

To include outputs from subgraphs in the streamed outputs, you can set the subgraphs option in the stream method of the parent graph. This will stream outputs from both the parent graph and any subgraphs.

:::python
```python
for chunk in graph.stream(
    {"foo": "foo"},
    subgraphs=True, # (1)!
    stream_mode="updates",
):
    print(chunk)
```

1. Set `subgraphs=True` to stream outputs from subgraphs.
:::

:::js
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

??? example "Stream from subgraphs"

    :::python
    ```python
    from typing_extensions import TypedDict
    from langgraph.graph.state import StateGraph, START

    # Define subgraph
    class SubgraphState(TypedDict):
        foo: str
        bar: str
    
    def subgraph_node_1(state: SubgraphState):
        return {"bar": "bar"}
    
    def subgraph_node_2(state: SubgraphState):
        # note that this node is using a state key ('bar') that is only available in the subgraph
        # and is sending update on the shared state key ('foo')
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
        subgraphs=True, # (1)!
    ):
        print(chunk)
    ```
  
    1. Set `subgraphs=True` to stream outputs from subgraphs.

    ```
    ((), {'node_1': {'foo': 'hi! foo'}})
    (('node_2:e58e5673-a661-ebb0-70d4-e298a7fc28b7',), {'subgraph_node_1': {'bar': 'bar'}})
    (('node_2:e58e5673-a661-ebb0-70d4-e298a7fc28b7',), {'subgraph_node_2': {'foo': 'hi! foobar'}})
    ((), {'node_2': {'foo': 'hi! foobar'}})
    ```
    :::

    :::js
    ```typescript
    import { StateGraph, START } from "@langchain/langgraph";
    import { z } from "zod";

    // Define subgraph
    const SubgraphState = z.object({
      foo: z.string(),
      bar: z.string(),
    });
    
    const subgraphBuilder = new StateGraph(SubgraphState)
      .addNode("subgraphNode1", (state) => {
        return { bar: "bar" };
      })
      .addNode("subgraphNode2", (state) => {
        // note that this node is using a state key ('bar') that is only available in the subgraph
        // and is sending update on the shared state key ('foo')
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
  
    2. Set `subgraphs: true` to stream outputs from subgraphs.

    ```
    [[], { node1: { foo: 'hi! foo' } }]
    [['node2:e58e5673-a661-ebb0-70d4-e298a7fc28b7'], { subgraphNode1: { bar: 'bar' } }]
    [['node2:e58e5673-a661-ebb0-70d4-e298a7fc28b7'], { subgraphNode2: { foo: 'hi! foobar' } }]
    [[], { node2: { foo: 'hi! foobar' } }]
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Send`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L285) (class in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`set`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L84) (function in checkpoint)
