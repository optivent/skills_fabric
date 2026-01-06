## highlight-next-line

response["structured_response"]
```

1.  When `response_format` is provided, a separate step is added at the end of the agent loop: agent message history is passed to an LLM with structured output to generate a structured response.

        To provide a system prompt to this LLM, use a tuple `(prompt, schema)`, e.g., `response_format=(prompt, WeatherResponse)`.

    :::

:::js
To produce structured responses conforming to a schema, use the `responseFormat` parameter. The schema can be defined with a `Zod` schema. The result will be accessible via the `structuredResponse` field.

```typescript
import { z } from "zod";
import { createReactAgent } from "@langchain/langgraph/prebuilt";

const WeatherResponse = z.object({
  conditions: z.string(),
});

const agent = createReactAgent({
  llm: "anthropic:claude-3-5-sonnet-latest",
  tools: [getWeather],
  // highlight-next-line
  responseFormat: WeatherResponse, // (1)!
});

const response = await agent.invoke({
  messages: [{ role: "user", content: "what is the weather in sf" }],
});

// highlight-next-line
response.structuredResponse;
```

1.  When `responseFormat` is provided, a separate step is added at the end of the agent loop: agent message history is passed to an LLM with structured output to generate a structured response.

        To provide a system prompt to this LLM, use an object `{ prompt, schema }`, e.g., `responseFormat: { prompt, schema: WeatherResponse }`.

    :::

!!! Note "LLM post-processing"

    Structured output requires an additional call to the LLM to format the response according to the schema.

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`ResponseFormat`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent_graph.py#L28) (class in prebuilt)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`prompt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L566) (function in prebuilt)
- [`WeatherResponse`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1994) (class in prebuilt)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
