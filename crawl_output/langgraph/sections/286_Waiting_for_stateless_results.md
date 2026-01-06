## Waiting for stateless results

In addition to streaming, you can also wait for a stateless result by using the `.wait` function like follows:

=== "Python"

    ```python
    stateless_run_result = await client.runs.wait(
        None,
        assistant_id,
        input=input,
    )
    print(stateless_run_result)
    ```

=== "Javascript"

    ```js
    let statelessRunResult = await client.runs.wait(
      null,
      assistantId,
      { input: input }
    );
    console.log(statelessRunResult);
    ```

=== "CURL"

    ```bash
    curl --request POST \
        --url <DEPLOYMENT_URL>/runs/wait \
        --header 'Content-Type: application/json' \
        --data '{
            "assistant_id": <ASSISTANT_IDD>,
        }'
    ```

Output:

    {
        'messages': [
            {
                'content': 'Hello! My name is Bagatur and I am 26 years old.',
                'additional_kwargs': {},
                'response_metadata': {},
                'type': 'human',
                'name': None,
                'id': '5e088543-62c2-43de-9d95-6086ad7f8b48',
                'example': False}
            ,
            {
                'content': "Hello Bagatur! It's nice to meet you. Thank you for introducing yourself and sharing your age. Is there anything specific you'd like to know or discuss? I'm here to help with any questions or topics you'd like to explore.",
                'additional_kwargs': {},
                'response_metadata': {},
                'type': 'ai',
                'name': None,
                'id': 'run-d6361e8d-4d4c-45bd-ba47-39520257f773',
                'example': False,
                'tool_calls': [],
                'invalid_tool_calls': [],
                'usage_metadata': None
            }
        ]
    }

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`_run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/batch.py#L326) (function in checkpoint)
- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
