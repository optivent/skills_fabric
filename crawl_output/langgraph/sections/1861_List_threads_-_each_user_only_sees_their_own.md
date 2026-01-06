## List threads - each user only sees their own

alice_threads = await alice.threads.search()
bob_threads = await bob.threads.search()
print(f"✅ Alice sees {len(alice_threads)} thread")
print(f"✅ Bob sees {len(bob_threads)} thread")
```

:::

:::js

```typescript
import { getClient } from "@langgraph/sdk";

// Create clients for both users
const alice = getClient({
  url: "http://localhost:2024",
  headers: { Authorization: "Bearer user1-token" },
});

const bob = getClient({
  url: "http://localhost:2024",
  headers: { Authorization: "Bearer user2-token" },
});

// Alice creates an assistant
const aliceAssistant = await alice.assistants.create();
console.log(`✅ Alice created assistant: ${aliceAssistant.assistant_id}`);

// Alice creates a thread and chats
const aliceThread = await alice.threads.create();
console.log(`✅ Alice created thread: ${aliceThread.thread_id}`);

await alice.runs.create(aliceThread.thread_id, "agent", {
  input: {
    messages: [{ role: "user", content: "Hi, this is Alice's private chat" }],
  },
});

// Bob tries to access Alice's thread
try {
  await bob.threads.get(aliceThread.thread_id);
  console.log("❌ Bob shouldn't see Alice's thread!");
} catch (error) {
  console.log("✅ Bob correctly denied access:", error);
}

// Bob creates his own thread
const bobThread = await bob.threads.create();
await bob.runs.create(bobThread.thread_id, "agent", {
  input: {
    messages: [{ role: "user", content: "Hi, this is Bob's private chat" }],
  },
});
console.log(`✅ Bob created his own thread: ${bobThread.thread_id}`);

// List threads - each user only sees their own
const aliceThreads = await alice.threads.search();
const bobThreads = await bob.threads.search();
console.log(`✅ Alice sees ${aliceThreads.length} thread`);
console.log(`✅ Bob sees ${bobThreads.length} thread`);
```

:::

Output:

```bash
✅ Alice created assistant: fc50fb08-78da-45a9-93cc-1d3928a3fc37
✅ Alice created thread: 533179b7-05bc-4d48-b47a-a83cbdb5781d
✅ Bob correctly denied access: Client error '404 Not Found' for url 'http://localhost:2024/threads/533179b7-05bc-4d48-b47a-a83cbdb5781d'
For more information check: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404
✅ Bob created his own thread: 437c36ed-dd45-4a1e-b484-28ba6eca8819
✅ Alice sees 1 thread
✅ Bob sees 1 thread
```

This means:

1. Each user can create and chat in their own threads
2. Users can't see each other's threads
3. Listing threads only shows your own

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`search`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L771) (function in checkpoint)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`list`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L174) (function in checkpoint)
- [`Assistant`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L242) (class in sdk-py)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
