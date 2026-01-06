## Use in an agent

:::python
When using `create_react_agent` you can specify the model by its name string, which is a shorthand for initializing the model using `init_chat_model`. This allows you to use the model without needing to import or instantiate it directly.

=== "model name"

      ```python
      from langgraph.prebuilt import create_react_agent

      create_react_agent(
         # highlight-next-line
         model="anthropic:claude-3-7-sonnet-latest",
         # other parameters
      )
      ```

=== "model instance"

      ```python
      from langchain_anthropic import ChatAnthropic
      from langgraph.prebuilt import create_react_agent

      model = ChatAnthropic(
          model="claude-3-7-sonnet-latest",
          temperature=0,
          max_tokens=2048
      )
      # Alternatively
      # model = init_chat_model("anthropic:claude-3-7-sonnet-latest")

      agent = create_react_agent(
        # highlight-next-line
        model=model,
        # other parameters
      )
      ```

:::

:::js
When using `createReactAgent` you can pass the model instance directly:

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { createReactAgent } from "@langchain/langgraph/prebuilt";

const model = new ChatOpenAI({
  model: "gpt-4o",
  temperature: 0,
});

const agent = createReactAgent({
  llm: model,
  tools: tools,
});
```

:::

:::python

### Source References

- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`new`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L779) (function in cli)
- [`a`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4642) (function in langgraph)
- [`A`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L124) (class in langgraph)
- [`B`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L128) (class in langgraph)
- [`b`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4645) (function in langgraph)
