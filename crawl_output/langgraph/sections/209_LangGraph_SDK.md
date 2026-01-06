## LangGraph SDK

To edit the assistant, use the `update` method. This will create a new version of the assistant with the provided edits. See the [Python](https://langchain-ai.github.io/langgraph/cloud/reference/sdk/python_sdk_ref/#langgraph_sdk.client.AssistantsClient.update) and [JS](https://langchain-ai.github.io/langgraph/cloud/reference/sdk/js_ts_sdk_ref/#update) SDK reference docs for more information.

!!! note "Note"

    You must pass in the ENTIRE config (and metadata if you are using it). The update endpoint creates new versions completely from scratch and does not rely on previous versions.

For example, to update your assistant's system prompt:

=== "Python"

    ```python
    openai_assistant_v2 = await client.assistants.update(
        openai_assistant["assistant_id"],
        config={
            "configurable": {
                "model_name": "openai",
                "system_prompt": "You are an unhelpful assistant!",
            }
        },
    )
    ```

=== "Javascript"

    ```js
    const openaiAssistantV2 = await client.assistants.update(
        openai_assistant["assistant_id"],
        {
            config: {
                configurable: {
                    model_name: 'openai',
                    system_prompt: 'You are an unhelpful assistant!',
                },
        },
    });
    ```

=== "CURL"

    ```bash
    curl --request PATCH \
    --url <DEPOLYMENT_URL>/assistants/<ASSISTANT_ID> \
    --header 'Content-Type: application/json' \
    --data '{
    "config": {"model_name": "openai", "system_prompt": "You are an unhelpful assistant!"}
    }'
    ```

This will create a new version of the assistant with the updated parameters and set this as the active version of your assistant. If you now run your graph and pass in this assistant id, it will use this latest version.

### Source References

- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`prompt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L566) (function in prebuilt)
- [`AssistantsClient`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L614) (class in sdk-py)
- [`AssistantsClient.update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L964) (method in sdk-py)
- [`patch`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3753) (function in sdk-py)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Assistant`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L242) (class in sdk-py)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
