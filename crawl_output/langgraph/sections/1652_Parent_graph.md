## Parent graph

class State(TypedDict):
    foo: str

def call_subgraph(state: State):
    subgraph_output = subgraph.invoke({"bar": state["foo"]})  # (1)!
    return {"foo": subgraph_output["bar"]}  # (2)!

builder = StateGraph(State)
builder.add_node("node_1", call_subgraph)
builder.add_edge(START, "node_1")
graph = builder.compile()
```

1. Transform the state to the subgraph state
2. Transform response back to the parent state
:::

:::js
```typescript
import { StateGraph, START } from "@langchain/langgraph";
import { z } from "zod";

const SubgraphState = z.object({
  bar: z.string(),
});

// Subgraph
const subgraphBuilder = new StateGraph(SubgraphState)
  .addNode("subgraphNode1", (state) => {
    return { bar: "hi! " + state.bar };
  })
  .addEdge(START, "subgraphNode1");

const subgraph = subgraphBuilder.compile();

// Parent graph
const State = z.object({
  foo: z.string(),
});

const builder = new StateGraph(State)
  .addNode("node1", async (state) => {
    const subgraphOutput = await subgraph.invoke({ bar: state.foo }); // (1)!
    return { foo: subgraphOutput.bar }; // (2)!
  })
  .addEdge(START, "node1");

