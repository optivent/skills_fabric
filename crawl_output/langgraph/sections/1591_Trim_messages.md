## Trim messages

Most LLMs have a maximum supported context window (denominated in tokens). One way to decide when to truncate messages is to count the tokens in the message history and truncate whenever it approaches that limit. If you're using LangChain, you can use the trim messages utility and specify the number of tokens to keep from the list, as well as the `strategy` (e.g., keep the last `maxTokens`) to use for handling the boundary.

=== "In an agent"

    :::python
    To trim message history in an agent, use @[`pre_model_hook`][create_react_agent] with the [`trim_messages`](https://python.langchain.com/api_reference/core/messages/langchain_core.messages.utils.trim_messages.html) function:

    ```python
    # highlight-next-line
    from langchain_core.messages.utils import (
        # highlight-next-line
        trim_messages,
        # highlight-next-line
        count_tokens_approximately
    # highlight-next-line
    )
    from langgraph.prebuilt import create_react_agent

    # This function will be called every time before the node that calls LLM
    def pre_model_hook(state):
        trimmed_messages = trim_messages(
            state["messages"],
            strategy="last",
            token_counter=count_tokens_approximately,
            max_tokens=384,
            start_on="human",
            end_on=("human", "tool"),
        )
        # highlight-next-line
        return {"llm_input_messages": trimmed_messages}

    checkpointer = InMemorySaver()
    agent = create_react_agent(
        model,
        tools,
        # highlight-next-line
        pre_model_hook=pre_model_hook,
        checkpointer=checkpointer,
    )
    ```
    :::

    :::js
    To trim message history in an agent, use `stateModifier` with the [`trimMessages`](https://js.langchain.com/docs/how_to/trim_messages/) function:

    ```typescript
    import { trimMessages } from "@langchain/core/messages";
    import { createReactAgent } from "@langchain/langgraph/prebuilt";

    // This function will be called every time before the node that calls LLM
    const stateModifier = async (state) => {
      return trimMessages(state.messages, {
        strategy: "last",
        maxTokens: 384,
        startOn: "human",
        endOn: ["human", "tool"],
      });
    };

    const checkpointer = new MemorySaver();
    const agent = createReactAgent({
      llm: model,
      tools,
      stateModifier,
      checkpointer,
    });
    ```
    :::

=== "In a workflow"

    :::python
    To trim message history, use the [`trim_messages`](https://python.langchain.com/api_reference/core/messages/langchain_core.messages.utils.trim_messages.html) function:

    ```python
    # highlight-next-line
    from langchain_core.messages.utils import (
        # highlight-next-line
        trim_messages,
        # highlight-next-line
        count_tokens_approximately
    # highlight-next-line
    )

    def call_model(state: MessagesState):
        # highlight-next-line
        messages = trim_messages(
            state["messages"],
            strategy="last",
            token_counter=count_tokens_approximately,
            max_tokens=128,
            start_on="human",
            end_on=("human", "tool"),
        )
        response = model.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node(call_model)
    ...
    ```
    :::

    :::js
    To trim message history, use the [`trimMessages`](https://js.langchain.com/docs/how_to/trim_messages/) function:

    ```typescript
    import { trimMessages } from "@langchain/core/messages";

    const callModel = async (state: z.infer<typeof MessagesZodState>) => {
      const messages = trimMessages(state.messages, {
        strategy: "last",
        maxTokens: 128,
        startOn: "human",
        endOn: ["human", "tool"],
      });
      const response = await model.invoke(messages);
      return { messages: [response] };
    };

    const builder = new StateGraph(MessagesZodState)
      .addNode("call_model", callModel);
    // ...
    ```
    :::

??? example "Full example: trim messages"

    :::python
    ```python
    # highlight-next-line
    from langchain_core.messages.utils import (
        # highlight-next-line
        trim_messages,
        # highlight-next-line
        count_tokens_approximately
    # highlight-next-line
    )
    from langchain.chat_models import init_chat_model
    from langgraph.graph import StateGraph, START, MessagesState

    model = init_chat_model("anthropic:claude-3-7-sonnet-latest")
    summarization_model = model.bind(max_tokens=128)

    def call_model(state: MessagesState):
        # highlight-next-line
        messages = trim_messages(
            state["messages"],
            strategy="last",
            token_counter=count_tokens_approximately,
            max_tokens=128,
            start_on="human",
            end_on=("human", "tool"),
        )
        response = model.invoke(messages)
        return {"messages": [response]}

    checkpointer = InMemorySaver()
    builder = StateGraph(MessagesState)
    builder.add_node(call_model)
    builder.add_edge(START, "call_model")
    graph = builder.compile(checkpointer=checkpointer)

    config = {"configurable": {"thread_id": "1"}}
    graph.invoke({"messages": "hi, my name is bob"}, config)
    graph.invoke({"messages": "write a short poem about cats"}, config)
    graph.invoke({"messages": "now do the same but for dogs"}, config)
    final_response = graph.invoke({"messages": "what's my name?"}, config)

    final_response["messages"][-1].pretty_print()
    ```

    ```
    ================================== Ai Message ==================================

    Your name is Bob, as you mentioned when you first introduced yourself.
    ```
    :::

    :::js
    ```typescript
    import { trimMessages } from "@langchain/core/messages";
    import { ChatAnthropic } from "@langchain/anthropic";
    import { StateGraph, START, MessagesZodState, MemorySaver } from "@langchain/langgraph";
    import { z } from "zod";

    const model = new ChatAnthropic({ model: "claude-3-5-sonnet-20241022" });

    const callModel = async (state: z.infer<typeof MessagesZodState>) => {
      const messages = trimMessages(state.messages, {
        strategy: "last",
        maxTokens: 128,
        startOn: "human",
        endOn: ["human", "tool"],
      });
      const response = await model.invoke(messages);
      return { messages: [response] };
    };

    const checkpointer = new MemorySaver();
    const builder = new StateGraph(MessagesZodState)
      .addNode("call_model", callModel)
      .addEdge(START, "call_model");
    const graph = builder.compile({ checkpointer });

    const config = { configurable: { thread_id: "1" } };
    await graph.invoke({ messages: [{ role: "user", content: "hi, my name is bob" }] }, config);
    await graph.invoke({ messages: [{ role: "user", content: "write a short poem about cats" }] }, config);
    await graph.invoke({ messages: [{ role: "user", content: "now do the same but for dogs" }] }, config);
    const finalResponse = await graph.invoke({ messages: [{ role: "user", content: "what's my name?" }] }, config);

    console.log(finalResponse.messages.at(-1)?.content);
    ```

    ```
    Your name is Bob, as you mentioned when you first introduced yourself.
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`pre_model_hook`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1942) (function in prebuilt)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`call_model`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6930) (function in langgraph)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
