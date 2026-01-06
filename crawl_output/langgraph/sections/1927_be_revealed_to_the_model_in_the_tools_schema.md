## be revealed to the model in the tool's schema.

def human_assistance(
    name: str, birthday: str, tool_call_id: Annotated[str, InjectedToolCallId]
) -> str:
    """Request assistance from a human."""
    human_response = interrupt(
        {
            "question": "Is this correct?",
            "name": name,
            "birthday": birthday,
        },
    )
    # If the information is correct, update the state as-is.
    if human_response.get("correct", "").lower().startswith("y"):
        verified_name = name
        verified_birthday = birthday
        response = "Correct"
    # Otherwise, receive information from the human reviewer.
    else:
        verified_name = human_response.get("name", name)
        verified_birthday = human_response.get("birthday", birthday)
        response = f"Made a correction: {human_response}"

    # This time we explicitly update the state with a ToolMessage inside
    # the tool.
    state_update = {
        "name": verified_name,
        "birthday": verified_birthday,
        "messages": [ToolMessage(response, tool_call_id=tool_call_id)],
    }
    # We return a Command object in the tool to update our state.
    return Command(update=state_update)
```

:::

:::js

Now, populate the state keys inside of the `humanAssistance` tool. This allows a human to review the information before it is stored in the state. Use [`Command`](../../concepts/low_level.md#using-inside-tools) to issue a state update from inside the tool.

```typescript
import { tool } from "@langchain/core/tools";
import { ToolMessage } from "@langchain/core/messages";
import { Command, interrupt } from "@langchain/langgraph";

const humanAssistance = tool(
  async (input, config) => {
    // Note that because we are generating a ToolMessage for a state update,
    // we generally require the ID of the corresponding tool call.
    // This is available in the tool's config.
    const toolCallId = config?.toolCall?.id as string | undefined;
    if (!toolCallId) throw new Error("Tool call ID is required");

    const humanResponse = await interrupt({
      question: "Is this correct?",
      name: input.name,
      birthday: input.birthday,
    });

    // We explicitly update the state with a ToolMessage inside the tool.
    const stateUpdate = (() => {
      // If the information is correct, update the state as-is.
      if (humanResponse.correct?.toLowerCase().startsWith("y")) {
        return {
          name: input.name,
          birthday: input.birthday,
          messages: [
            new ToolMessage({ content: "Correct", tool_call_id: toolCallId }),
          ],
        };
      }

      // Otherwise, receive information from the human reviewer.
      return {
        name: humanResponse.name || input.name,
        birthday: humanResponse.birthday || input.birthday,
        messages: [
          new ToolMessage({
            content: `Made a correction: ${JSON.stringify(humanResponse)}`,
            tool_call_id: toolCallId,
          }),
        ],
      };
    })();

    // We return a Command object in the tool to update our state.
    return new Command({ update: stateUpdate });
  },
  {
    name: "humanAssistance",
    description: "Request assistance from a human.",
    schema: z.object({
      name: z.string().describe("The name of the entity"),
      birthday: z.string().describe("The birthday/release date of the entity"),
    }),
  }
);
```

:::

The rest of the graph stays the same.

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`human_assistance`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L605) (function in prebuilt)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`HumanResponse`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/interrupt.py#L87) (class in prebuilt)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
