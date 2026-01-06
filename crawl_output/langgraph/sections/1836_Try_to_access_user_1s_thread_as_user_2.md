## Try to access user 1's thread as user 2

user2_token = await login(email2, password)
user2_client = get_client(
    url="http://localhost:2024", headers={"Authorization": f"Bearer {user2_token}"}
)

try:
    await user2_client.threads.get(thread["thread_id"])
    print("❌ User 2 shouldn't see User 1's thread!")
except Exception as e:
    print("✅ User 2 blocked from User 1's thread:", e)
```

:::

:::js

```typescript
async function login(email: string, password: string): Promise<string> {
  /**Get an access token for an existing user.*/
  const response = await fetch(
    `${SUPABASE_URL}/auth/v1/token?grant_type=password`,
    {
      method: "POST",
      headers: {
        apikey: SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    }
  );

  if (response.status !== 200) {
    throw new Error(`Failed to login: ${response.statusText}`);
  }

  const data = await response.json();
  return data.access_token;
}

// Log in as user 1
const user1Token = await login(email1, password);
const user1Client = new Client({
  apiUrl: "http://localhost:2024",
  headers: { Authorization: `Bearer ${user1Token}` },
});

// Create a thread as user 1
const thread = await user1Client.threads.create();
console.log(`✅ User 1 created thread: ${thread.thread_id}`);

// Try to access without a token
const unauthenticatedClient = new Client({ apiUrl: "http://localhost:2024" });
try {
  await unauthenticatedClient.threads.create();
  console.log("❌ Unauthenticated access should fail!");
} catch (e) {
  console.log("✅ Unauthenticated access blocked:", e.message);
}

// Try to access user 1's thread as user 2
const user2Token = await login(email2, password);
const user2Client = new Client({
  apiUrl: "http://localhost:2024",
  headers: { Authorization: `Bearer ${user2Token}` },
});

try {
  await user2Client.threads.get(thread.thread_id);
  console.log("❌ User 2 shouldn't see User 1's thread!");
} catch (e) {
  console.log("✅ User 2 blocked from User 1's thread:", e.message);
}
```

:::

The output should look like this:

```shell
✅ User 1 created thread: d6af3754-95df-4176-aa10-dbd8dca40f1a
✅ Unauthenticated access blocked: Client error '403 Forbidden' for url 'http://localhost:2024/threads'
✅ User 2 blocked from User 1's thread: Client error '404 Not Found' for url 'http://localhost:2024/threads/d6af3754-95df-4176-aa10-dbd8dca40f1a'
```

Your authentication and authorization are working together:

1. Users must log in to access the bot
2. Each user can only see their own threads

All users are managed by the Supabase auth provider, so you don't need to implement any additional user management logic.

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`get_client`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L177) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
