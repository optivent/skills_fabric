## Run the evaluator

result = evaluator(
    outputs=outputs, reference_outputs=reference_outputs
)
```

:::

:::js

```typescript
import { createTrajectoryMatchEvaluator } from "agentevals/trajectory/match";

const outputs = [
  {
    role: "assistant",
    tool_calls: [
      {
        function: {
          name: "get_weather",
          arguments: JSON.stringify({ city: "san francisco" }),
        },
      },
      {
        function: {
          name: "get_directions",
          arguments: JSON.stringify({ destination: "presidio" }),
        },
      },
    ],
  },
];

const referenceOutputs = [
  {
    role: "assistant",
    tool_calls: [
      {
        function: {
          name: "get_weather",
          arguments: JSON.stringify({ city: "san francisco" }),
        },
      },
    ],
  },
];

// Create the evaluator
const evaluator = createTrajectoryMatchEvaluator({
  // Specify how the trajectories will be compared. `superset` will accept output trajectory as valid if it's a superset of the reference one. Other options include: strict, unordered and subset
  trajectoryMatchMode: "superset", // (1)!
});

// Run the evaluator
const result = evaluator({
  outputs: outputs,
  referenceOutputs: referenceOutputs,
});
```

:::

1. Specify how the trajectories will be compared. `superset` will accept output trajectory as valid if it's a superset of the reference one. Other options include: [strict](https://github.com/langchain-ai/agentevals?tab=readme-ov-file#strict-match), [unordered](https://github.com/langchain-ai/agentevals?tab=readme-ov-file#unordered-match) and [subset](https://github.com/langchain-ai/agentevals?tab=readme-ov-file#subset-and-superset-match)

As a next step, learn more about how to [customize trajectory match evaluator](https://github.com/langchain-ai/agentevals?tab=readme-ov-file#agent-trajectory-match).

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`get_weather`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L6455) (function in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`Assistant`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L242) (class in sdk-py)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`read`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1044) (class in sdk-py)
