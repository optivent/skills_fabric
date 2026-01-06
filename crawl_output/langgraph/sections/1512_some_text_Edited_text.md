## > {'some_text': 'Edited text'}

```

1. `interrupt(...)` pauses execution at `human_node`, surfacing the given payload to a human.
2. Any JSON serializable value can be passed to the `interrupt` function. Here, a dict containing the text to revise.
3. Once resumed, the return value of `interrupt(...)` is the human-provided input, which is used to update the state.
4. A checkpointer is required to persist graph state. In production, this should be durable (e.g., backed by a database).
5. The graph is invoked with some initial state.
6. When the graph hits the interrupt, it returns an `Interrupt` object with the payload and metadata.
7. The graph is resumed with a `Command(resume=...)`, injecting the human's input and continuing execution.
   :::

:::js

```typescript
// highlight-next-line
import { interrupt, Command } from "@langchain/langgraph";

const graph = graphBuilder
  .addNode("humanNode", (state) => {
    // highlight-next-line
    const value = interrupt(
      // (1)!
      {
        textToRevise: state.someText, // (2)!
      }
    );
    return {
      someText: value, // (3)!
    };
  })
  .addEdge(START, "humanNode")
  .compile({ checkpointer }); // (4)!

// Run the graph until the interrupt is hit.
const config = { configurable: { thread_id: "some_id" } };
const result = await graph.invoke({ someText: "original text" }, config); // (5)!
console.log(result.__interrupt__); // (6)!
// > [
// >   {
// >     value: { textToRevise: 'original text' },
// >     resumable: true,
// >     ns: ['humanNode:6ce9e64f-edef-fe5d-f7dc-511fa9526960'],
// >     when: 'during'
// >   }
// > ]

