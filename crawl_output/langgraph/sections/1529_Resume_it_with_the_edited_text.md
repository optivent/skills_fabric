## Resume it with the edited text.

thread_config = {"configurable": {"thread_id": "some_id"}}
graph.invoke(
    Command(resume={"edited_text": "The edited text"}),
    config=thread_config
)
```

:::

:::js

```typescript
import { interrupt } from "@langchain/langgraph";

function humanEditing(state: z.infer<typeof StateAnnotation>) {
  const result = interrupt({
    // Interrupt information to surface to the client.
    // Can be any JSON serializable value.
    task: "Review the output from the LLM and make any necessary edits.",
    llmGeneratedSummary: state.llmGeneratedSummary,
  });

  // Update the state with the edited text
  return {
    llmGeneratedSummary: result.editedText,
  };
}

// Add the node to the graph in an appropriate location
// and connect it to the relevant nodes.
graphBuilder.addNode("humanEditing", humanEditing);
const graph = graphBuilder.compile({ checkpointer });

// After running the graph and hitting the interrupt, the graph will pause.
// Resume it with the edited text.
const threadConfig = { configurable: { thread_id: "some_id" } };
await graph.invoke(
  new Command({ resume: { editedText: "The edited text" } }),
  threadConfig
);
```

:::

??? example "Extended example: edit state with interrupt"

    :::python
    ```python
    from typing import TypedDict
    import uuid

    from langgraph.constants import START, END
    from langgraph.graph import StateGraph
    from langgraph.types import interrupt, Command
    from langgraph.checkpoint.memory import InMemorySaver

    # Define the graph state
    class State(TypedDict):
        summary: str

    # Simulate an LLM summary generation
    def generate_summary(state: State) -> State:
        return {
            "summary": "The cat sat on the mat and looked at the stars."
        }

    # Human editing node
    def human_review_edit(state: State) -> State:
        result = interrupt({
            "task": "Please review and edit the generated summary if necessary.",
            "generated_summary": state["summary"]
        })
        return {
            "summary": result["edited_summary"]
        }

    # Simulate downstream use of the edited summary
    def downstream_use(state: State) -> State:
        print(f"✅ Using edited summary: {state['summary']}")
        return state

    # Build the graph
    builder = StateGraph(State)
    builder.add_node("generate_summary", generate_summary)
    builder.add_node("human_review_edit", human_review_edit)
    builder.add_node("downstream_use", downstream_use)

    builder.set_entry_point("generate_summary")
    builder.add_edge("generate_summary", "human_review_edit")
    builder.add_edge("human_review_edit", "downstream_use")
    builder.add_edge("downstream_use", END)

    # Set up in-memory checkpointing for interrupt support
    checkpointer = InMemorySaver()
    graph = builder.compile(checkpointer=checkpointer)

    # Invoke the graph until it hits the interrupt
    config = {"configurable": {"thread_id": uuid.uuid4()}}
    result = graph.invoke({}, config=config)

    # Output interrupt payload
    print(result["__interrupt__"])
    # Example output:
    # > [
    # >     Interrupt(
    # >         value={
    # >             'task': 'Please review and edit the generated summary if necessary.',
    # >             'generated_summary': 'The cat sat on the mat and looked at the stars.'
    # >         },
    # >         id='...'
    # >     )
    # > ]

    # Resume the graph with human-edited input
    edited_summary = "The cat lay on the rug, gazing peacefully at the night sky."
    resumed_result = graph.invoke(
        Command(resume={"edited_summary": edited_summary}),
        config=config
    )
    print(resumed_result)
    ```
    :::

    :::js
    ```typescript
    import { z } from "zod";
    import { v4 as uuidv4 } from "uuid";
    import {
      StateGraph,
      START,
      END,
      interrupt,
      Command,
      MemorySaver
    } from "@langchain/langgraph";

    // Define the graph state
    const StateAnnotation = z.object({
      summary: z.string(),
    });

    // Simulate an LLM summary generation
    function generateSummary(state: z.infer<typeof StateAnnotation>) {
      return {
        summary: "The cat sat on the mat and looked at the stars."
      };
    }

    // Human editing node
    function humanReviewEdit(state: z.infer<typeof StateAnnotation>) {
      const result = interrupt({
        task: "Please review and edit the generated summary if necessary.",
        generatedSummary: state.summary
      });
      return {
        summary: result.editedSummary
      };
    }

    // Simulate downstream use of the edited summary
    function downstreamUse(state: z.infer<typeof StateAnnotation>) {
      console.log(`✅ Using edited summary: ${state.summary}`);
      return state;
    }

    // Build the graph
    const builder = new StateGraph(StateAnnotation)
      .addNode("generateSummary", generateSummary)
      .addNode("humanReviewEdit", humanReviewEdit)
      .addNode("downstreamUse", downstreamUse)
      .addEdge(START, "generateSummary")
      .addEdge("generateSummary", "humanReviewEdit")
      .addEdge("humanReviewEdit", "downstreamUse")
      .addEdge("downstreamUse", END);

    // Set up in-memory checkpointing for interrupt support
    const checkpointer = new MemorySaver();
    const graph = builder.compile({ checkpointer });

    // Invoke the graph until it hits the interrupt
    const config = { configurable: { thread_id: uuidv4() } };
    const result = await graph.invoke({}, config);

    // Output interrupt payload
    console.log(result.__interrupt__);
    // Example output:
    // [{
    //   value: {
    //     task: 'Please review and edit the generated summary if necessary.',
    //     generatedSummary: 'The cat sat on the mat and looked at the stars.'
    //   },
    //   resumable: true,
    //   ...
    // }]

    // Resume the graph with human-edited input
    const editedSummary = "The cat lay on the rug, gazing peacefully at the night sky.";
    const resumedResult = await graph.invoke(
      new Command({ resume: { editedSummary } }),
      config
    );
    console.log(resumedResult);
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`Interrupt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L157) (class in langgraph)
