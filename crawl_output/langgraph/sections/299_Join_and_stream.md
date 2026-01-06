## Join and stream

LangGraph Platform allows you to join an active [background run](../how-tos/background_run.md) and stream outputs from it. To do so, you can use [LangGraph SDK's](https://langchain-ai.github.io/langgraph/cloud/reference/sdk/python_sdk_ref/) `client.runs.join_stream` method:

=== "Python"

    ```python
    from langgraph_sdk import get_client
    client = get_client(url=<DEPLOYMENT_URL>, api_key=<API_KEY>)

    # highlight-next-line
    async for chunk in client.runs.join_stream(
        thread_id,
        # highlight-next-line
        run_id,  # (1)!
    ):
        print(chunk)
    ```

    1. This is the `run_id` of an existing run you want to join.


=== "JavaScript"

    ```js
    import { Client } from "@langchain/langgraph-sdk";
    const client = new Client({ apiUrl: <DEPLOYMENT_URL>, apiKey: <API_KEY> });

    // highlight-next-line
    const streamResponse = client.runs.joinStream(
      threadID,
      // highlight-next-line
      runId  // (1)!
    );
    for await (const chunk of streamResponse) {
      console.log(chunk);
    }
    ```

    1. This is the `run_id` of an existing run you want to join.

=== "cURL"

    ```bash
    curl --request GET \
    --url <DEPLOYMENT_URL>/threads/<THREAD_ID>/runs/<RUN_ID>/stream \
    --header 'Content-Type: application/json' \
    --header 'x-api-key: <API_KEY>'
    ```

!!! warning "Outputs not buffered"

    When you use `.join_stream`, output is not buffered, so any output produced before joining will not be received.

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`_run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/batch.py#L326) (function in checkpoint)
- [`get_client`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L177) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`join_stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L6151) (function in sdk-py)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`join`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L6114) (function in sdk-py)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