const graph = builder.compile();
```

1. Transform the state to the subgraph state
2. Transform response back to the parent state
:::

??? example "Full example: different state schemas"

    :::python
    ```python
    from typing_extensions import TypedDict
    from langgraph.graph.state import StateGraph, START

    # Define subgraph
    class SubgraphState(TypedDict):
        # note that none of these keys are shared with the parent graph state
        bar: str
        baz: str
    
    def subgraph_node_1(state: SubgraphState):
        return {"baz": "baz"}
    
    def subgraph_node_2(state: SubgraphState):
        return {"bar": state["bar"] + state["baz"]}
    
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
    
    def node_2(state: ParentState):
        response = subgraph.invoke({"bar": state["foo"]})  # (1)!
        return {"foo": response["bar"]}  # (2)!
    
    
    builder = StateGraph(ParentState)
    builder.add_node("node_1", node_1)
    builder.add_node("node_2", node_2)
    builder.add_edge(START, "node_1")
    builder.add_edge("node_1", "node_2")
    graph = builder.compile()
    
    for chunk in graph.stream({"foo": "foo"}, subgraphs=True):
        print(chunk)
    ```

    1. Transform the state to the subgraph state
    2. Transform response back to the parent state

    ```
    ((), {'node_1': {'foo': 'hi! foo'}})
    (('node_2:9c36dd0f-151a-cb42-cbad-fa2f851f9ab7',), {'grandchild_1': {'my_grandchild_key': 'hi Bob, how are you'}})
    (('node_2:9c36dd0f-151a-cb42-cbad-fa2f851f9ab7',), {'grandchild_2': {'bar': 'hi! foobaz'}})
    ((), {'node_2': {'foo': 'hi! foobaz'}})
    ```
    :::

    :::js
    ```typescript
    import { StateGraph, START } from "@langchain/langgraph";
    import { z } from "zod";

    // Define subgraph
    const SubgraphState = z.object({
      // note that none of these keys are shared with the parent graph state
      bar: z.string(),
      baz: z.string(),
    });
    
    const subgraphBuilder = new StateGraph(SubgraphState)
      .addNode("subgraphNode1", (state) => {
        return { baz: "baz" };
      })
      .addNode("subgraphNode2", (state) => {
        return { bar: state.bar + state.baz };
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
      .addNode("node2", async (state) => {
        const response = await subgraph.invoke({ bar: state.foo }); // (1)!
        return { foo: response.bar }; // (2)!
      })
      .addEdge(START, "node1")
      .addEdge("node1", "node2");
    
    const graph = builder.compile();
    
    for await (const chunk of await graph.stream(
      { foo: "foo" }, 
      { subgraphs: true }
    )) {
      console.log(chunk);
    }
    ```

    3. Transform the state to the subgraph state
    4. Transform response back to the parent state

    ```
    [[], { node1: { foo: 'hi! foo' } }]
    [['node2:9c36dd0f-151a-cb42-cbad-fa2f851f9ab7'], { subgraphNode1: { baz: 'baz' } }]
    [['node2:9c36dd0f-151a-cb42-cbad-fa2f851f9ab7'], { subgraphNode2: { bar: 'hi! foobaz' } }]
    [[], { node2: { foo: 'hi! foobaz' } }]
    ```
    :::

??? example "Full example: different state schemas (two levels of subgraphs)"

    This is an example with two levels of subgraphs: parent -> child -> grandchild.

    :::python
    ```python
    # Grandchild graph
    from typing_extensions import TypedDict
    from langgraph.graph.state import StateGraph, START, END
    
    class GrandChildState(TypedDict):
        my_grandchild_key: str
    
    def grandchild_1(state: GrandChildState) -> GrandChildState:
        # NOTE: child or parent keys will not be accessible here
        return {"my_grandchild_key": state["my_grandchild_key"] + ", how are you"}
    
    
    grandchild = StateGraph(GrandChildState)
    grandchild.add_node("grandchild_1", grandchild_1)
    
    grandchild.add_edge(START, "grandchild_1")
    grandchild.add_edge("grandchild_1", END)
    
    grandchild_graph = grandchild.compile()
    
    # Child graph
    class ChildState(TypedDict):
        my_child_key: str
    
    def call_grandchild_graph(state: ChildState) -> ChildState:
        # NOTE: parent or grandchild keys won't be accessible here
        grandchild_graph_input = {"my_grandchild_key": state["my_child_key"]}  # (1)!
        grandchild_graph_output = grandchild_graph.invoke(grandchild_graph_input)
        return {"my_child_key": grandchild_graph_output["my_grandchild_key"] + " today?"}  # (2)!
    
    child = StateGraph(ChildState)
    child.add_node("child_1", call_grandchild_graph)  # (3)!
    child.add_edge(START, "child_1")
    child.add_edge("child_1", END)
    child_graph = child.compile()
    
    # Parent graph
    class ParentState(TypedDict):
        my_key: str
    
    def parent_1(state: ParentState) -> ParentState:
        # NOTE: child or grandchild keys won't be accessible here
        return {"my_key": "hi " + state["my_key"]}
    
    def parent_2(state: ParentState) -> ParentState:
        return {"my_key": state["my_key"] + " bye!"}
    
    def call_child_graph(state: ParentState) -> ParentState:
        child_graph_input = {"my_child_key": state["my_key"]}  # (4)!
        child_graph_output = child_graph.invoke(child_graph_input)
        return {"my_key": child_graph_output["my_child_key"]}  # (5)!
    
    parent = StateGraph(ParentState)
    parent.add_node("parent_1", parent_1)
    parent.add_node("child", call_child_graph)  # (6)!
    parent.add_node("parent_2", parent_2)
    
    parent.add_edge(START, "parent_1")
    parent.add_edge("parent_1", "child")
    parent.add_edge("child", "parent_2")
    parent.add_edge("parent_2", END)
    
    parent_graph = parent.compile()
    
    for chunk in parent_graph.stream({"my_key": "Bob"}, subgraphs=True):
        print(chunk)
    ```

    1. We're transforming the state from the child state channels (`my_child_key`) to the child state channels (`my_grandchild_key`)
    2. We're transforming the state from the grandchild state channels (`my_grandchild_key`) back to the child state channels (`my_child_key`)
    3. We're passing a function here instead of just compiled graph (`grandchild_graph`)
    4. We're transforming the state from the parent state channels (`my_key`) to the child state channels (`my_child_key`)
    5. We're transforming the state from the child state channels (`my_child_key`) back to the parent state channels (`my_key`)
    6. We're passing a function here instead of just a compiled graph (`child_graph`)

    ```
    ((), {'parent_1': {'my_key': 'hi Bob'}})
    (('child:2e26e9ce-602f-862c-aa66-1ea5a4655e3b', 'child_1:781bb3b1-3971-84ce-810b-acf819a03f9c'), {'grandchild_1': {'my_grandchild_key': 'hi Bob, how are you'}})
    (('child:2e26e9ce-602f-862c-aa66-1ea5a4655e3b',), {'child_1': {'my_child_key': 'hi Bob, how are you today?'}})
    ((), {'child': {'my_key': 'hi Bob, how are you today?'}})
    ((), {'parent_2': {'my_key': 'hi Bob, how are you today? bye!'}})
    ```
    :::

    :::js
    ```typescript
    import { StateGraph, START, END } from "@langchain/langgraph";
    import { z } from "zod";

    // Grandchild graph
    const GrandChildState = z.object({
      myGrandchildKey: z.string(),
    });
    
    const grandchild = new StateGraph(GrandChildState)
      .addNode("grandchild1", (state) => {
        // NOTE: child or parent keys will not be accessible here
        return { myGrandchildKey: state.myGrandchildKey + ", how are you" };
      })
      .addEdge(START, "grandchild1")
      .addEdge("grandchild1", END);
    
    const grandchildGraph = grandchild.compile();
    
    // Child graph
    const ChildState = z.object({
      myChildKey: z.string(),
    });
    
    const child = new StateGraph(ChildState)
      .addNode("child1", async (state) => {
        // NOTE: parent or grandchild keys won't be accessible here
        const grandchildGraphInput = { myGrandchildKey: state.myChildKey }; // (1)!
        const grandchildGraphOutput = await grandchildGraph.invoke(grandchildGraphInput);
        return { myChildKey: grandchildGraphOutput.myGrandchildKey + " today?" }; // (2)!
      }) // (3)!
      .addEdge(START, "child1")
      .addEdge("child1", END);
    
    const childGraph = child.compile();
    
    // Parent graph
    const ParentState = z.object({
      myKey: z.string(),
    });
    
    const parent = new StateGraph(ParentState)
      .addNode("parent1", (state) => {
        // NOTE: child or grandchild keys won't be accessible here
        return { myKey: "hi " + state.myKey };
      })
      .addNode("child", async (state) => {
        const childGraphInput = { myChildKey: state.myKey }; // (4)!
        const childGraphOutput = await childGraph.invoke(childGraphInput);
        return { myKey: childGraphOutput.myChildKey }; // (5)!
      }) // (6)!
      .addNode("parent2", (state) => {
        return { myKey: state.myKey + " bye!" };
      })
      .addEdge(START, "parent1")
      .addEdge("parent1", "child")
      .addEdge("child", "parent2")
      .addEdge("parent2", END);
    
    const parentGraph = parent.compile();
    
    for await (const chunk of await parentGraph.stream(
      { myKey: "Bob" }, 
      { subgraphs: true }
    )) {
      console.log(chunk);
    }
    ```

    7. We're transforming the state from the child state channels (`myChildKey`) to the grandchild state channels (`myGrandchildKey`)
    8. We're transforming the state from the grandchild state channels (`myGrandchildKey`) back to the child state channels (`myChildKey`)
    9. We're passing a function here instead of just compiled graph (`grandchildGraph`)
    10. We're transforming the state from the parent state channels (`myKey`) to the child state channels (`myChildKey`)
    11. We're transforming the state from the child state channels (`myChildKey`) back to the parent state channels (`myKey`)
    12. We're passing a function here instead of just a compiled graph (`childGraph`)

    ```
    [[], { parent1: { myKey: 'hi Bob' } }]
    [['child:2e26e9ce-602f-862c-aa66-1ea5a4655e3b', 'child1:781bb3b1-3971-84ce-810b-acf819a03f9c'], { grandchild1: { myGrandchildKey: 'hi Bob, how are you' } }]
    [['child:2e26e9ce-602f-862c-aa66-1ea5a4655e3b'], { child1: { myChildKey: 'hi Bob, how are you today?' } }]
    [[], { child: { myKey: 'hi Bob, how are you today?' } }]
    [[], { parent2: { myKey: 'hi Bob, how are you today? bye!' } }]
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`dict`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L151) (function in checkpoint)
- [`sync`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L556) (function in checkpoint)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
