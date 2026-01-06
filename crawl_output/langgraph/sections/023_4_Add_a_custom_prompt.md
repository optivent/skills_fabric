## 4. Add a custom prompt

Prompts instruct the LLM how to behave. Add one of the following types of prompts:

- **Static**: A string is interpreted as a **system message**.
- **Dynamic**: A list of messages generated at **runtime**, based on input or configuration.

=== "Static prompt"

    Define a fixed prompt string or list of messages:

    :::python
    ```python
    from langgraph.prebuilt import create_react_agent

    agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=[get_weather],
        # A static prompt that never changes
        # highlight-next-line
        prompt="Never answer questions about the weather."
    )

    agent.invoke(
        {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
    )
    ```
    :::

    :::js
    ```typescript
    import { createReactAgent } from "@langchain/langgraph/prebuilt";
    import { ChatAnthropic } from "@langchain/anthropic";

    const agent = createReactAgent({
      llm: new ChatAnthropic({ model: "anthropic:claude-3-5-sonnet-latest" }),
      tools: [getWeather],
      // A static prompt that never changes
      // highlight-next-line
      stateModifier: "Never answer questions about the weather."
    });

    await agent.invoke({
      messages: [{ role: "user", content: "what is the weather in sf" }]
    });
    ```
    :::

=== "Dynamic prompt"

    :::python
    Define a function that returns a message list based on the agent's state and configuration:

    ```python
    from langchain_core.messages import AnyMessage
    from langchain_core.runnables import RunnableConfig
    from langgraph.prebuilt.chat_agent_executor import AgentState
    from langgraph.prebuilt import create_react_agent

    # highlight-next-line
    def prompt(state: AgentState, config: RunnableConfig) -> list[AnyMessage]:  # (1)!
        user_name = config["configurable"].get("user_name")
        system_msg = f"You are a helpful assistant. Address the user as {user_name}."
        return [{"role": "system", "content": system_msg}] + state["messages"]

    agent = create_react_agent(
        model="anthropic:claude-3-7-sonnet-latest",
        tools=[get_weather],
        # highlight-next-line
        prompt=prompt
    )

    agent.invoke(
        {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
        # highlight-next-line
        config={"configurable": {"user_name": "John Smith"}}
    )
    ```

    1. Dynamic prompts allow including non-message [context](./context.md) when constructing an input to the LLM, such as:

        - Information passed at runtime, like a `user_id` or API credentials (using `config`).
        - Internal agent state updated during a multi-step reasoning process (using `state`).

        Dynamic prompts can be defined as functions that take `state` and `config` and return a list of messages to send to the LLM.
    :::

    :::js
    Define a function that returns messages based on the agent's state and configuration:

    ```typescript
    import { type BaseMessageLike } from "@langchain/core/messages";
    import { type RunnableConfig } from "@langchain/core/runnables";
    import { createReactAgent } from "@langchain/langgraph/prebuilt";

    // highlight-next-line
    const dynamicPrompt = (state: { messages: BaseMessageLike[] }, config: RunnableConfig): BaseMessageLike[] => {  // (1)!
      const userName = config.configurable?.user_name;
      const systemMsg = `You are a helpful assistant. Address the user as ${userName}.`;
      return [{ role: "system", content: systemMsg }, ...state.messages];
    };

    const agent = createReactAgent({
      llm: "anthropic:claude-3-5-sonnet-latest",
      tools: [getWeather],
      // highlight-next-line
      stateModifier: dynamicPrompt
    });

    await agent.invoke(
      { messages: [{ role: "user", content: "what is the weather in sf" }] },
      // highlight-next-line
      { configurable: { user_name: "John Smith" } }
    );
    ```

    1. Dynamic prompts allow including non-message [context](./context.md) when constructing an input to the LLM, such as:

        - Information passed at runtime, like a `user_id` or API credentials (using `config`).
        - Internal agent state updated during a multi-step reasoning process (using `state`).

        Dynamic prompts can be defined as functions that take `state` and `config` and return a list of messages to send to the LLM.
    :::

For more information, see [Context](./context.md).

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`prompt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L566) (function in prebuilt)
- [`get_weather`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L6455) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`AgentState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/example_app/example_graph.py#L12) (class in langgraph)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
