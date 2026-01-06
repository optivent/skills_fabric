## Filter by thread status

Use the `status` field to filter threads based on their status. Supported values are `idle`, `busy`, `interrupted`, and `error`. See [here](https://langchain-ai.github.io/langgraph/cloud/reference/sdk/python_sdk_ref/?h=thread+status#langgraph_sdk.auth.types.ThreadStatus) for information on each status. For example, to view `idle` threads:

=== "Python"

    ```python
    print(await client.threads.search(status="idle",limit=1))
    ```

=== "Javascript"

    ```js
    console.log(await client.threads.search({ status: "idle", limit: 1 }));
    ```

=== "CURL"

    ```bash
    curl --request POST \
    --url <DEPLOYMENT_URL>/threads/search \
    --header 'Content-Type: application/json' \
    --data '{"status": "idle", "limit": 1}'
    ```

Output:

    [
      {
        'thread_id': 'cacf79bb-4248-4d01-aabc-938dbd60ed2c',
        'created_at': '2024-08-14T17:36:38.921660+00:00',
        'updated_at': '2024-08-14T17:36:38.921660+00:00',
        'metadata': {'graph_id': 'agent'},
        'status': 'idle',
        'config': {'configurable': {}}
      }
    ]

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`search`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L771) (function in checkpoint)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Interrupt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L157) (class in langgraph)
