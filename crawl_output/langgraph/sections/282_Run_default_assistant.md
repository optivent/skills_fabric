## Run default assistant

Now, we can run it on the default assistant and see that this second assistant is aware of the initial question, and can answer the question, "and you?":

=== "Python"

    ```python
    input = {"messages": [{"role": "user", "content": "and you?"}]}
    async for event in client.runs.stream(
        thread["thread_id"],
        default_assistant["assistant_id"],
        input=input,
        stream_mode="updates",
    ):
        print(f"Receiving event of type: {event.event}")
        print(event.data)
        print("\n\n")
    ```

=== "Javascript"

    ```js
    let input =  {"messages": [{"role": "user", "content": "and you?"}]}

    const streamResponse = client.runs.stream(
      thread["thread_id"],
      defaultAssistant["assistant_id"],
      {
        input,
        streamMode: "updates"
      }
    );
    for await (const event of streamResponse) {
      console.log(`Receiving event of type: ${event.event}`);
      console.log(event.data);
      console.log("\n\n");
    }
    ```

=== "CURL"

    ```bash
    curl --request POST \
        --url <DEPLOYMENT_URL>/threads/<THREAD_ID>/runs/stream \
        --header 'Content-Type: application/json' \
        --data '{
            "assistant_id": <DEFAULT_ASSISTANT_ID>,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": "and you?"
                    }
                ]
            },
            "stream_mode": [
                "updates"
            ]
        }' | \
        sed 's/\r$//' | \
        awk '
        /^event:/ {
            if (data_content != "") {
                print data_content "\n"
            }
            sub(/^event: /, "Receiving event of type: ", $0)
            printf "%s...\n", $0
            data_content = ""
        }
        /^data:/ {
            sub(/^data: /, "", $0)
            data_content = $0
        }
        END {
            if (data_content != "") {
                print data_content "\n\n"
            }
        }
    '
    ```

Output:

    Receiving event of type: metadata
    {'run_id': '1ef6722d-80b3-6fbb-9324-253796b1cd13'}


    Receiving event of type: updates
    {'agent': {'messages': [{'content': [{'text': 'I am an artificial intelligence created by Anthropic, not by OpenAI. I should not have stated that OpenAI created me, as that is incorrect. Anthropic is the company that developed and trained me using advanced language models and AI technology. I will be more careful about providing accurate information regarding my origins in the future.', 'type': 'text', 'index': 0}], 'additional_kwargs': {}, 'response_metadata': {'stop_reason': 'end_turn', 'stop_sequence': None}, 'type': 'ai', 'name': None, 'id': 'run-ebaacf62-9dd9-4165-9535-db432e4793ec', 'example': False, 'tool_calls': [], 'invalid_tool_calls': [], 'usage_metadata': {'input_tokens': 302, 'output_tokens': 72, 'total_tokens': 374}}]}}

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
