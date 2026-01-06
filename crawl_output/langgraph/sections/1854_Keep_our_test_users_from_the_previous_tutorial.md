## Keep our test users from the previous tutorial

VALID_TOKENS = {
    "user1-token": {"id": "user1", "name": "Alice"},
    "user2-token": {"id": "user2", "name": "Bob"},
}

auth = Auth()


@auth.authenticate
async def get_current_user(authorization: str | None) -> Auth.types.MinimalUserDict:
    """Our authentication handler from the previous tutorial."""
    assert authorization
    scheme, token = authorization.split()
    assert scheme.lower() == "bearer"

    if token not in VALID_TOKENS:
        raise Auth.exceptions.HTTPException(status_code=401, detail="Invalid token")

    user_data = VALID_TOKENS[token]
    return {
        "identity": user_data["id"],
    }


@auth.on
async def add_owner(
    ctx: Auth.types.AuthContext,  # Contains info about the current user
    value: dict,  # The resource being created/accessed
):
    """Make resources private to their creator."""
    # Examples:
    # ctx: AuthContext(
    #     permissions=[],
    #     user=ProxyUser(
    #         identity='user1',
    #         is_authenticated=True,
    #         display_name='user1'
    #     ),
    #     resource='threads',
    #     action='create_run'
    # )
    # value:
    # {
    #     'thread_id': UUID('1e1b2733-303f-4dcd-9620-02d370287d72'),
    #     'assistant_id': UUID('fe096781-5601-53d2-b2f6-0d3403f7e9ca'),
    #     'run_id': UUID('1efbe268-1627-66d4-aa8d-b956b0f02a41'),
    #     'status': 'pending',
    #     'metadata': {},
    #     'prevent_insert_if_inflight': True,
    #     'multitask_strategy': 'reject',
    #     'if_not_exists': 'reject',
    #     'after_seconds': 0,
    #     'kwargs': {
    #         'input': {'messages': [{'role': 'user', 'content': 'Hello!'}]},
    #         'command': None,
    #         'config': {
    #             'configurable': {
    #                 'langgraph_auth_user': ... Your user object...
    #                 'langgraph_auth_user_id': 'user1'
    #             }
    #         },
    #         'stream_mode': ['values'],
    #         'interrupt_before': None,
    #         'interrupt_after': None,
    #         'webhook': None,
    #         'feedback_keys': None,
    #         'temporary': False,
    #         'subgraphs': False
    #     }
    # }

    # Does 2 things:
    # 1. Add the user's ID to the resource's metadata. Each LangGraph resource has a `metadata` dict that persists with the resource.
    # this metadata is useful for filtering in read and update operations
    # 2. Return a filter that lets users only see their own resources
    filters = {"owner": ctx.user.identity}
    metadata = value.setdefault("metadata", {})
    metadata.update(filters)

    # Only let users see their own resources
    return filters
```

:::

:::js
Update your `src/security/auth.ts` and add one authorization handler to run on every request:

```typescript hl_lines="29-39" title="src/security/auth.ts"
import { Auth, HTTPException } from "@langchain/langgraph-sdk";

// Keep our test users from the previous tutorial
const VALID_TOKENS: Record<string, { id: string; name: string }> = {
  "user1-token": { id: "user1", name: "Alice" },
  "user2-token": { id: "user2", name: "Bob" },
};

const auth = new Auth()
  .authenticate(async (request) => {
    // Our authentication handler from the previous tutorial.
    const apiKey = request.headers.get("x-api-key");
    if (!apiKey || !isValidKey(apiKey)) {
      throw new HTTPException(401, "Invalid API key");
    }

    const [scheme, token] = apiKey.split(" ");
    if (scheme.toLowerCase() !== "bearer") {
      throw new Error("Bearer token required");
    }

    if (!VALID_TOKENS[token]) {
      throw new HTTPException(401, "Invalid token");
    }

    const userData = VALID_TOKENS[token];
    return {
      identity: userData.id,
    };
  })
  .on("*", ({ value, user }) => {
    // This handler makes resources private to their creator by doing 2 things:
    // 1. Add the user's ID to the resource's metadata. Each LangGraph resource has a `metadata` object that persists with the resource.
    // this metadata is useful for filtering in read and update operations
    // 2. Return a filter that lets users only see their own resources
    // Examples:
    // {
    //   user: ProxyUser {
    //     identity: 'user1',
    //     is_authenticated: true,
    //     display_name: 'user1'
    //   },
    //   value: {
    //     'thread_id': UUID('1e1b2733-303f-4dcd-9620-02d370287d72'),
    //     'assistant_id': UUID('fe096781-5601-53d2-b2f6-0d3403f7e9ca'),
    //     'run_id': UUID('1efbe268-1627-66d4-aa8d-b956b0f02a41'),
    //     'status': 'pending',
    //     'metadata': {},
    //     'prevent_insert_if_inflight': true,
    //     'multitask_strategy': 'reject',
    //     'if_not_exists': 'reject',
    //     'after_seconds': 0,
    //     'kwargs': {
    //         'input': {'messages': [{'role': 'user', 'content': 'Hello!'}]},
    //         'command': null,
    //         'config': {
    //             'configurable': {
    //                 'langgraph_auth_user': ... Your user object...
    //                 'langgraph_auth_user_id': 'user1'
    //             }
    //         },
    //         'stream_mode': ['values'],
    //         'interrupt_before': null,
    //         'interrupt_after': null,
    //         'webhook': null,
    //         'feedback_keys': null,
    //         'temporary': false,
    //         'subgraphs': false
    //     }
    //   }
    // }

    const filters = { owner: user.identity };
    const metadata = value.metadata || {};
    Object.assign(metadata, filters);
    value.metadata = metadata;

    // Only let users see their own resources
    return filters;
  });

export { auth };
```

:::

:::python
The handler receives two parameters:

1. `ctx` ([AuthContext](../../cloud/reference/sdk/python_sdk_ref.md#langgraph_sdk.auth.types.AuthContext)): contains info about the current `user`, the user's `permissions`, the `resource` ("threads", "crons", "assistants"), and the `action` being taken ("create", "read", "update", "delete", "search", "create_run")
2. `value` (`dict`): data that is being created or accessed. The contents of this dict depend on the resource and action being accessed. See [adding scoped authorization handlers](#scoped-authorization) below for information on how to get more tightly scoped access control.
   :::

:::js
The handler receives an object with the following properties:

1. `user` contains info about the current `user`, the user's `permissions`, the `resource` ("threads", "crons", "assistants")
2. `action` contains information about the action being taken ("create", "read", "update", "delete", "search", "create_run")
3. `value` (`Record<string, any>`): data that is being created or accessed. The contents of this object depend on the resource and action being accessed. See [adding scoped authorization handlers](#scoped-authorization) below for information on how to get more tightly scoped access control.
   :::

Notice that the simple handler does two things:

1. Adds the user's ID to the resource's metadata.
2. Returns a metadata filter so users only see resources they own.

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`Handler`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L446) (class in prebuilt)
- [`handler`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_client_stream.py#L234) (function in sdk-py)
- [`_run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/batch.py#L326) (function in checkpoint)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
