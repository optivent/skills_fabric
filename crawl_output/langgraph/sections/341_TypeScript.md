## TypeScript

The `useStream()` hook is friendly for apps written in TypeScript and you can specify types for the state to get better type safety and IDE support.

```tsx
// Define your types
type State = {
  messages: Message[];
  context?: Record<string, unknown>;
};

// Use them with the hook
const thread = useStream<State>({
  apiUrl: "http://localhost:2024",
  assistantId: "agent",
  messagesKey: "messages",
});
```

You can also optionally specify types for different scenarios, such as:

- `ConfigurableType`: Type for the `config.configurable` property (default: `Record<string, unknown>`)
- `InterruptType`: Type for the interrupt value - i.e. contents of `interrupt(...)` function (default: `unknown`)
- `CustomEventType`: Type for the custom events (default: `unknown`)
- `UpdateType`: Type for the submit function (default: `Partial<State>`)

```tsx
const thread = useStream<
  State,
  {
    UpdateType: {
      messages: Message[] | Message;
      context?: Record<string, unknown>;
    };
    InterruptType: string;
    CustomEventType: {
      type: "progress" | "debug";
      payload: unknown;
    };
    ConfigurableType: {
      model: string;
    };
  }
>({
  apiUrl: "http://localhost:2024",
  assistantId: "agent",
  messagesKey: "messages",
});
```

If you're using LangGraph.js, you can also reuse your graph's annotation types. However, make sure to only import the types of the annotation schema in order to avoid importing the entire LangGraph.js runtime (i.e. via `import type { ... }` directive).

```tsx
import {
  Annotation,
  MessagesAnnotation,
  type StateType,
  type UpdateType,
} from "@langchain/langgraph/web";

const AgentState = Annotation.Root({
  ...MessagesAnnotation.spec,
  context: Annotation<string>(),
});

const thread = useStream<
  StateType<typeof AgentState.spec>,
  { UpdateType: UpdateType<typeof AgentState.spec> }
>({
  apiUrl: "http://localhost:2024",
  assistantId: "agent",
  messagesKey: "messages",
});
```

### Source References

- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`AgentState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/example_app/example_graph.py#L12) (class in langgraph)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`Assistant`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L242) (class in sdk-py)
- [`Interrupt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L157) (class in langgraph)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
