## Setup

=== "Python"

    ```python
    from langgraph_sdk import get_client

    client = get_client(url=<DEPLOYMENT_URL>)

    openai_assistant = await client.assistants.create(
        graph_id="agent", config={"configurable": {"model_name": "openai"}}
    )

    # There should always be a default assistant with no configuration
    assistants = await client.assistants.search()
    default_assistant = [a for a in assistants if not a["config"]][0]
    ```

=== "Javascript"

    ```js
    import { Client } from "@langchain/langgraph-sdk";

    const client = new Client({ apiUrl: <DEPLOYMENT_URL> });
    
    const openAIAssistant = await client.assistants.create(
      { graphId: "agent", config: {"configurable": {"model_name": "openai"}}}
    );

    const assistants = await client.assistants.search();
    const defaultAssistant = assistants.find(a => !a.config);
    ```

=== "CURL"

    ```bash
    curl --request POST \
        --url <DEPLOYMENT_URL>/assistants \
        --header 'Content-Type: application/json' \
        --data '{
            "graph_id": "agent",
            "config": { "configurable": { "model_name": "openai" } }
        }' && \
    curl --request POST \
        --url <DEPLOYMENT_URL>/assistants/search \
        --header 'Content-Type: application/json' \
        --data '{
            "limit": 10,
            "offset": 0
        }' | jq -c 'map(select(.config == null or .config == {})) | .[0]'
    ```

We can see that these agents are different:

=== "Python"

    ```python
    print(openai_assistant)
    ```

=== "Javascript"

    ```js
    console.log(openAIAssistant);
    ```

=== "CURL"

    ```bash
    curl --request GET \
        --url <DEPLOYMENT_URL>/assistants/<OPENAI_ASSISTANT_ID>
    ```

Output:

    {
        "assistant_id": "db87f39d-b2b1-4da8-ac65-cf81beb3c766",
        "graph_id": "agent",
        "created_at": "2024-08-30T21:18:51.850581+00:00",
        "updated_at": "2024-08-30T21:18:51.850581+00:00",
        "config": {
            "configurable": {
                "model_name": "openai"
            }
        },
        "metadata": {}
    }

=== "Python"

    ```python
    print(default_assistant)
    ```

=== "Javascript"

    ```js
    console.log(defaultAssistant);
    ```

=== "CURL"

    ```bash
    curl --request GET \
        --url <DEPLOYMENT_URL>/assistants/<DEFAULT_ASSISTANT_ID>
    ```

Output:

    {
        "assistant_id": "fe096781-5601-53d2-b2f6-0d3403f7e9ca",
        "graph_id": "agent",
        "created_at": "2024-08-08T22:45:24.562906+00:00",
        "updated_at": "2024-08-08T22:45:24.562906+00:00",
        "config": {},
        "metadata": {
            "created_by": "system"
        }
    }

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get_client`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L177) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`search`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L771) (function in checkpoint)
