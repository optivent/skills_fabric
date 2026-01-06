## 3. Interact with your chatbot

Now you can interact with your bot!

1.  Pick a thread to use as the key for this conversation.

    :::python

    ```python
    config = {"configurable": {"thread_id": "1"}}
    ```

    :::

    :::js

    ```typescript
    const config = { configurable: { thread_id: "1" } };
    ```

    :::

2.  Call your chatbot:

    :::python

    ```python
    user_input = "Hi there! My name is Will."

    # The config is the **second positional argument** to stream() or invoke()!
    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
        stream_mode="values",
    )
    for event in events:
        event["messages"][-1].pretty_print()
    ```

    ```
    ================================ Human Message =================================

    Hi there! My name is Will.
    ================================== Ai Message ==================================

    Hello Will! It's nice to meet you. How can I assist you today? Is there anything specific you'd like to know or discuss?
    ```

    !!! note

        The config was provided as the **second positional argument** when calling our graph. It importantly is _not_ nested within the graph inputs (`{'messages': []}`).

    :::

    :::js

    ```typescript
    const userInput = "Hi there! My name is Will.";

    const events = await graph.stream(
      { messages: [{ type: "human", content: userInput }] },
      { configurable: { thread_id: "1" }, streamMode: "values" }
    );

    for await (const event of events) {
      const lastMessage = event.messages.at(-1);
      console.log(`${lastMessage?.getType()}: ${lastMessage?.text}`);
    }
    ```

    ```
    human: Hi there! My name is Will.
    ai: Hello Will! It's nice to meet you. How can I assist you today? Is there anything specific you'd like to know or discuss?
    ```

    !!! note
    !!! note

        The config was provided as the **second parameter** when calling our graph. It importantly is _not_ nested within the graph inputs (`{"messages": []}`).

    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`read`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1044) (class in sdk-py)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`a`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4642) (function in langgraph)
