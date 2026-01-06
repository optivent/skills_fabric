## Summarize messages

The problem with trimming or removing messages, as shown above, is that you may lose information from culling of the message queue. Because of this, some applications benefit from a more sophisticated approach of summarizing the message history using a chat model.

![](../../concepts/img/memory/summary.png)

=== "In an agent"

    :::python
    To summarize message history in an agent, use @[`pre_model_hook`][create_react_agent] with a prebuilt [`SummarizationNode`](https://langchain-ai.github.io/langmem/reference/short_term/#langmem.short_term.SummarizationNode) abstraction:

    ```python
    from langchain_anthropic import ChatAnthropic
    from langmem.short_term import SummarizationNode, RunningSummary
    from langchain_core.messages.utils import count_tokens_approximately
    from langgraph.prebuilt import create_react_agent
    from langgraph.prebuilt.chat_agent_executor import AgentState
    from langgraph.checkpoint.memory import InMemorySaver
    from typing import Any

    model = ChatAnthropic(model="claude-3-7-sonnet-latest")

    summarization_node = SummarizationNode( # (1)!
        token_counter=count_tokens_approximately,
        model=model,
        max_tokens=384,
        max_summary_tokens=128,
        output_messages_key="llm_input_messages",
    )

    class State(AgentState):
        # NOTE: we're adding this key to keep track of previous summary information
        # to make sure we're not summarizing on every LLM call
        # highlight-next-line
        context: dict[str, RunningSummary]  # (2)!


    checkpointer = InMemorySaver() # (3)!

    agent = create_react_agent(
        model=model,
        tools=tools,
        # highlight-next-line
        pre_model_hook=summarization_node, # (4)!
        # highlight-next-line
        state_schema=State, # (5)!
        checkpointer=checkpointer,
    )
    ```

    1. The `InMemorySaver` is a checkpointer that stores the agent's state in memory. In a production setting, you would typically use a database or other persistent storage. Please review the [checkpointer documentation](../../reference/checkpoints.md) for more options. If you're deploying with **LangGraph Platform**, the platform will provide a production-ready checkpointer for you.
    2. The `context` key is added to the agent's state. The key contains book-keeping information for the summarization node. It is used to keep track of the last summary information and ensure that the agent doesn't summarize on every LLM call, which can be inefficient.
    3. The `checkpointer` is passed to the agent. This enables the agent to persist its state across invocations.
    4. The `pre_model_hook` is set to the `SummarizationNode`. This node will summarize the message history before sending it to the LLM. The summarization node will automatically handle the summarization process and update the agent's state with the new summary. You can replace this with a custom implementation if you prefer. Please see the @[create_react_agent][create_react_agent] API reference for more details.
    5. The `state_schema` is set to the `State` class, which is the custom state that contains an extra `context` key.
    :::

=== "In a workflow"

    :::python
    Prompting and orchestration logic can be used to summarize the message history. For example, in LangGraph you can extend the [`MessagesState`](../../concepts/low_level.md#working-with-messages-in-graph-state) to include a `summary` key:

    ```python
    from langgraph.graph import MessagesState
    class State(MessagesState):
        summary: str
    ```

    Then, you can generate a summary of the chat history, using any existing summary as context for the next summary. This `summarize_conversation` node can be called after some number of messages have accumulated in the `messages` state key.

    ```python
    def summarize_conversation(state: State):

        # First, we get any existing summary
        summary = state.get("summary", "")

        # Create our summarization prompt
        if summary:

            # A summary already exists
            summary_message = (
                f"This is a summary of the conversation to date: {summary}\n\n"
                "Extend the summary by taking into account the new messages above:"
            )

        else:
            summary_message = "Create a summary of the conversation above:"

        # Add prompt to our history
        messages = state["messages"] + [HumanMessage(content=summary_message)]
        response = model.invoke(messages)

        # Delete all but the 2 most recent messages
        delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
        return {"summary": response.content, "messages": delete_messages}
    ```
    :::

    :::js
    Prompting and orchestration logic can be used to summarize the message history. For example, in LangGraph you can extend the [`MessagesZodState`](../../concepts/low_level.md#working-with-messages-in-graph-state) to include a `summary` key:

    ```typescript
    import { MessagesZodState } from "@langchain/langgraph";
    import { z } from "zod";

    const State = MessagesZodState.merge(z.object({
      summary: z.string().optional(),
    }));
    ```

    Then, you can generate a summary of the chat history, using any existing summary as context for the next summary. This `summarizeConversation` node can be called after some number of messages have accumulated in the `messages` state key.

    ```typescript
    import { RemoveMessage, HumanMessage } from "@langchain/core/messages";

    const summarizeConversation = async (state: z.infer<typeof State>) => {
      // First, we get any existing summary
      const summary = state.summary || "";

      // Create our summarization prompt
      let summaryMessage: string;
      if (summary) {
        // A summary already exists
        summaryMessage =
          `This is a summary of the conversation to date: ${summary}\n\n` +
          "Extend the summary by taking into account the new messages above:";
      } else {
        summaryMessage = "Create a summary of the conversation above:";
      }

      // Add prompt to our history
      const messages = [
        ...state.messages,
        new HumanMessage({ content: summaryMessage })
      ];
      const response = await model.invoke(messages);

      // Delete all but the 2 most recent messages
      const deleteMessages = state.messages
        .slice(0, -2)
        .map(m => new RemoveMessage({ id: m.id }));

      return {
        summary: response.content,
        messages: deleteMessages
      };
    };
    ```
    :::

??? example "Full example: summarize messages"

    :::python
    ```python
    from typing import Any, TypedDict

    from langchain.chat_models import init_chat_model
    from langchain_core.messages import AnyMessage
    from langchain_core.messages.utils import count_tokens_approximately
    from langgraph.graph import StateGraph, START, MessagesState
    from langgraph.checkpoint.memory import InMemorySaver
    # highlight-next-line
    from langmem.short_term import SummarizationNode, RunningSummary

    model = init_chat_model("anthropic:claude-3-7-sonnet-latest")
    summarization_model = model.bind(max_tokens=128)

    class State(MessagesState):
        # highlight-next-line
        context: dict[str, RunningSummary]  # (1)!

    class LLMInputState(TypedDict):  # (2)!
        summarized_messages: list[AnyMessage]
        context: dict[str, RunningSummary]

    # highlight-next-line
    summarization_node = SummarizationNode(
        token_counter=count_tokens_approximately,
        model=summarization_model,
        max_tokens=256,
        max_tokens_before_summary=256,
        max_summary_tokens=128,
    )

    # highlight-next-line
    def call_model(state: LLMInputState):  # (3)!
        response = model.invoke(state["summarized_messages"])
        return {"messages": [response]}

    checkpointer = InMemorySaver()
    builder = StateGraph(State)
    builder.add_node(call_model)
    # highlight-next-line
    builder.add_node("summarize", summarization_node)
    builder.add_edge(START, "summarize")
    builder.add_edge("summarize", "call_model")
    graph = builder.compile(checkpointer=checkpointer)

    # Invoke the graph
    config = {"configurable": {"thread_id": "1"}}
    graph.invoke({"messages": "hi, my name is bob"}, config)
    graph.invoke({"messages": "write a short poem about cats"}, config)
    graph.invoke({"messages": "now do the same but for dogs"}, config)
    final_response = graph.invoke({"messages": "what's my name?"}, config)

    final_response["messages"][-1].pretty_print()
    print("\nSummary:", final_response["context"]["running_summary"].summary)
    ```

    1. We will keep track of our running summary in the `context` field
    (expected by the `SummarizationNode`).
    2. Define private state that will be used only for filtering
    the inputs to `call_model` node.
    3. We're passing a private input state here to isolate the messages returned by the summarization node

    ```
    ================================== Ai Message ==================================

    From our conversation, I can see that you introduced yourself as Bob. That's the name you shared with me when we began talking.

    Summary: In this conversation, I was introduced to Bob, who then asked me to write a poem about cats. I composed a poem titled "The Mystery of Cats" that captured cats' graceful movements, independent nature, and their special relationship with humans. Bob then requested a similar poem about dogs, so I wrote "The Joy of Dogs," which highlighted dogs' loyalty, enthusiasm, and loving companionship. Both poems were written in a similar style but emphasized the distinct characteristics that make each pet special.
    ```
    :::

    :::js
    ```typescript
    import { ChatAnthropic } from "@langchain/anthropic";
    import {
      SystemMessage,
      HumanMessage,
      RemoveMessage,
      type BaseMessage
    } from "@langchain/core/messages";
    import {
      MessagesZodState,
      StateGraph,
      START,
      END,
      MemorySaver,
    } from "@langchain/langgraph";
    import { z } from "zod";
    import { v4 as uuidv4 } from "uuid";

    const memory = new MemorySaver();

    // We will add a `summary` attribute (in addition to `messages` key,
    // which MessagesZodState already has)
    const GraphState = z.object({
      messages: MessagesZodState.shape.messages,
      summary: z.string().default(""),
    });

    // We will use this model for both the conversation and the summarization
    const model = new ChatAnthropic({ model: "claude-3-haiku-20240307" });

    // Define the logic to call the model
    const callModel = async (state: z.infer<typeof GraphState>) => {
      // If a summary exists, we add this in as a system message
      const { summary } = state;
      let { messages } = state;
      if (summary) {
        const systemMessage = new SystemMessage({
          id: uuidv4(),
          content: `Summary of conversation earlier: ${summary}`,
        });
        messages = [systemMessage, ...messages];
      }
      const response = await model.invoke(messages);
      // We return an object, because this will get added to the existing state
      return { messages: [response] };
    };

    // We now define the logic for determining whether to end or summarize the conversation
    const shouldContinue = (state: z.infer<typeof GraphState>) => {
      const messages = state.messages;
      // If there are more than six messages, then we summarize the conversation
      if (messages.length > 6) {
        return "summarize_conversation";
      }
      // Otherwise we can just end
      return END;
    };

    const summarizeConversation = async (state: z.infer<typeof GraphState>) => {
      // First, we summarize the conversation
      const { summary, messages } = state;
      let summaryMessage: string;
      if (summary) {
        // If a summary already exists, we use a different system prompt
        // to summarize it than if one didn't
        summaryMessage =
          `This is summary of the conversation to date: ${summary}\n\n` +
          "Extend the summary by taking into account the new messages above:";
      } else {
        summaryMessage = "Create a summary of the conversation above:";
      }

      const allMessages = [
        ...messages,
        new HumanMessage({ id: uuidv4(), content: summaryMessage }),
      ];

      const response = await model.invoke(allMessages);

      // We now need to delete messages that we no longer want to show up
      // I will delete all but the last two messages, but you can change this
      const deleteMessages = messages
        .slice(0, -2)
        .map((m) => new RemoveMessage({ id: m.id! }));

      if (typeof response.content !== "string") {
        throw new Error("Expected a string response from the model");
      }

      return { summary: response.content, messages: deleteMessages };
    };

    // Define a new graph
    const workflow = new StateGraph(GraphState)
      // Define the conversation node and the summarize node
      .addNode("conversation", callModel)
      .addNode("summarize_conversation", summarizeConversation)
      // Set the entrypoint as conversation
      .addEdge(START, "conversation")
      // We now add a conditional edge
      .addConditionalEdges(
        // First, we define the start node. We use `conversation`.
        // This means these are the edges taken after the `conversation` node is called.
        "conversation",
        // Next, we pass in the function that will determine which node is called next.
        shouldContinue,
      )
      // We now add a normal edge from `summarize_conversation` to END.
      // This means that after `summarize_conversation` is called, we end.
      .addEdge("summarize_conversation", END);

    // Finally, we compile it!
    const app = workflow.compile({ checkpointer: memory });
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`pre_model_hook`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1942) (function in prebuilt)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`prompt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L566) (function in prebuilt)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`call_model`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6930) (function in langgraph)
