## 3. Generate query

Now we will start building components ([nodes](../../concepts/low_level.md#nodes) and [edges](../../concepts/low_level.md#edges)) for our agentic RAG graph.

:::python
Note that the components will operate on the [`MessagesState`](../../concepts/low_level.md#messagesstate) — graph state that contains a `messages` key with a list of [chat messages](https://python.langchain.com/docs/concepts/messages/).
:::

:::js
Note that the components will operate on the `MessagesZodState` — graph state that contains a `messages` key with a list of [chat messages](https://js.langchain.com/docs/concepts/messages/).
:::

1. Build a `generate_query_or_respond` node. It will call an LLM to generate a response based on the current graph state (list of messages). Given the input messages, it will decide to retrieve using the retriever tool, or respond directly to the user. Note that we're giving the chat model access to the `retriever_tool` we created earlier via `.bind_tools`:

    ```python
    from langgraph.graph import MessagesState
    from langchain.chat_models import init_chat_model

    response_model = init_chat_model("openai:gpt-4.1", temperature=0)


    def generate_query_or_respond(state: MessagesState):
        """Call the model to generate a response based on the current state. Given
        the question, it will decide to retrieve using the retriever tool, or simply respond to the user.
        """
        response = (
            response_model
            # highlight-next-line
            .bind_tools([retriever_tool]).invoke(state["messages"])
        )
        return {"messages": [response]}
    ```

2. Try it on a random input:

    ```python
    input = {"messages": [{"role": "user", "content": "hello!"}]}
    generate_query_or_respond(input)["messages"][-1].pretty_print()
    ```

    **Output:**
    ```
    ================================== Ai Message ==================================

    Hello! How can I help you today?
    ```

3. Ask a question that requires semantic search:

    ```python
    input = {
        "messages": [
            {
                "role": "user",
                "content": "What does Lilian Weng say about types of reward hacking?",
            }
        ]
    }
    generate_query_or_respond(input)["messages"][-1].pretty_print()
    ```

    **Output:**
    ```
    ================================== Ai Message ==================================
    Tool Calls:
    retrieve_blog_posts (call_tYQxgfIlnQUDMdtAhdbXNwIM)
    Call ID: call_tYQxgfIlnQUDMdtAhdbXNwIM
    Args:
        query: types of reward hacking
    ```

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`bind_tools`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/react_agent.py#L19) (function in langgraph)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`search`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L771) (function in checkpoint)
- [`list`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L174) (function in checkpoint)
