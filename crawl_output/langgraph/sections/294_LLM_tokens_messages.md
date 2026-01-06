## LLM tokens {#messages}

Use the `messages-tuple` streaming mode to stream Large Language Model (LLM) outputs **token by token** from any part of your graph, including nodes, tools, subgraphs, or tasks.

The streamed output from [`messages-tuple` mode](#supported-stream-modes) is a tuple `(message_chunk, metadata)` where:

- `message_chunk`: the token or message segment from the LLM.
- `metadata`: a dictionary containing details about the graph node and LLM invocation.
 
??? example "Example graph"

    ```python
    from dataclasses import dataclass

    from langchain.chat_models import init_chat_model
    from langgraph.graph import StateGraph, START

    @dataclass
    class MyState:
        topic: str
        joke: str = ""

    llm = init_chat_model(model="openai:gpt-4o-mini")

    def call_model(state: MyState):
        """Call the LLM to generate a joke about a topic"""
        # highlight-next-line
        llm_response = llm.invoke( # (1)!
            [
                {"role": "user", "content": f"Generate a joke about {state.topic}"}
            ]
        )
        return {"joke": llm_response.content}

    graph = (
        StateGraph(MyState)
        .add_node(call_model)
        .add_edge(START, "call_model")
        .compile()
    )
    ```

    1. Note that the message events are emitted even when the LLM is run using `.invoke` rather than `.stream`.

=== "Python"

    ```python
    async for chunk in client.runs.stream(
        thread_id,
        assistant_id,
        input={"topic": "ice cream"},
        # highlight-next-line
        stream_mode="messages-tuple",
    ):
        if chunk.event != "messages":
            continue

        message_chunk, metadata = chunk.data  # (1)!
        if message_chunk["content"]:
            print(message_chunk["content"], end="|", flush=True)
    ```

    1. The "messages-tuple" stream mode returns an iterator of tuples `(message_chunk, metadata)` where `message_chunk` is the token streamed by the LLM and `metadata` is a dictionary with information about the graph node where the LLM was called and other information.

=== "JavaScript"

    ```js
    const streamResponse = client.runs.stream(
      threadID,
      assistantID,
      {
        input: { topic: "ice cream" },
        // highlight-next-line
        streamMode: "messages-tuple"
      }
    );
    for await (const chunk of streamResponse) {
      if (chunk.event !== "messages") {
        continue;
      }
      console.log(chunk.data[0]["content"]);  // (1)!
    }
    ```

    1. The "messages-tuple" stream mode returns an iterator of tuples `(message_chunk, metadata)` where `message_chunk` is the token streamed by the LLM and `metadata` is a dictionary with information about the graph node where the LLM was called and other information.

=== "cURL"

    ```bash
    curl --request POST \
    --url <DEPLOYMENT_URL>/threads/<THREAD_ID>/runs/stream \
    --header 'Content-Type: application/json' \
    --data "{
      \"assistant_id\": \"agent\",
      \"input\": {\"topic\": \"ice cream\"},
      \"stream_mode\": \"messages-tuple\"
    }"
    ```

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`call_model`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6930) (function in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`flush`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/sse.py#L68) (function in sdk-py)
