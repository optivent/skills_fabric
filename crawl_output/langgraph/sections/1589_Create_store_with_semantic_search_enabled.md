## Create store with semantic search enabled

embeddings = init_embeddings("openai:text-embedding-3-small")
store = InMemoryStore(
    index={
        "embed": embeddings,
        "dims": 1536,
    }
)

store.put(("user_123", "memories"), "1", {"text": "I love pizza"})
store.put(("user_123", "memories"), "2", {"text": "I am a plumber"})

items = store.search(
    ("user_123", "memories"), query="I'm hungry", limit=1
)
```

:::

:::js

```typescript
import { OpenAIEmbeddings } from "@langchain/openai";
import { InMemoryStore } from "@langchain/langgraph";

// Create store with semantic search enabled
const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });
const store = new InMemoryStore({
  index: {
    embeddings,
    dims: 1536,
  },
});

await store.put(["user_123", "memories"], "1", { text: "I love pizza" });
await store.put(["user_123", "memories"], "2", { text: "I am a plumber" });

const items = await store.search(["user_123", "memories"], {
  query: "I'm hungry",
  limit: 1,
});
```

:::

??? example "Long-term memory with semantic search"

    :::python
    ```python
    from typing import Optional

    from langchain.embeddings import init_embeddings
    from langchain.chat_models import init_chat_model
    from langgraph.store.base import BaseStore
    from langgraph.store.memory import InMemoryStore
    from langgraph.graph import START, MessagesState, StateGraph

    llm = init_chat_model("openai:gpt-4o-mini")

    # Create store with semantic search enabled
    embeddings = init_embeddings("openai:text-embedding-3-small")
    store = InMemoryStore(
        index={
            "embed": embeddings,
            "dims": 1536,
        }
    )

    store.put(("user_123", "memories"), "1", {"text": "I love pizza"})
    store.put(("user_123", "memories"), "2", {"text": "I am a plumber"})

    def chat(state, *, store: BaseStore):
        # Search based on user's last message
        items = store.search(
            ("user_123", "memories"), query=state["messages"][-1].content, limit=2
        )
        memories = "\n".join(item.value["text"] for item in items)
        memories = f"## Memories of user\n{memories}" if memories else ""
        response = llm.invoke(
            [
                {"role": "system", "content": f"You are a helpful assistant.\n{memories}"},
                *state["messages"],
            ]
        )
        return {"messages": [response]}


    builder = StateGraph(MessagesState)
    builder.add_node(chat)
    builder.add_edge(START, "chat")
    graph = builder.compile(store=store)

    for message, metadata in graph.stream(
        input={"messages": [{"role": "user", "content": "I'm hungry"}]},
        stream_mode="messages",
    ):
        print(message.content, end="")
    ```
    :::

    :::js
    ```typescript
    import { OpenAIEmbeddings, ChatOpenAI } from "@langchain/openai";
    import { StateGraph, START, MessagesZodState, InMemoryStore } from "@langchain/langgraph";
    import { z } from "zod";

    const llm = new ChatOpenAI({ model: "gpt-4o-mini" });

    // Create store with semantic search enabled
    const embeddings = new OpenAIEmbeddings({ model: "text-embedding-3-small" });
    const store = new InMemoryStore({
      index: {
        embeddings,
        dims: 1536,
      }
    });

    await store.put(["user_123", "memories"], "1", { text: "I love pizza" });
    await store.put(["user_123", "memories"], "2", { text: "I am a plumber" });

    const chat = async (state: z.infer<typeof MessagesZodState>, config) => {
      // Search based on user's last message
      const items = await config.store.search(
        ["user_123", "memories"],
        { query: state.messages.at(-1)?.content, limit: 2 }
      );
      const memories = items.map(item => item.value.text).join("\n");
      const memoriesText = memories ? `## Memories of user\n${memories}` : "";

      const response = await llm.invoke([
        { role: "system", content: `You are a helpful assistant.\n${memoriesText}` },
        ...state.messages,
      ]);

      return { messages: [response] };
    };

    const builder = new StateGraph(MessagesZodState)
      .addNode("chat", chat)
      .addEdge(START, "chat");
    const graph = builder.compile({ store });

    for await (const [message, metadata] of await graph.stream(
      { messages: [{ role: "user", content: "I'm hungry" }] },
      { streamMode: "messages" }
    )) {
      if (message.content) {
        console.log(message.content);
      }
    }
    ```
    :::

See [this guide](../../cloud/deployment/semantic_search.md) for more information on how to use semantic search with LangGraph memory store.

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`search`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L771) (function in checkpoint)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`join`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L6114) (function in sdk-py)
