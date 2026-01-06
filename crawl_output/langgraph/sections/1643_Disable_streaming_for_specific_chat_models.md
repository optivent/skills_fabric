## Disable streaming for specific chat models

If your application mixes models that support streaming with those that do not, you may need to explicitly disable streaming for
models that do not support it.

:::python
Set `disable_streaming=True` when initializing the model.

=== "init_chat_model"

      ```python
      from langchain.chat_models import init_chat_model

      model = init_chat_model(
          "anthropic:claude-3-7-sonnet-latest",
          # highlight-next-line
          disable_streaming=True # (1)!
      )
      ```

      1. Set `disable_streaming=True` to disable streaming for the chat model.

=== "chat model interface"

      ```python
      from langchain_openai import ChatOpenAI

      llm = ChatOpenAI(model="o1-preview", disable_streaming=True) # (1)!
      ```

      1. Set `disable_streaming=True` to disable streaming for the chat model.

:::

:::js
Set `streaming: false` when initializing the model.

```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({
  model: "o1-preview",
  streaming: false, // (1)!
});
```

:::

:::python

### Source References

- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`set`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L84) (function in checkpoint)
- [`up`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L3118) (function in langgraph)
- [`new`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L779) (function in cli)
- [`_stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/fake_chat.py#L44) (function in langgraph)
- [`Cat`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel_async.py#L4123) (class in langgraph)
- [`a`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4642) (function in langgraph)
- [`A`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L124) (class in langgraph)
- [`B`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L128) (class in langgraph)
