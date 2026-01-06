## 4. Prompt the chatbot

Now, prompt the chatbot with a question that will engage the new `human_assistance` tool:

:::python

```python
user_input = "I need some expert guidance for building an AI agent. Could you request assistance for me?"
config = {"configurable": {"thread_id": "1"}}

events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
```

```
================================ Human Message =================================

I need some expert guidance for building an AI agent. Could you request assistance for me?
================================== Ai Message ==================================

[{'text': "Certainly! I'd be happy to request expert assistance for you regarding building an AI agent. To do this, I'll use the human_assistance function to relay your request. Let me do that for you now.", 'type': 'text'}, {'id': 'toolu_01ABUqneqnuHNuo1vhfDFQCW', 'input': {'query': 'A user is requesting expert guidance for building an AI agent. Could you please provide some expert advice or resources on this topic?'}, 'name': 'human_assistance', 'type': 'tool_use'}]
Tool Calls:
  human_assistance (toolu_01ABUqneqnuHNuo1vhfDFQCW)
 Call ID: toolu_01ABUqneqnuHNuo1vhfDFQCW
  Args:
    query: A user is requesting expert guidance for building an AI agent. Could you please provide some expert advice or resources on this topic?
```

:::

:::js

```typescript
import { isAIMessage } from "@langchain/core/messages";

const userInput =
  "I need some expert guidance for building an AI agent. Could you request assistance for me?";

const events = await graph.stream(
  { messages: [{ role: "user", content: userInput }] },
  { configurable: { thread_id: "1" }, streamMode: "values" }
  { configurable: { thread_id: "1" }, streamMode: "values" }
);

for await (const event of events) {
  if ("messages" in event) {
    const lastMessage = event.messages.at(-1);
    console.log(`[${lastMessage?.getType()}]: ${lastMessage?.text}`);

    if (
      lastMessage &&
      isAIMessage(lastMessage) &&
      lastMessage.tool_calls?.length
    ) {
    const lastMessage = event.messages.at(-1);
    console.log(`[${lastMessage?.getType()}]: ${lastMessage?.text}`);

    if (
      lastMessage &&
      isAIMessage(lastMessage) &&
      lastMessage.tool_calls?.length
    ) {
      console.log("Tool calls:", lastMessage.tool_calls);
    }
  }
}
```

```
[human]: I need some expert guidance for building an AI agent. Could you request assistance for me?
[ai]: I'll help you request human assistance for guidance on building an AI agent.
[ai]: I'll help you request human assistance for guidance on building an AI agent.
Tool calls: [
  {
    name: 'humanAssistance',
    args: {
      query: 'I would like expert guidance on building an AI agent. Could you please provide assistance with this topic?'
      query: 'I would like expert guidance on building an AI agent. Could you please provide assistance with this topic?'
    },
    id: 'toolu_01Bpxc8rFVMhSaRosS6b85Ts',
    type: 'tool_call'
    id: 'toolu_01Bpxc8rFVMhSaRosS6b85Ts',
    type: 'tool_call'
  }
]
```

:::

The chatbot generated a tool call, but then execution has been interrupted. If you inspect the graph state, you see that it stopped at the tools node:

:::python

```python
snapshot = graph.get_state(config)
snapshot.next
```

```
('tools',)
```

:::

:::js

```typescript
const snapshot = await graph.getState({ configurable: { thread_id: "1" } });
snapshot.next;
const snapshot = await graph.getState({ configurable: { thread_id: "1" } });
snapshot.next;
```

```json
["tools"]
```

:::

!!! info Additional information

    :::python

    Take a closer look at the `human_assistance` tool:

    ```python
    @tool
    def human_assistance(query: str) -> str:
        """Request assistance from a human."""
        human_response = interrupt({"query": query})
        return human_response["data"]
    ```

    Similar to Python's built-in `input()` function, calling `interrupt` inside the tool will pause execution. Progress is persisted based on the [checkpointer](../../concepts/persistence.md#checkpointer-libraries); so if it is persisting with Postgres, it can resume at any time as long as the database is alive. In this example, it is persisting with the in-memory checkpointer and can resume any time if the Python kernel is running.
    :::

    :::js

    Take a closer look at the `humanAssistance` tool:

    ```typescript hl_lines="3"
    const humanAssistance = tool(
      async ({ query }) => {
        const humanResponse = interrupt({ query });
        return humanResponse.data;
      },
      {
        name: "humanAssistance",
        description: "Request assistance from a human.",
        schema: z.object({
          query: z.string().describe("Human readable question for the human"),
        }),
      },
    );

    Take a closer look at the `humanAssistance` tool:

    ```typescript hl_lines="3"
    const humanAssistance = tool(
      async ({ query }) => {
        const humanResponse = interrupt({ query });
        return humanResponse.data;
      },
      {
        name: "humanAssistance",
        description: "Request assistance from a human.",
        schema: z.object({
          query: z.string().describe("Human readable question for the human"),
        }),
      },
    );
    ```

    Calling `interrupt` inside the tool will pause execution. Progress is persisted based on the [checkpointer](../../concepts/persistence.md#checkpointer-libraries); so if it is persisting with Postgres, it can resume at any time as long as the database is alive. In this example, it is persisting with the in-memory checkpointer and can resume any time if the JavaScript runtime is running.
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`prompt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L566) (function in prebuilt)
- [`human_assistance`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L605) (function in prebuilt)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`HumanResponse`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/interrupt.py#L87) (class in prebuilt)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
