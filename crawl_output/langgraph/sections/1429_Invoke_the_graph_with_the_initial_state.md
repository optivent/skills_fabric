## Invoke the graph with the initial state

response = graph.invoke(
    {
        "a": "set at start",
    }
)

print()
print(f"Output of graph invocation: {response}")
```

```
Entered node `node_1`:
	Input: {'a': 'set at start'}.
	Returned: {'private_data': 'set by node_1'}
Entered node `node_2`:
	Input: {'private_data': 'set by node_1'}.
	Returned: {'a': 'set by node_2'}
Entered node `node_3`:
	Input: {'a': 'set by node_2'}.
	Returned: {'a': 'set by node_3'}

Output of graph invocation: {'a': 'set by node_3'}
```
:::

:::js
```typescript
import { StateGraph, START, END } from "@langchain/langgraph";
import { z } from "zod";

// The overall state of the graph (this is the public state shared across nodes)
const OverallState = z.object({
  a: z.string(),
});

// Output from node1 contains private data that is not part of the overall state
const Node1Output = z.object({
  privateData: z.string(),
});

// The private data is only shared between node1 and node2
const node1 = (state: z.infer<typeof OverallState>): z.infer<typeof Node1Output> => {
  const output = { privateData: "set by node1" };
  console.log(`Entered node 'node1':\n\tInput: ${JSON.stringify(state)}.\n\tReturned: ${JSON.stringify(output)}`);
  return output;
};

// Node 2 input only requests the private data available after node1
const Node2Input = z.object({
  privateData: z.string(),
});

const node2 = (state: z.infer<typeof Node2Input>): z.infer<typeof OverallState> => {
  const output = { a: "set by node2" };
  console.log(`Entered node 'node2':\n\tInput: ${JSON.stringify(state)}.\n\tReturned: ${JSON.stringify(output)}`);
  return output;
};

// Node 3 only has access to the overall state (no access to private data from node1)
const node3 = (state: z.infer<typeof OverallState>): z.infer<typeof OverallState> => {
  const output = { a: "set by node3" };
  console.log(`Entered node 'node3':\n\tInput: ${JSON.stringify(state)}.\n\tReturned: ${JSON.stringify(output)}`);
  return output;
};

// Connect nodes in a sequence
// node2 accepts private data from node1, whereas
// node3 does not see the private data.
const graph = new StateGraph({
  state: OverallState,
  nodes: {
    node1: { action: node1, output: Node1Output },
    node2: { action: node2, input: Node2Input },
    node3: { action: node3 },
  }
})
  .addEdge(START, "node1")
  .addEdge("node1", "node2")
  .addEdge("node2", "node3")
  .addEdge("node3", END)
  .compile();

// Invoke the graph with the initial state
const response = await graph.invoke({ a: "set at start" });

console.log(`\nOutput of graph invocation: ${JSON.stringify(response)}`);
```

```
Entered node 'node1':
	Input: {"a":"set at start"}.
	Returned: {"privateData":"set by node1"}
Entered node 'node2':
	Input: {"privateData":"set by node1"}.
	Returned: {"a":"set by node2"}
Entered node 'node3':
	Input: {"a":"set by node2"}.
	Returned: {"a":"set by node3"}

Output of graph invocation: {"a":"set by node3"}
```
:::

:::python

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`json`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L173) (function in sdk-py)
- [`set`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L84) (function in checkpoint)
- [`conn`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/conftest.py#L15) (function in checkpoint-postgres)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
