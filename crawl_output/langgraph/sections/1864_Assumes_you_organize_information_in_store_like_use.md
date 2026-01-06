## Assumes you organize information in store like (user_id, resource_type, resource_id)

@auth.on.store()
async def authorize_store(ctx: Auth.types.AuthContext, value: dict):
    # The "namespace" field for each store item is a tuple you can think of as the directory of an item.
    namespace: tuple = value["namespace"]
    assert namespace[0] == ctx.user.identity, "Not authorized"
```

:::

:::js
The broad `auth.on("*")` handler matches on all [authorization events](../../concepts/auth.md#supported-resources). This is concise, but it means the contents of the `value` object are not well-scoped, and the same user-level access control is applied to every resource. If you want to be more fine-grained, you can also control specific actions on resources.

Update `src/security/auth.ts` to add handlers for specific resource types:

```typescript
// Keep our previous handlers...

import { Auth, HTTPException } from "@langchain/langgraph-sdk";

auth.on("threads:create", async ({ user, value }) => {
  // Add owner when creating threads.
  // This handler runs when creating new threads and does two things:
  // 1. Sets metadata on the thread being created to track ownership
  // 2. Returns a filter that ensures only the creator can access it

  // Example value:
  //  {thread_id: UUID('99b045bc-b90b-41a8-b882-dabc541cf740'), metadata: {}, if_exists: 'raise'}

  // Add owner metadata to the thread being created
  // This metadata is stored with the thread and persists
  const metadata = value.metadata || {};
  metadata.owner = user.identity;
  value.metadata = metadata;

  // Return filter to restrict access to just the creator
  return { owner: user.identity };
});

auth.on("threads:read", async ({ user, value }) => {
  // Only let users read their own threads.
  // This handler runs on read operations. We don't need to set
  // metadata since the thread already exists - we just need to
  // return a filter to ensure users can only see their own threads.
  return { owner: user.identity };
});

auth.on("assistants", async ({ user, value }) => {
  // For illustration purposes, we will deny all requests
  // that touch the assistants resource
  // Example value:
  // {
  //     'assistant_id': UUID('63ba56c3-b074-4212-96e2-cc333bbc4eb4'),
  //     'graph_id': 'agent',
  //     'config': {},
  //     'metadata': {},
  //     'name': 'Untitled'
  // }
  throw new HTTPException(403, "User lacks the required permissions.");
});

auth.on("store", async ({ user, value }) => {
  // The "namespace" field for each store item is a tuple you can think of as the directory of an item.
  const namespace: string[] = value.namespace;
  if (namespace[0] !== user.identity) {
    throw new Error("Not authorized");
  }
});
```

:::

Notice that instead of one global handler, you now have specific handlers for:

1. Creating threads
2. Reading threads
3. Accessing assistants

:::python
The first three of these match specific **actions** on each resource (see [resource actions](../../concepts/auth.md#resource-specific-handlers)), while the last one (`@auth.on.assistants`) matches _any_ action on the `assistants` resource. For each request, LangGraph will run the most specific handler that matches the resource and action being accessed. This means that the four handlers above will run rather than the broadly scoped "`@auth.on`" handler.
:::

:::js
The first three of these match specific **actions** on each resource (see [resource actions](../../concepts/auth.md#resource-specific-handlers)), while the last one (`auth.on.assistants`) matches _any_ action on the `assistants` resource. For each request, LangGraph will run the most specific handler that matches the resource and action being accessed. This means that the four handlers above will run rather than the broadly scoped "`auth.on`" handler.
:::

Try adding the following test code to your test file:

:::python

```python

### Source References

- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`Handler`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L446) (class in prebuilt)
- [`handler`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_client_stream.py#L234) (function in sdk-py)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`Assistant`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L242) (class in sdk-py)
