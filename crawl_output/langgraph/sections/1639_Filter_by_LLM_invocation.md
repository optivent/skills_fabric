## Filter by LLM invocation

You can associate `tags` with LLM invocations to filter the streamed tokens by LLM invocation.

:::python

```python
from langchain.chat_models import init_chat_model

llm_1 = init_chat_model(model="openai:gpt-4o-mini", tags=['joke']) # (1)!
llm_2 = init_chat_model(model="openai:gpt-4o-mini", tags=['poem']) # (2)!

graph = ... # define a graph that uses these LLMs

async for msg, metadata in graph.astream(  # (3)!
    {"topic": "cats"},
    # highlight-next-line
    stream_mode="messages",
):
    if metadata["tags"] == ["joke"]: # (4)!
        print(msg.content, end="|", flush=True)
```

1. llm_1 is tagged with "joke".
2. llm_2 is tagged with "poem".
3. The `stream_mode` is set to "messages" to stream LLM tokens. The `metadata` contains information about the LLM invocation, including the tags.
4. Filter the streamed tokens by the `tags` field in the metadata to only include the tokens from the LLM invocation with the "joke" tag.
   :::

:::js

```typescript
import { ChatOpenAI } from "@langchain/openai";

const llm1 = new ChatOpenAI({
  model: "gpt-4o-mini",
  tags: ['joke'] // (1)!
});
const llm2 = new ChatOpenAI({
  model: "gpt-4o-mini",
  tags: ['poem'] // (2)!
});

const graph = // ... define a graph that uses these LLMs

for await (const [msg, metadata] of await graph.stream( // (3)!
  { topic: "cats" },
  { streamMode: "messages" }
)) {
  if (metadata.tags?.includes("joke")) { // (4)!
    console.log(msg.content + "|");
  }
}
```

1. llm1 is tagged with "joke".
2. llm2 is tagged with "poem".
3. The `streamMode` is set to "messages" to stream LLM tokens. The `metadata` contains information about the LLM invocation, including the tags.
4. Filter the streamed tokens by the `tags` field in the metadata to only include the tokens from the LLM invocation with the "joke" tag.
   :::

??? example "Extended example: filtering by tags"

      :::python
      ```python
      from typing import TypedDict

      from langchain.chat_models import init_chat_model
      from langgraph.graph import START, StateGraph

      joke_model = init_chat_model(model="openai:gpt-4o-mini", tags=["joke"]) # (1)!
      poem_model = init_chat_model(model="openai:gpt-4o-mini", tags=["poem"]) # (2)!


      class State(TypedDict):
            topic: str
            joke: str
            poem: str


      async def call_model(state, config):
            topic = state["topic"]
            print("Writing joke...")
            # Note: Passing the config through explicitly is required for python < 3.11
            # Since context var support wasn't added before then: https://docs.python.org/3/library/asyncio-task.html#creating-tasks
            joke_response = await joke_model.ainvoke(
                  [{"role": "user", "content": f"Write a joke about {topic}"}],
                  config, # (3)!
            )
            print("\n\nWriting poem...")
            poem_response = await poem_model.ainvoke(
                  [{"role": "user", "content": f"Write a short poem about {topic}"}],
                  config, # (3)!
            )
            return {"joke": joke_response.content, "poem": poem_response.content}


      graph = (
            StateGraph(State)
            .add_node(call_model)
            .add_edge(START, "call_model")
            .compile()
      )

      async for msg, metadata in graph.astream(
            {"topic": "cats"},
            # highlight-next-line
            stream_mode="messages", # (4)!
      ):
          if metadata["tags"] == ["joke"]: # (4)!
              print(msg.content, end="|", flush=True)
      ```

      1. The `joke_model` is tagged with "joke".
      2. The `poem_model` is tagged with "poem".
      3. The `config` is passed through explicitly to ensure the context vars are propagated correctly. This is required for Python < 3.11 when using async code. Please see the [async section](#async) for more details.
      4. The `stream_mode` is set to "messages" to stream LLM tokens. The `metadata` contains information about the LLM invocation, including the tags.
      :::

      :::js
      ```typescript
      import { ChatOpenAI } from "@langchain/openai";
      import { StateGraph, START } from "@langchain/langgraph";
      import { z } from "zod";

      const jokeModel = new ChatOpenAI({
        model: "gpt-4o-mini",
        tags: ["joke"] // (1)!
      });
      const poemModel = new ChatOpenAI({
        model: "gpt-4o-mini",
        tags: ["poem"] // (2)!
      });

      const State = z.object({
        topic: z.string(),
        joke: z.string(),
        poem: z.string(),
      });

      const graph = new StateGraph(State)
        .addNode("callModel", (state) => {
          const topic = state.topic;
          console.log("Writing joke...");

          const jokeResponse = await jokeModel.invoke([
            { role: "user", content: `Write a joke about ${topic}` }
          ]);

          console.log("\n\nWriting poem...");
          const poemResponse = await poemModel.invoke([
            { role: "user", content: `Write a short poem about ${topic}` }
          ]);

          return {
            joke: jokeResponse.content,
            poem: poemResponse.content
          };
        })
        .addEdge(START, "callModel")
        .compile();

      for await (const [msg, metadata] of await graph.stream(
        { topic: "cats" },
        { streamMode: "messages" } // (3)!
      )) {
        if (metadata.tags?.includes("joke")) { // (4)!
          console.log(msg.content + "|");
        }
      }
      ```

      1. The `jokeModel` is tagged with "joke".
      2. The `poemModel` is tagged with "poem".
      3. The `streamMode` is set to "messages" to stream LLM tokens. The `metadata` contains information about the LLM invocation, including the tags.
      4. Filter the streamed tokens by the `tags` field in the metadata to only include the tokens from the LLM invocation with the "joke" tag.
      :::

### Source References

- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`call_model`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6930) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`flush`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/sse.py#L68) (function in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L387) (function in sdk-py)
