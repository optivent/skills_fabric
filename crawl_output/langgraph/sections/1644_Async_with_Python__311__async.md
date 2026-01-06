## Async with Python < 3.11 { #async }

In Python versions < 3.11, [asyncio tasks](https://docs.python.org/3/library/asyncio-task.html#asyncio.create_task) do not support the `context` parameter.  
This limits LangGraph ability to automatically propagate context, and affects LangGraph's streaming mechanisms in two key ways:

1. You **must** explicitly pass [`RunnableConfig`](https://python.langchain.com/docs/concepts/runnables/#runnableconfig) into async LLM calls (e.g., `ainvoke()`), as callbacks are not automatically propagated.
2. You **cannot** use `get_stream_writer()` in async nodes or tools — you must pass a `writer` argument directly.

??? example "Extended example: async LLM call with manual config"

      ```python
      from typing import TypedDict
      from langgraph.graph import START, StateGraph
      from langchain.chat_models import init_chat_model

      llm = init_chat_model(model="openai:gpt-4o-mini")

      class State(TypedDict):
          topic: str
          joke: str

      async def call_model(state, config): # (1)!
          topic = state["topic"]
          print("Generating joke...")
          joke_response = await llm.ainvoke(
              [{"role": "user", "content": f"Write a joke about {topic}"}],
              # highlight-next-line
              config, # (2)!
          )
          return {"joke": joke_response.content}

      graph = (
          StateGraph(State)
          .add_node(call_model)
          .add_edge(START, "call_model")
          .compile()
      )

      async for chunk, metadata in graph.astream(
          {"topic": "ice cream"},
          # highlight-next-line
          stream_mode="messages", # (3)!
      ):
          if chunk.content:
              print(chunk.content, end="|", flush=True)
      ```

      1. Accept `config` as an argument in the async node function.
      2. Pass `config` to `llm.ainvoke()` to ensure proper context propagation.
      3. Set `stream_mode="messages"` to stream LLM tokens.

??? example "Extended example: async custom streaming with stream writer"

      ```python
      from typing import TypedDict
      from langgraph.types import StreamWriter

      class State(TypedDict):
            topic: str
            joke: str

      # highlight-next-line
      async def generate_joke(state: State, writer: StreamWriter): # (1)!
            writer({"custom_key": "Streaming custom data while generating a joke"})
            return {"joke": f"This is a joke about {state['topic']}"}

      graph = (
            StateGraph(State)
            .add_node(generate_joke)
            .add_edge(START, "generate_joke")
            .compile()
      )

      async for chunk in graph.astream(
            {"topic": "ice cream"},
            # highlight-next-line
            stream_mode="custom", # (2)!
      ):
            print(chunk)
      ```

      1. Add `writer` as an argument in the function signature of the async node or tool. LangGraph will automatically pass the stream writer to the function.
      2. Set `stream_mode="custom"` to receive the custom data in the stream.

:::

### Source References

- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`call_model`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6930) (function in langgraph)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
