## High-level API

LangGraph provides two high-level APIs for creating a Pregel application: the [StateGraph (Graph API)](./low_level.md) and the [Functional API](functional_api.md).

=== "StateGraph (Graph API)"

    :::python

    The @[StateGraph (Graph API)][StateGraph] is a higher-level abstraction that simplifies the creation of Pregel applications. It allows you to define a graph of nodes and edges. When you compile the graph, the StateGraph API automatically creates the Pregel application for you.

    ```python
    from typing import TypedDict, Optional

    from langgraph.constants import START
    from langgraph.graph import StateGraph

    class Essay(TypedDict):
        topic: str
        content: Optional[str]
        score: Optional[float]

    def write_essay(essay: Essay):
        return {
            "content": f"Essay about {essay['topic']}",
        }

    def score_essay(essay: Essay):
        return {
            "score": 10
        }

    builder = StateGraph(Essay)
    builder.add_node(write_essay)
    builder.add_node(score_essay)
    builder.add_edge(START, "write_essay")

    # Compile the graph.
    # This will return a Pregel instance.
    graph = builder.compile()
    ```
    :::

    :::js

    The @[StateGraph (Graph API)][StateGraph] is a higher-level abstraction that simplifies the creation of Pregel applications. It allows you to define a graph of nodes and edges. When you compile the graph, the StateGraph API automatically creates the Pregel application for you.

    ```typescript
    import { START, StateGraph } from "@langchain/langgraph";

    interface Essay {
      topic: string;
      content?: string;
      score?: number;
    }

    const writeEssay = (essay: Essay) => {
      return {
        content: `Essay about ${essay.topic}`,
      };
    };

    const scoreEssay = (essay: Essay) => {
      return {
        score: 10
      };
    };

    const builder = new StateGraph<Essay>({
      channels: {
        topic: null,
        content: null,
        score: null,
      }
    })
      .addNode("writeEssay", writeEssay)
      .addNode("scoreEssay", scoreEssay)
      .addEdge(START, "writeEssay");

    // Compile the graph.
    // This will return a Pregel instance.
    const graph = builder.compile();
    ```
    :::

    The compiled Pregel instance will be associated with a list of nodes and channels. You can inspect the nodes and channels by printing them.

    :::python
    ```python
    print(graph.nodes)
    ```

    You will see something like this:

    ```pycon
    {'__start__': <langgraph.pregel.read.PregelNode at 0x7d05e3ba1810>,
     'write_essay': <langgraph.pregel.read.PregelNode at 0x7d05e3ba14d0>,
     'score_essay': <langgraph.pregel.read.PregelNode at 0x7d05e3ba1710>}
    ```

    ```python
    print(graph.channels)
    ```

    You should see something like this

    ```pycon
    {'topic': <langgraph.channels.last_value.LastValue at 0x7d05e3294d80>,
     'content': <langgraph.channels.last_value.LastValue at 0x7d05e3295040>,
     'score': <langgraph.channels.last_value.LastValue at 0x7d05e3295980>,
     '__start__': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e3297e00>,
     'write_essay': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e32960c0>,
     'score_essay': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e2d8ab80>,
     'branch:__start__:__self__:write_essay': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e32941c0>,
     'branch:__start__:__self__:score_essay': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e2d88800>,
     'branch:write_essay:__self__:write_essay': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e3295ec0>,
     'branch:write_essay:__self__:score_essay': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e2d8ac00>,
     'branch:score_essay:__self__:write_essay': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e2d89700>,
     'branch:score_essay:__self__:score_essay': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e2d8b400>,
     'start:write_essay': <langgraph.channels.ephemeral_value.EphemeralValue at 0x7d05e2d8b280>}
    ```
    :::

    :::js
    ```typescript
    console.log(graph.nodes);
    ```

    You will see something like this:

    ```console
    {
      __start__: PregelNode { ... },
      writeEssay: PregelNode { ... },
      scoreEssay: PregelNode { ... }
    }
    ```

    ```typescript
    console.log(graph.channels);
    ```

    You should see something like this

    ```console
    {
      topic: LastValue { ... },
      content: LastValue { ... },
      score: LastValue { ... },
      __start__: EphemeralValue { ... },
      writeEssay: EphemeralValue { ... },
      scoreEssay: EphemeralValue { ... },
      'branch:__start__:__self__:writeEssay': EphemeralValue { ... },
      'branch:__start__:__self__:scoreEssay': EphemeralValue { ... },
      'branch:writeEssay:__self__:writeEssay': EphemeralValue { ... },
      'branch:writeEssay:__self__:scoreEssay': EphemeralValue { ... },
      'branch:scoreEssay:__self__:writeEssay': EphemeralValue { ... },
      'branch:scoreEssay:__self__:scoreEssay': EphemeralValue { ... },
      'start:writeEssay': EphemeralValue { ... }
    }
    ```
    :::

=== "Functional API"

    :::python

    In the [Functional API](functional_api.md), you can use an @[`entrypoint`][entrypoint] to create a Pregel application. The `entrypoint` decorator allows you to define a function that takes input and returns output.

    ```python
    from typing import TypedDict, Optional

    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.func import entrypoint

    class Essay(TypedDict):
        topic: str
        content: Optional[str]
        score: Optional[float]


    checkpointer = InMemorySaver()

    @entrypoint(checkpointer=checkpointer)
    def write_essay(essay: Essay):
        return {
            "content": f"Essay about {essay['topic']}",
        }

    print("Nodes: ")
    print(write_essay.nodes)
    print("Channels: ")
    print(write_essay.channels)
    ```

    ```pycon
    Nodes:
    {'write_essay': <langgraph.pregel.read.PregelNode object at 0x7d05e2f9aad0>}
    Channels:
    {'__start__': <langgraph.channels.ephemeral_value.EphemeralValue object at 0x7d05e2c906c0>, '__end__': <langgraph.channels.last_value.LastValue object at 0x7d05e2c90c40>, '__previous__': <langgraph.channels.last_value.LastValue object at 0x7d05e1007280>}
    ```
    :::

    :::js

    In the [Functional API](functional_api.md), you can use an @[`entrypoint`][entrypoint] to create a Pregel application. The `entrypoint` decorator allows you to define a function that takes input and returns output.

    ```typescript
    import { MemorySaver } from "@langchain/langgraph";
    import { entrypoint } from "@langchain/langgraph/func";

    interface Essay {
      topic: string;
      content?: string;
      score?: number;
    }

    const checkpointer = new MemorySaver();

    const writeEssay = entrypoint(
      { checkpointer, name: "writeEssay" },
      async (essay: Essay) => {
        return {
          content: `Essay about ${essay.topic}`,
        };
      }
    );

    console.log("Nodes: ");
    console.log(writeEssay.nodes);
    console.log("Channels: ");
    console.log(writeEssay.channels);
    ```

    ```console
    Nodes:
    { writeEssay: PregelNode { ... } }
    Channels:
    {
      __start__: EphemeralValue { ... },
      __end__: LastValue { ... },
      __previous__: LastValue { ... }
    }
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`list`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L174) (function in checkpoint)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`read`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1044) (class in sdk-py)
- [`decorator`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/func/__init__.py#L207) (function in langgraph)
