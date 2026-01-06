## Run the agent

agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)
```

1. Define a tool for the agent to use. Tools can be defined as vanilla Python functions. For more advanced tool usage and customization, check the [tools](../how-tos/tool-calling.md) page.
2. Provide a language model for the agent to use. To learn more about configuring language models for the agents, check the [models](./models.md) page.
3. Provide a list of tools for the model to use.
4. Provide a system prompt (instructions) to the language model used by the agent.
   :::

:::js
To create an agent, use [`createReactAgent`](https://langchain-ai.github.io/langgraphjs/reference/functions/langgraph_prebuilt.createReactAgent.html):

```typescript
import { ChatAnthropic } from "@langchain/anthropic";
import { createReactAgent } from "@langchain/langgraph/prebuilt";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

const getWeather = tool(
  // (1)!
  async ({ city }) => {
    return `It's always sunny in ${city}!`;
  },
  {
    name: "get_weather",
    description: "Get weather for a given city.",
    schema: z.object({
      city: z.string().describe("The city to get weather for"),
    }),
  }
);

const agent = createReactAgent({
  llm: new ChatAnthropic({ model: "anthropic:claude-3-5-sonnet-latest" }), // (2)!
  tools: [getWeather], // (3)!
  stateModifier: "You are a helpful assistant", // (4)!
});

// Run the agent
await agent.invoke({
  messages: [{ role: "user", content: "what is the weather in sf" }],
});
```

1. Define a tool for the agent to use. Tools can be defined using the `tool` function. For more advanced tool usage and customization, check the [tools](./tools.md) page.
2. Provide a language model for the agent to use. To learn more about configuring language models for the agents, check the [models](./models.md) page.
3. Provide a list of tools for the model to use.
4. Provide a system prompt (instructions) to the language model used by the agent.
   :::

### Source References

- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`prompt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L566) (function in prebuilt)
- [`get_weather`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L6455) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`list`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L174) (function in checkpoint)
- [`Assistant`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L242) (class in sdk-py)
