## highlight-next-line

checkpointer = InMemorySaver() # (2)!

agent = create_react_agent(
    model="anthropic:claude-3-5-sonnet-latest",
    tools=[book_hotel],
    # highlight-next-line
    checkpointer=checkpointer, # (3)!
)
```

1. The @[`interrupt` function][interrupt] pauses the agent graph at a specific node. In this case, we call `interrupt()` at the beginning of the tool function, which pauses the graph at the node that executes the tool. The information inside `interrupt()` (e.g., tool calls) can be presented to a human, and the graph can be resumed with the user input (tool call approval, edit or feedback).
2. The `InMemorySaver` is used to store the agent state at every step in the tool calling loop. This enables [short-term memory](../memory/add-memory.md#add-short-term-memory) and [human-in-the-loop](../../concepts/human_in_the_loop.md) capabilities. In this example, we use `InMemorySaver` to store the agent state in memory. In a production application, the agent state will be stored in a database.
3. Initialize the agent with the `checkpointer`.
   :::

:::js

```typescript
import { MemorySaver } from "@langchain/langgraph";
import { interrupt } from "@langchain/langgraph";
import { createReactAgent } from "@langchain/langgraph/prebuilt";
import { tool } from "@langchain/core/tools";
import { z } from "zod";

// An example of a sensitive tool that requires human review / approval
const bookHotel = tool(
  async ({ hotelName }) => {
    // highlight-next-line
    const response = interrupt(
      // (1)!
      `Trying to call \`bookHotel\` with args {"hotelName": "${hotelName}"}. ` +
        "Please approve or suggest edits."
    );
    if (response.type === "accept") {
      // Continue with original args
    } else if (response.type === "edit") {
      hotelName = response.args.hotelName;
    } else {
      throw new Error(`Unknown response type: ${response.type}`);
    }
    return `Successfully booked a stay at ${hotelName}.`;
  },
  {
    name: "bookHotel",
    description: "Book a hotel",
    schema: z.object({
      hotelName: z.string(),
    }),
  }
);

// highlight-next-line
const checkpointer = new MemorySaver(); // (2)!

const agent = createReactAgent({
  llm: model,
  tools: [bookHotel],
  // highlight-next-line
  checkpointSaver: checkpointer, // (3)!
});
```

1. The @[`interrupt` function][interrupt] pauses the agent graph at a specific node. In this case, we call `interrupt()` at the beginning of the tool function, which pauses the graph at the node that executes the tool. The information inside `interrupt()` (e.g., tool calls) can be presented to a human, and the graph can be resumed with the user input (tool call approval, edit or feedback).
2. The `MemorySaver` is used to store the agent state at every step in the tool calling loop. This enables [short-term memory](../memory/add-memory.md#add-short-term-memory) and [human-in-the-loop](../../concepts/human_in_the_loop.md) capabilities. In this example, we use `MemorySaver` to store the agent state in memory. In a production application, the agent state will be stored in a database.
3. Initialize the agent with the `checkpointSaver`.
   :::

Run the agent with the `stream()` method, passing the `config` object to specify the thread ID. This allows the agent to resume the same conversation on future invocations.

:::python

```python
config = {
   "configurable": {
      # highlight-next-line
      "thread_id": "1"
   }
}

for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "book a stay at McKittrick hotel"}]},
    # highlight-next-line
    config
):
    print(chunk)
    print("\n")
```

:::

:::js

```typescript
const config = {
  configurable: {
    // highlight-next-line
    thread_id: "1",
  },
};

const stream = await agent.stream(
  { messages: [{ role: "user", content: "book a stay at McKittrick hotel" }] },
  // highlight-next-line
  config
);

for await (const chunk of stream) {
  console.log(chunk);
  console.log("\n");
}
```

:::

> You should see that the agent runs until it reaches the `interrupt()` call, at which point it pauses and waits for human input.

Resume the agent with a `Command` to continue based on human input.

:::python

```python
from langgraph.types import Command

for chunk in agent.stream(
    # highlight-next-line
    Command(resume={"type": "accept"}),  # (1)!
    # Command(resume={"type": "edit", "args": {"hotel_name": "McKittrick Hotel"}}),
    config
):
    print(chunk)
    print("\n")
```

1. The @[`interrupt` function][interrupt] is used in conjunction with the @[`Command`][Command] object to resume the graph with a value provided by the human.
   :::

:::js

```typescript
import { Command } from "@langchain/langgraph";

const resumeStream = await agent.stream(
  // highlight-next-line
  new Command({ resume: { type: "accept" } }), // (1)!
  // new Command({ resume: { type: "edit", args: { hotelName: "McKittrick Hotel" } } }),
  config
);

for await (const chunk of resumeStream) {
  console.log(chunk);
  console.log("\n");
}
```

1. The @[`interrupt` function][interrupt] is used in conjunction with the @[`Command`][Command] object to resume the graph with a value provided by the human.
   :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`execute`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1174) (function in prebuilt)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
