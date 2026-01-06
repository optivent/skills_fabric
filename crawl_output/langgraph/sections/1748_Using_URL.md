## Using URL

:::python

```python
from langgraph.pregel.remote import RemoteGraph

url = <DEPLOYMENT_URL>
graph_name = "agent"
remote_graph = RemoteGraph(graph_name, url=url)
```

:::

:::js

```ts
import { RemoteGraph } from "@langchain/langgraph/remote";

const url = `<DEPLOYMENT_URL>`;
const graphName = "agent";
const remoteGraph = new RemoteGraph({ graphId: graphName, url });
```

:::

### Source References

- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`new`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L779) (function in cli)
- [`remote_graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_remote_graph.py#L1104) (function in langgraph)
- [`a`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4642) (function in langgraph)
- [`A`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L124) (class in langgraph)
- [`agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L6229) (function in langgraph)
- [`gen`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_utils.py#L71) (function in langgraph)
- [`c`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4666) (function in langgraph)
- [`d`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4669) (function in langgraph)
