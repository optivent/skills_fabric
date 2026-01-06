## Prepopulated State

Finally, you can create a thread with an arbitrary pre-defined state by providing a list of `supersteps` into the `create` method. The `supersteps` describe a list of a sequence of state updates. For example:

=== "Python"

    ```python
    from langgraph_sdk import get_client

    client = get_client(url=<DEPLOYMENT_URL>)
    thread = await client.threads.create(
      graph_id="agent",
      supersteps=[
        {
          updates: [
            {
              values: {},
              as_node: '__input__',
            },
          ],
        },
        {
          updates: [
            {
              values: {
                messages: [
                  {
                    type: 'human',
                    content: 'hello',
                  },
                ],
              },
              as_node: '__start__',
            },
          ],
        },
        {
          updates: [
            {
              values: {
                messages: [
                  {
                    content: 'Hello! How can I assist you today?',
                    type: 'ai',
                  },
                ],
              },
              as_node: 'call_model',
            },
          ],
        },
      ])

    print(thread)
    ```

=== "Javascript"

    ```js
    import { Client } from "@langchain/langgraph-sdk";

    const client = new Client({ apiUrl: <DEPLOYMENT_URL> });
    const thread = await client.threads.create({
        graphId: 'agent',
        supersteps: [
        {
          updates: [
            {
              values: {},
              asNode: '__input__',
            },
          ],
        },
        {
          updates: [
            {
              values: {
                messages: [
                  {
                    type: 'human',
                    content: 'hello',
                  },
                ],
              },
              asNode: '__start__',
            },
          ],
        },
        {
          updates: [
            {
              values: {
                messages: [
                  {
                    content: 'Hello! How can I assist you today?',
                    type: 'ai',
                  },
                ],
              },
              asNode: 'call_model',
            },
          ],
        },
      ],
    });

    console.log(thread);
    ```

=== "CURL"

    ```bash
    curl --request POST \
        --url <DEPLOYMENT_URL>/threads \
        --header 'Content-Type: application/json' \
        --data '{"metadata":{"graph_id":"agent"},"supersteps":[{"updates":[{"values":{},"as_node":"__input__"}]},{"updates":[{"values":{"messages":[{"type":"human","content":"hello"}]},"as_node":"__start__"}]},{"updates":[{"values":{"messages":[{"content":"Hello\u0021 How can I assist you today?","type":"ai"}]},"as_node":"call_model"}]}]}'
    ```

Output:

    {
        "thread_id": "f15d70a1-27d4-4793-a897-de5609920b7d",
        "created_at": "2025-05-12T15:37:08.935038+00:00",
        "updated_at": "2025-05-12T15:37:08.935046+00:00",
        "metadata": {"graph_id": "agent"},
        "status": "idle",
        "config": {},
        "values": {
            "messages": [
                {
                    "content": "hello",
                    "additional_kwargs": {},
                    "response_metadata": {},
                    "type": "human",
                    "name": null,
                    "id": "8701f3be-959c-4b7c-852f-c2160699b4ab",
                    "example": false
                },
                {
                    "content": "Hello! How can I assist you today?",
                    "additional_kwargs": {},
                    "response_metadata": {},
                    "type": "ai",
                    "name": null,
                    "id": "4d8ea561-7ca1-409a-99f7-6b67af3e1aa3",
                    "example": false,
                    "tool_calls": [],
                    "invalid_tool_calls": [],
                    "usage_metadata": null
                }
            ]
        }
    }

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`call_model`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6930) (function in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`get_client`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L177) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
