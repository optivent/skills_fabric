## INVALID_CONCURRENT_GRAPH_UPDATE

A LangGraph [`StateGraph`](https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.state.StateGraph) received concurrent updates to its state from multiple nodes to a state property that doesn't
support it.

One way this can occur is if you are using a [fanout](https://langchain-ai.github.io/langgraph/how-tos/map-reduce/)
or other parallel execution in your graph and you have defined a graph like this:

:::python

```python hl_lines="2"
class State(TypedDict):
    some_key: str

def node(state: State):
    return {"some_key": "some_string_value"}

def other_node(state: State):
    return {"some_key": "some_string_value"}


builder = StateGraph(State)
builder.add_node(node)
builder.add_node(other_node)
builder.add_edge(START, "node")
builder.add_edge(START, "other_node")
graph = builder.compile()
```

:::

:::js

```typescript hl_lines="2"
import { StateGraph, Annotation, START } from "@langchain/langgraph";
import { z } from "zod";

const State = z.object({
  someKey: z.string(),
});

const builder = new StateGraph(State)
  .addNode("node", (state) => {
    return { someKey: "some_string_value" };
  })
  .addNode("otherNode", (state) => {
    return { someKey: "some_string_value" };
  })
  .addEdge(START, "node")
  .addEdge(START, "otherNode");

const graph = builder.compile();
```

:::

:::python
If a node in the above graph returns `{ "some_key": "some_string_value" }`, this will overwrite the state value for `"some_key"` with `"some_string_value"`.
However, if multiple nodes in e.g. a fanout within a single step return values for `"some_key"`, the graph will throw this error because
there is uncertainty around how to update the internal state.
:::

:::js
If a node in the above graph returns `{ someKey: "some_string_value" }`, this will overwrite the state value for `someKey` with `"some_string_value"`.
However, if multiple nodes in e.g. a fanout within a single step return values for `someKey`, the graph will throw this error because
there is uncertainty around how to update the internal state.
:::

To get around this, you can define a reducer that combines multiple values:

:::python

```python hl_lines="5-6"
import operator
from typing import Annotated

class State(TypedDict):
    # The operator.add reducer fn makes this append-only
    some_key: Annotated[list, operator.add]
```

:::

:::js

```typescript hl_lines="4-7"
import { withLangGraph } from "@langchain/langgraph";
import { z } from "zod";

const State = z.object({
  someKey: withLangGraph(z.array(z.string()), {
    reducer: {
      fn: (existing, update) => existing.concat(update),
    },
    default: () => [],
  }),
});
```

:::

This will allow you to define logic that handles the same key returned from multiple nodes executed in parallel.

### Source References

- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`execute`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1174) (function in prebuilt)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`list`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L174) (function in checkpoint)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`Row`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L1163) (class in checkpoint-postgres)
- [`dict`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L151) (function in checkpoint)
