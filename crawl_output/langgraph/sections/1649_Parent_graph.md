## Parent graph

builder = StateGraph(State)
builder.add_node("node_1", subgraph)
builder.add_edge(START, "node_1")
graph = builder.compile()
```
:::

:::js
1. Define the subgraph workflow (`subgraphBuilder` in the example below) and compile it
2. Pass compiled subgraph to the `.addNode` method when defining the parent graph workflow

```typescript
import { StateGraph, START } from "@langchain/langgraph";
import { z } from "zod";

const State = z.object({
  foo: z.string(),
});

// Subgraph
const subgraphBuilder = new StateGraph(State)
  .addNode("subgraphNode1", (state) => {
    return { foo: "hi! " + state.foo };
  })
  .addEdge(START, "subgraphNode1");

const subgraph = subgraphBuilder.compile();

// Parent graph
const builder = new StateGraph(State)
  .addNode("node1", subgraph)
  .addEdge(START, "node1");

const graph = builder.compile();
```
:::

??? example "Full example: shared state schemas"

    :::python
    ```python
    from typing_extensions import TypedDict
    from langgraph.graph.state import StateGraph, START

    # Define subgraph
    class SubgraphState(TypedDict):
        foo: str  # (1)! 
        bar: str  # (2)!
    
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
    
    for chunk in graph.stream({"foo": "foo"}):
        print(chunk)
    ```

    1. This key is shared with the parent graph state
    2. This key is private to the `SubgraphState` and is not visible to the parent graph
    
    ```
    {'node_1': {'foo': 'hi! foo'}}
    {'node_2': {'foo': 'hi! foobar'}}
    ```
    :::

    :::js
    ```typescript
    import { StateGraph, START } from "@langchain/langgraph";
    import { z } from "zod";

    // Define subgraph
    const SubgraphState = z.object({
      foo: z.string(),  // (1)! 
      bar: z.string(),  // (2)!
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
    
    for await (const chunk of await graph.stream({ foo: "foo" })) {
      console.log(chunk);
    }
    ```

    3. This key is shared with the parent graph state
    4. This key is private to the `SubgraphState` and is not visible to the parent graph
    
    ```
    { node1: { foo: 'hi! foo' } }
    { node2: { foo: 'hi! foobar' } }
    ```
    :::

### Source References

- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Send`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L285) (class in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`dict`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L151) (function in checkpoint)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`up`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L3118) (function in langgraph)
