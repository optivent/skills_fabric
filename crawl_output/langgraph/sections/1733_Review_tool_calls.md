## Review tool calls

To review tool calls before execution, we add a `review_tool_call` function that calls [`interrupt`](../how-tos/human_in_the_loop/add-human-in-the-loop.md#pause-using-interrupt). When this function is called, execution will be paused until we issue a command to resume it.

Given a tool call, our function will `interrupt` for human review. At that point we can either:

- Accept the tool call
- Revise the tool call and continue
- Generate a custom tool message (e.g., instructing the model to re-format its tool call)

:::python

```python
from typing import Union

def review_tool_call(tool_call: ToolCall) -> Union[ToolCall, ToolMessage]:
    """Review a tool call, returning a validated version."""
    human_review = interrupt(
        {
            "question": "Is this correct?",
            "tool_call": tool_call,
        }
    )
    review_action = human_review["action"]
    review_data = human_review.get("data")
    if review_action == "continue":
        return tool_call
    elif review_action == "update":
        updated_tool_call = {**tool_call, **{"args": review_data}}
        return updated_tool_call
    elif review_action == "feedback":
        return ToolMessage(
            content=review_data, name=tool_call["name"], tool_call_id=tool_call["id"]
        )
```

:::

:::js

```typescript
import { ToolCall } from "@langchain/core/messages/tool";
import { ToolMessage } from "@langchain/core/messages";

function reviewToolCall(toolCall: ToolCall): ToolCall | ToolMessage {
  // Review a tool call, returning a validated version
  const humanReview = interrupt({
    question: "Is this correct?",
    tool_call: toolCall,
  });

  const reviewAction = humanReview.action;
  const reviewData = humanReview.data;

  if (reviewAction === "continue") {
    return toolCall;
  } else if (reviewAction === "update") {
    const updatedToolCall = { ...toolCall, args: reviewData };
    return updatedToolCall;
  } else if (reviewAction === "feedback") {
    return new ToolMessage({
      content: reviewData,
      name: toolCall.name,
      tool_call_id: toolCall.id,
    });
  }

  throw new Error(`Unknown review action: ${reviewAction}`);
}
```

:::

We can now update our [entrypoint](../concepts/functional_api.md#entrypoint) to review the generated tool calls. If a tool call is accepted or revised, we execute in the same way as before. Otherwise, we just append the `ToolMessage` supplied by the human. The results of prior tasks — in this case the initial model call — are persisted, so that they are not run again following the `interrupt`.

:::python

```python
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages
from langgraph.types import Command, interrupt


checkpointer = InMemorySaver()


@entrypoint(checkpointer=checkpointer)
def agent(messages, previous):
    if previous is not None:
        messages = add_messages(previous, messages)

    llm_response = call_model(messages).result()
    while True:
        if not llm_response.tool_calls:
            break

        # Review tool calls
        tool_results = []
        tool_calls = []
        for i, tool_call in enumerate(llm_response.tool_calls):
            review = review_tool_call(tool_call)
            if isinstance(review, ToolMessage):
                tool_results.append(review)
            else:  # is a validated tool call
                tool_calls.append(review)
                if review != tool_call:
                    llm_response.tool_calls[i] = review  # update message

        # Execute remaining tool calls
        tool_result_futures = [call_tool(tool_call) for tool_call in tool_calls]
        remaining_tool_results = [fut.result() for fut in tool_result_futures]

        # Append to message list
        messages = add_messages(
            messages,
            [llm_response, *tool_results, *remaining_tool_results],
        )

        # Call model again
        llm_response = call_model(messages).result()

    # Generate final response
    messages = add_messages(messages, llm_response)
    return entrypoint.final(value=llm_response, save=messages)
```

:::

:::js

```typescript
import {
  MemorySaver,
  entrypoint,
  interrupt,
  Command,
  addMessages,
} from "@langchain/langgraph";
import { ToolMessage, AIMessage, BaseMessage } from "@langchain/core/messages";

const checkpointer = new MemorySaver();

const agent = entrypoint(
  { checkpointer, name: "agent" },
  async (
    messages: BaseMessage[],
    previous?: BaseMessage[]
  ): Promise<BaseMessage> => {
    if (previous !== undefined) {
      messages = addMessages(previous, messages);
    }

    let llmResponse = await callModel(messages);
    while (true) {
      if (!llmResponse.tool_calls?.length) {
        break;
      }

      // Review tool calls
      const toolResults: ToolMessage[] = [];
      const toolCalls: ToolCall[] = [];

      for (let i = 0; i < llmResponse.tool_calls.length; i++) {
        const review = reviewToolCall(llmResponse.tool_calls[i]);
        if (review instanceof ToolMessage) {
          toolResults.push(review);
        } else {
          // is a validated tool call
          toolCalls.push(review);
          if (review !== llmResponse.tool_calls[i]) {
            llmResponse.tool_calls[i] = review; // update message
          }
        }
      }

      // Execute remaining tool calls
      const remainingToolResults = await Promise.all(
        toolCalls.map((toolCall) => callTool(toolCall))
      );

      // Append to message list
      messages = addMessages(messages, [
        llmResponse,
        ...toolResults,
        ...remainingToolResults,
      ]);

      // Call model again
      llmResponse = await callModel(messages);
    }

    // Generate final response
    messages = addMessages(messages, llmResponse);
    return entrypoint.final({ value: llmResponse, save: messages });
  }
);
```

:::

### Source References

- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`call_model`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6930) (function in langgraph)
- [`execute`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1174) (function in prebuilt)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`list`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L174) (function in checkpoint)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`Interrupt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L157) (class in langgraph)
