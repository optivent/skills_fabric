## Use time travel in a workflow

??? example "Example graph"

    ```python
    from typing_extensions import TypedDict, NotRequired
    from langgraph.graph import StateGraph, START, END
    from langchain.chat_models import init_chat_model
    from langgraph.checkpoint.memory import InMemorySaver

    class State(TypedDict):
        topic: NotRequired[str]
        joke: NotRequired[str]

    llm = init_chat_model(
        "anthropic:claude-3-7-sonnet-latest",
        temperature=0,
    )

    def generate_topic(state: State):
        """LLM call to generate a topic for the joke"""
        msg = llm.invoke("Give me a funny topic for a joke")
        return {"topic": msg.content}

    def write_joke(state: State):
        """LLM call to write a joke based on the topic"""
        msg = llm.invoke(f"Write a short joke about {state['topic']}")
        return {"joke": msg.content}

    # Build workflow
    builder = StateGraph(State)

    # Add nodes
    builder.add_node("generate_topic", generate_topic)
    builder.add_node("write_joke", write_joke)

    # Add edges to connect nodes
    builder.add_edge(START, "generate_topic")
    builder.add_edge("generate_topic", "write_joke")

    # Compile
    graph = builder.compile()
    ```

### Source References

- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`conn`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/conftest.py#L15) (function in checkpoint-postgres)
- [`dict`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L151) (function in checkpoint)
- [`InMemorySaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L31) (class in checkpoint)
- [`time`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/id.py#L61) (function in checkpoint)
- [`checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L124) (function in langgraph)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
