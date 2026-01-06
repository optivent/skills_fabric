## highlight-next-line

builder.add_conditional_edges("a", conditional_edge)

graph = builder.compile()
```

```python
from IPython.display import Image, display

display(Image(graph.get_graph().draw_mermaid_png()))
```

![Conditional branching graph](assets/graph_api_image_5.png)

```python
result = graph.invoke({"aggregate": []})
print(result)
```

```
Adding "A" to []
Adding "C" to ['A']
{'aggregate': ['A', 'C'], 'which': 'c'}
```
:::

:::js
If your fan-out should vary at runtime based on the state, you can use [addConditionalEdges](https://langchain-ai.github.io/langgraph/reference/graphs.md#langgraph.graph.StateGraph.addConditionalEdges) to select one or more paths using the graph state. See example below, where node `a` generates a state update that determines the following node.

```typescript
import "@langchain/langgraph/zod";
import { StateGraph, START, END } from "@langchain/langgraph";
import { z } from "zod";

const State = z.object({
  aggregate: z.array(z.string()).langgraph.reducer((x, y) => x.concat(y)),
  // Add a key to the state. We will set this key to determine
  // how we branch.
  which: z.string().langgraph.reducer((x, y) => y ?? x),
});

const nodeA = (state: z.infer<typeof State>) => {
  console.log(`Adding "A" to ${state.aggregate}`);
  // highlight-next-line
  return { aggregate: ["A"], which: "c" };
};

const nodeB = (state: z.infer<typeof State>) => {
  console.log(`Adding "B" to ${state.aggregate}`);
  return { aggregate: ["B"] };
};

const nodeC = (state: z.infer<typeof State>) => {
  console.log(`Adding "C" to ${state.aggregate}`);
  return { aggregate: ["C"] };
};

const conditionalEdge = (state: z.infer<typeof State>): "b" | "c" => {
  // Fill in arbitrary logic here that uses the state
  // to determine the next node
  return state.which as "b" | "c";
};

// highlight-next-line
const graph = new StateGraph(State)
  .addNode("a", nodeA)  
  .addNode("b", nodeB)
  .addNode("c", nodeC)
  .addEdge(START, "a")
  .addEdge("b", END)
  .addEdge("c", END)
  .addConditionalEdges("a", conditionalEdge)
  .compile();
```

```typescript
import * as fs from "node:fs/promises";

const drawableGraph = await graph.getGraphAsync();
const image = await drawableGraph.drawMermaidPng();
const imageBuffer = new Uint8Array(await image.arrayBuffer());

await fs.writeFile("graph.png", imageBuffer);
```

```typescript
const result = await graph.invoke({ aggregate: [] });
console.log(result);
```

```
Adding "A" to []
Adding "C" to ['A']
{ aggregate: ['A', 'C'], which: 'c' }
```
:::

!!! tip

    Your conditional edges can route to multiple destination nodes. For example:

    :::python
    ```python
    def route_bc_or_cd(state: State) -> Sequence[str]:
        if state["which"] == "cd":
            return ["c", "d"]
        return ["b", "c"]
    ```
    :::

    :::js
    ```typescript
    const routeBcOrCd = (state: z.infer<typeof State>): string[] => {
      if (state.which === "cd") {
        return ["c", "d"];
      }
      return ["b", "c"];
    };
    ```
    :::

### Source References

- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`get_graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L704) (function in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`set`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L84) (function in checkpoint)
