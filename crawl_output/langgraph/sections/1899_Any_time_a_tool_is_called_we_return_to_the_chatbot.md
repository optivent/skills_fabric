## Any time a tool is called, we return to the chatbot to decide the next step

graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()
```

!!! note

    You can replace this with the prebuilt [tools_condition](https://langchain-ai.github.io/langgraph/reference/prebuilt/#tools_condition) to be more concise.

:::

:::js

```typescript
import { END, START } from "@langchain/langgraph";

const routeTools = (state: z.infer<typeof State>) => {
  /**
   * Use as conditional edge to route to the ToolNode if the last message
   * has tool calls.
   */
  const lastMessage = state.messages.at(-1);
  if (
    lastMessage &&
    isAIMessage(lastMessage) &&
    lastMessage.tool_calls?.length
  ) {
    return "tools";
  }

  /** Otherwise, route to the end. */
  return END;
};

const graph = new StateGraph(State)
  .addNode("chatbot", chatbot)

  // The `routeTools` function returns "tools" if the chatbot asks to use a tool, and "END" if
  // it is fine directly responding. This conditional routing defines the main agent loop.
  .addNode("tools", createToolNode(tools))

  // Start the graph with the chatbot
  .addEdge(START, "chatbot")

  // The `routeTools` function returns "tools" if the chatbot asks to use a tool, and "END" if
  // it is fine directly responding.
  .addConditionalEdges("chatbot", routeTools, ["tools", END])

  // Any time a tool is called, we need to return to the chatbot
  .addEdge("tools", "chatbot")
  .compile();
```

!!! note

    You can replace this with the prebuilt [toolsCondition](https://langchain-ai.github.io/langgraphjs/reference/functions/langgraph_prebuilt.toolsCondition.html) to be more concise.

:::

### Source References

- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`ToolNode`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L610) (class in prebuilt)
- [`tools_condition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L8365) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`time`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/id.py#L61) (function in checkpoint)
- [`main`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6527) (function in langgraph)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