// highlight-next-line
console.log(await graph.invoke(new Command({ resume: "Edited text" }), config)); // (7)!
// > { someText: 'Edited text' }
```

1. `interrupt(...)` pauses execution at `humanNode`, surfacing the given payload to a human.
2. Any JSON serializable value can be passed to the `interrupt` function. Here, an object containing the text to revise.
3. Once resumed, the return value of `interrupt(...)` is the human-provided input, which is used to update the state.
4. A checkpointer is required to persist graph state. In production, this should be durable (e.g., backed by a database).
5. The graph is invoked with some initial state.
6. When the graph hits the interrupt, it returns an object with `__interrupt__` containing the payload and metadata.
7. The graph is resumed with a `Command({ resume: ... })`, injecting the human's input and continuing execution.
   :::

??? example "Extended example: using `interrupt`"

    :::python
    ```python
    from typing import TypedDict
    import uuid
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.constants import START
    from langgraph.graph import StateGraph

    # highlight-next-line
    from langgraph.types import interrupt, Command


    class State(TypedDict):
        some_text: str


    def human_node(state: State):
        # highlight-next-line
        value = interrupt(  # (1)!
            {
                "text_to_revise": state["some_text"]  # (2)!
            }
        )
        return {
            "some_text": value  # (3)!
        }


    # Build the graph
    graph_builder = StateGraph(State)
    graph_builder.add_node("human_node", human_node)
    graph_builder.add_edge(START, "human_node")
    checkpointer = InMemorySaver()  # (4)!
    graph = graph_builder.compile(checkpointer=checkpointer)
    # Pass a thread ID to the graph to run it.
    config = {"configurable": {"thread_id": uuid.uuid4()}}
    # Run the graph until the interrupt is hit.
    result = graph.invoke({"some_text": "original text"}, config=config)  # (5)!

    print(result['__interrupt__']) # (6)!
    # > [
    # >    Interrupt(
    # >       value={'text_to_revise': 'original text'},
    # >       resumable=True,
    # >       ns=['human_node:6ce9e64f-edef-fe5d-f7dc-511fa9526960']
    # >    )
    # > ]
    print(result["__interrupt__"])  # (6)!
    # > [Interrupt(value={'text_to_revise': 'original text'}, id='6d7c4048049254c83195429a3659661d')]

    # highlight-next-line
    print(graph.invoke(Command(resume="Edited text"), config=config)) # (7)!
    # > {'some_text': 'Edited text'}
    ```

    1. `interrupt(...)` pauses execution at `human_node`, surfacing the given payload to a human.
    2. Any JSON serializable value can be passed to the `interrupt` function. Here, a dict containing the text to revise.
    3. Once resumed, the return value of `interrupt(...)` is the human-provided input, which is used to update the state.
    4. A checkpointer is required to persist graph state. In production, this should be durable (e.g., backed by a database).
    5. The graph is invoked with some initial state.
    6. When the graph hits the interrupt, it returns an `Interrupt` object with the payload and metadata.
    7. The graph is resumed with a `Command(resume=...)`, injecting the human's input and continuing execution.
    :::

    :::js
    ```typescript
    import { z } from "zod";
    import { v4 as uuidv4 } from "uuid";
    import { MemorySaver, StateGraph, START, interrupt, Command } from "@langchain/langgraph";

    const StateAnnotation = z.object({
      someText: z.string(),
    });

    // Build the graph
    const graphBuilder = new StateGraph(StateAnnotation)
      .addNode("humanNode", (state) => {
        // highlight-next-line
        const value = interrupt( // (1)!
          {
            textToRevise: state.someText // (2)!
          }
        );
        return {
          someText: value // (3)!
        };
      })
      .addEdge(START, "humanNode");

    const checkpointer = new MemorySaver(); // (4)!

    const graph = graphBuilder.compile({ checkpointer });

    // Pass a thread ID to the graph to run it.
    const config = { configurable: { thread_id: uuidv4() } };

    // Run the graph until the interrupt is hit.
    const result = await graph.invoke({ someText: "original text" }, config); // (5)!

    console.log(result.__interrupt__); // (6)!
    // > [
    // >   {
    // >     value: { textToRevise: 'original text' },
    // >     resumable: true,
    // >     ns: ['humanNode:6ce9e64f-edef-fe5d-f7dc-511fa9526960'],
    // >     when: 'during'
    // >   }
    // > ]

    // highlight-next-line
    console.log(await graph.invoke(new Command({ resume: "Edited text" }), config)); // (7)!
    // > { someText: 'Edited text' }
    ```

    1. `interrupt(...)` pauses execution at `humanNode`, surfacing the given payload to a human.
    2. Any JSON serializable value can be passed to the `interrupt` function. Here, an object containing the text to revise.
    3. Once resumed, the return value of `interrupt(...)` is the human-provided input, which is used to update the state.
    4. A checkpointer is required to persist graph state. In production, this should be durable (e.g., backed by a database).
    5. The graph is invoked with some initial state.
    6. When the graph hits the interrupt, it returns an object with `__interrupt__` containing the payload and metadata.
    7. The graph is resumed with a `Command({ resume: ... })`, injecting the human's input and continuing execution.
    :::

!!! tip "New in 0.4.0"

    :::python
    `__interrupt__` is a special key that will be returned when running the graph if the graph is interrupted. Support for `__interrupt__` in `invoke` and `ainvoke` has been added in version 0.4.0. If you're on an older version, you will only see `__interrupt__` in the result if you use `stream` or `astream`. You can also use `graph.get_state(thread_id)` to get the interrupt value(s).
    :::

    :::js
    `__interrupt__` is a special key that will be returned when running the graph if the graph is interrupted. Support for `__interrupt__` in `invoke` has been added in version 0.4.0. If you're on an older version, you will only see `__interrupt__` in the result if you use `stream`. You can also use `graph.getState(config)` to get the interrupt value(s).
    :::

!!! warning

    :::python
    Interrupts resemble Python's input() function in terms of developer experience, but they do not automatically resume execution from the interruption point. Instead, they rerun the entire node where the interrupt was used. For this reason, interrupts are typically best placed at the start of a node or in a dedicated node.
    :::

    :::js
    Interrupts are both powerful and ergonomic, but it's important to note that they do not automatically resume execution from the interrupt point. Instead, they rerun the entire where the interrupt was used. For this reason, interrupts are typically best placed at the state of a node or in a dedicated node.
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`get_state`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L1235) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
