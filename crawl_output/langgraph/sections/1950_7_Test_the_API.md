## 7. Test the API

:::python
=== "Python SDK (async)"

    1. Install the LangGraph Python SDK:

        ```shell
        pip install langgraph-sdk
        ```

    1. Send a message to the assistant (threadless run):

        ```python
        from langgraph_sdk import get_client
        import asyncio

        client = get_client(url="http://localhost:2024")

        async def main():
            async for chunk in client.runs.stream(
                None,  # Threadless run
                "agent", # Name of assistant. Defined in langgraph.json.
                input={
                "messages": [{
                    "role": "human",
                    "content": "What is LangGraph?",
                    }],
                },
            ):
                print(f"Receiving new event of type: {chunk.event}...")
                print(chunk.data)
                print("\n\n")

        asyncio.run(main())
        ```

=== "Python SDK (sync)"

    1. Install the LangGraph Python SDK:

        ```shell
        pip install langgraph-sdk
        ```

    1. Send a message to the assistant (threadless run):

        ```python
        from langgraph_sdk import get_sync_client

        client = get_sync_client(url="http://localhost:2024")

        for chunk in client.runs.stream(
            None,  # Threadless run
            "agent", # Name of assistant. Defined in langgraph.json.
            input={
                "messages": [{
                    "role": "human",
                    "content": "What is LangGraph?",
                }],
            },
            stream_mode="messages-tuple",
        ):
            print(f"Receiving new event of type: {chunk.event}...")
            print(chunk.data)
            print("\n\n")
        ```

=== "Rest API"

    ```bash
    curl -s --request POST \
        --url "http://localhost:2024/runs/stream" \
        --header 'Content-Type: application/json' \
        --data "{
            \"assistant_id\": \"agent\",
            \"input\": {
                \"messages\": [
                    {
                        \"role\": \"human\",
                        \"content\": \"What is LangGraph?\"
                    }
                ]
            },
            \"stream_mode\": \"messages-tuple\"
        }"
    ```

:::

:::js
=== "Javascript SDK"

    1. Install the LangGraph JS SDK:

        ```shell
        npm install @langchain/langgraph-sdk
        ```

    1. Send a message to the assistant (threadless run):

        ```js
        const { Client } = await import("@langchain/langgraph-sdk");

        // only set the apiUrl if you changed the default port when calling langgraph dev
        const client = new Client({ apiUrl: "http://localhost:2024"});

        const streamResponse = client.runs.stream(
            null, // Threadless run
            "agent", // Assistant ID
            {
                input: {
                    "messages": [
                        { "role": "user", "content": "What is LangGraph?"}
                    ]
                },
                streamMode: "messages-tuple",
            }
        );

        for await (const chunk of streamResponse) {
            console.log(`Receiving new event of type: ${chunk.event}...`);
            console.log(JSON.stringify(chunk.data));
            console.log("\n\n");
        }
        ```

=== "Rest API"

    ```bash
    curl -s --request POST \
        --url "http://localhost:2024/runs/stream" \
        --header 'Content-Type: application/json' \
        --data "{
            \"assistant_id\": \"agent\",
            \"input\": {
                \"messages\": [
                    {
                        \"role\": \"human\",
                        \"content\": \"What is LangGraph?\"
                    }
                ]
            },
            \"stream_mode\": \"messages-tuple\"
        }"
    ```

:::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`get_client`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L177) (function in sdk-py)
- [`get_sync_client`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3568) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Assistant`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L242) (class in sdk-py)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
