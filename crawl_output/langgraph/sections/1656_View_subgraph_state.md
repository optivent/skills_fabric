## View subgraph state

When you enable [persistence](../concepts/persistence.md), you can [inspect the graph state](../concepts/persistence.md#checkpoints) (checkpoint) via the appropriate method. To view the subgraph state, you can use the subgraphs option.

:::python
You can inspect the graph state via `graph.get_state(config)`. To view the subgraph state, you can use `graph.get_state(config, subgraphs=True)`.
:::

:::js
You can inspect the graph state via `graph.getState(config)`. To view the subgraph state, you can use `graph.getState(config, { subgraphs: true })`.
:::

!!! important "Available **only** when interrupted"

    Subgraph state can only be viewed **when the subgraph is interrupted**. Once you resume the graph, you won't be able to access the subgraph state.

??? example "View interrupted subgraph state"

    :::python
    ```python
    from langgraph.graph import START, StateGraph
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.types import interrupt, Command
    from typing_extensions import TypedDict
    
    class State(TypedDict):
        foo: str
    
    # Subgraph
    
    def subgraph_node_1(state: State):
        value = interrupt("Provide value:")
        return {"foo": state["foo"] + value}
    
    subgraph_builder = StateGraph(State)
    subgraph_builder.add_node(subgraph_node_1)
    subgraph_builder.add_edge(START, "subgraph_node_1")
    
    subgraph = subgraph_builder.compile()
    
    # Parent graph
        
    builder = StateGraph(State)
    builder.add_node("node_1", subgraph)
    builder.add_edge(START, "node_1")
    
    checkpointer = MemorySaver()
    graph = builder.compile(checkpointer=checkpointer)
    
    config = {"configurable": {"thread_id": "1"}}
    
    graph.invoke({"foo": ""}, config)
    parent_state = graph.get_state(config)
    subgraph_state = graph.get_state(config, subgraphs=True).tasks[0].state  # (1)!
    
    # resume the subgraph
    graph.invoke(Command(resume="bar"), config)
    ```
    
    1. This will be available only when the subgraph is interrupted. Once you resume the graph, you won't be able to access the subgraph state.
    :::

    :::js
    ```typescript
    import { StateGraph, START, MemorySaver, interrupt, Command } from "@langchain/langgraph";
    import { z } from "zod";
    
    const State = z.object({
      foo: z.string(),
    });
    
    // Subgraph
    const subgraphBuilder = new StateGraph(State)
      .addNode("subgraphNode1", (state) => {
        const value = interrupt("Provide value:");
        return { foo: state.foo + value };
      })
      .addEdge(START, "subgraphNode1");
    
    const subgraph = subgraphBuilder.compile();
    
    // Parent graph
    const builder = new StateGraph(State)
      .addNode("node1", subgraph)
      .addEdge(START, "node1");
    
    const checkpointer = new MemorySaver();
    const graph = builder.compile({ checkpointer });
    
    const config = { configurable: { thread_id: "1" } };
    
    await graph.invoke({ foo: "" }, config);
    const parentState = await graph.getState(config);
    const subgraphState = (await graph.getState(config, { subgraphs: true })).tasks[0].state; // (1)!
    
    // resume the subgraph
    await graph.invoke(new Command({ resume: "bar" }), config);
    ```
    
    2. This will be available only when the subgraph is interrupted. Once you resume the graph, you won't be able to access the subgraph state.
    :::

### Source References

- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`get_state`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L1235) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`Interrupt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L157) (class in langgraph)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
- [`Command`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L364) (class in langgraph)
