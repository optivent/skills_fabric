## for every request. This will determine whether the request is allowed or not

@auth.authenticate
async def get_current_user(authorization: str | None) -> Auth.types.MinimalUserDict:
    """Check if the user's token is valid."""
    assert authorization
    scheme, token = authorization.split()
    assert scheme.lower() == "bearer"
    # Check if token is valid
    if token not in VALID_TOKENS:
        raise Auth.exceptions.HTTPException(status_code=401, detail="Invalid token")

    # Return user info if valid
    user_data = VALID_TOKENS[token]
    return {
        "identity": user_data["id"],
    }
```

Notice that your [authentication](../../cloud/reference/sdk/python_sdk_ref.md#langgraph_sdk.auth.Auth.authenticate) handler does two important things:

1. Checks if a valid token is provided in the request's [Authorization header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization)
2. Returns the user's [identity](../../cloud/reference/sdk/python_sdk_ref.md#langgraph_sdk.auth.types.MinimalUserDict)
   :::

:::js
The [`Auth`](../../cloud/reference/sdk/js_sdk_ref.md#Auth) object lets you register an authentication function that the LangGraph platform will run on every request. This function receives each request and decides whether to accept or reject.

Create a new file `src/security/auth.ts`. This is where your code will live to check if users are allowed to access your bot:

```typescript title="src/security/auth.ts"
import { Auth } from "@langchain/langgraph-sdk";

// This is our toy user database. Do not do this in production
const VALID_TOKENS: Record<string, { id: string; name: string }> = {
  "user1-token": { id: "user1", name: "Alice" },
  "user2-token": { id: "user2", name: "Bob" },
};

// The "Auth" object is a container that LangGraph will use to mark our authentication function
const auth = new Auth();
  // The `authenticate` method tells LangGraph to call this function as middleware
  // for every request. This will determine whether the request is allowed or not
  .authenticate((request) => {
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
  });

export { auth };
```

Notice that your [authentication](../../cloud/reference/sdk/js_sdk_ref.md#Auth) handler does two important things:

1. Checks if a valid token is provided in the request's [Authorization header](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Authorization)
2. Returns the user's [identity](../../cloud/reference/sdk/js_sdk_ref.md#Auth.types.MinimalUserDict)
   :::

Now tell LangGraph to use authentication by adding the following to the [`langgraph.json`](../../cloud/reference/cli.md#configuration-file) configuration:

:::python

```json hl_lines="7-9" title="langgraph.json"
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/agent/graph.py:graph"
  },
  "env": ".env",
  "auth": {
    "path": "src/security/auth.py:auth"
  }
}
```

:::

:::js

```json hl_lines="7-9" title="langgraph.json"
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/agent/graph.ts:graph"
  },
  "env": ".env",
  "auth": {
    "path": "src/security/auth.ts:auth"
  }
}
```

:::

### Source References

- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`Handler`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L446) (class in prebuilt)
- [`handler`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_client_stream.py#L234) (function in sdk-py)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`MinimalUser`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L151) (class in sdk-py)
