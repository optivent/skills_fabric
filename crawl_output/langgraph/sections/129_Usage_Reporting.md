## Usage Reporting

**Endpoint:**

`POST beacon.langchain.com/v1/metadata/submit`

**Request:**

```json
{
  "license": "<YOUR_LICENSE_KEY>",
  "from_timestamp": "2025-01-06T09:00:00Z",
  "to_timestamp": "2025-01-06T10:00:00Z",
  "tags": {
    "langgraph.python.version": "0.1.0",
    "langgraph_api.version": "0.2.0",
    "langgraph.platform.revision": "abc123",
    "langgraph.platform.variant": "standard",
    "langgraph.platform.host": "host-1",
    "langgraph.platform.tenant_id": "3a1c2b6f-4430-4b92-8a5b-79b8b567bbc1",
    "langgraph.platform.project_id": "c5b5f53a-4716-4326-8967-d4f7f7799735",
    "langgraph.platform.plan": "enterprise",
    "user_app.uses_indexing": "true",
    "user_app.uses_custom_app": "false",
    "user_app.uses_custom_auth": "true",
    "user_app.uses_thread_ttl": "true",
    "user_app.uses_store_ttl": "false"
  },
  "measures": {
    "langgraph.platform.runs": 150,
    "langgraph.platform.nodes": 450
  },
  "logs": []
}
```

**Response:**

```json
"204 No Content"
```

### Source References

- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`store`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/test_store.py#L34) (function in checkpoint-postgres)
- [`read`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1044) (class in sdk-py)
- [`Auth`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/__init__.py#L13) (class in sdk-py)
- [`json`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L173) (function in sdk-py)
- [`time`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/id.py#L61) (function in checkpoint)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
