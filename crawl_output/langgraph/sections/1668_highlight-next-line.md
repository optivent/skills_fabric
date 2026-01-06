## highlight-next-line

model_with_tools = model.bind_tools([multiply])
```

:::

:::js
Use `model.bindTools()` to register the tools with the model.

```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ model: "gpt-4o" });

// highlight-next-line
const modelWithTools = model.bindTools([multiply]);
```

:::

LLMs automatically determine if a tool invocation is necessary and handle calling the tool with the appropriate arguments.

??? example "Extended example: attach tools to a chat model"

    :::python
    ```python
    from langchain_core.tools import tool
    from langchain.chat_models import init_chat_model

    @tool
    def multiply(a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b

    model = init_chat_model(model="claude-3-5-haiku-latest")
    # highlight-next-line
    model_with_tools = model.bind_tools([multiply])

    response_message = model_with_tools.invoke("what's 42 x 7?")
    tool_call = response_message.tool_calls[0]

    multiply.invoke(tool_call)
    ```

    ```pycon
    ToolMessage(
        content='294',
        name='multiply',
        tool_call_id='toolu_0176DV4YKSD8FndkeuuLj36c'
    )
    ```
    :::

    :::js
    ```typescript
    import { tool } from "@langchain/core/tools";
    import { ChatOpenAI } from "@langchain/openai";
    import { z } from "zod";

    const multiply = tool(
      (input) => {
        return input.a * input.b;
      },
      {
        name: "multiply",
        description: "Multiply two numbers.",
        schema: z.object({
          a: z.number().describe("First operand"),
          b: z.number().describe("Second operand"),
        }),
      }
    );

    const model = new ChatOpenAI({ model: "gpt-4o" });
    // highlight-next-line
    const modelWithTools = model.bindTools([multiply]);

    const responseMessage = await modelWithTools.invoke("what's 42 x 7?");
    const toolCall = responseMessage.tool_calls[0];

    await multiply.invoke(toolCall);
    ```

    ```
    ToolMessage {
      content: "294",
      name: "multiply",
      tool_call_id: "toolu_0176DV4YKSD8FndkeuuLj36c"
    }
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`multiply`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6341) (function in langgraph)
- [`bind_tools`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/react_agent.py#L19) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`new`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L779) (function in cli)
- [`Cat`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel_async.py#L4123) (class in langgraph)
- [`a`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4642) (function in langgraph)
