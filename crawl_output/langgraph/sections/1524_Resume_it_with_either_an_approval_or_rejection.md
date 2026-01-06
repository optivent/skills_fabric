## Resume it with either an approval or rejection.

thread_config = {"configurable": {"thread_id": "some_id"}}
graph.invoke(Command(resume=True), config=thread_config)
```

:::

:::js

```typescript
import { interrupt, Command } from "@langchain/langgraph";

// Add the node to the graph in an appropriate location
// and connect it to the relevant nodes.
graphBuilder.addNode("humanApproval", (state) => {
  const isApproved = interrupt({
    question: "Is this correct?",
    // Surface the output that should be
    // reviewed and approved by the human.
    llmOutput: state.llmOutput,
  });

  if (isApproved) {
    return new Command({ goto: "someNode" });
  } else {
    return new Command({ goto: "anotherNode" });
  }
});
const graph = graphBuilder.compile({ checkpointer });

// After running the graph and hitting the interrupt, the graph will pause.
// Resume it with either an approval or rejection.
const threadConfig = { configurable: { thread_id: "some_id" } };
await graph.invoke(new Command({ resume: true }), threadConfig);
```

:::

??? example "Extended example: approve or reject with interrupt"

    :::python
    ```python
    from typing import Literal, TypedDict
    import uuid

    from langgraph.constants import START, END
    from langgraph.graph import StateGraph
    from langgraph.types import interrupt, Command
    from langgraph.checkpoint.memory import InMemorySaver

    # Define the shared graph state
    class State(TypedDict):
        llm_output: str
        decision: str

    # Simulate an LLM output node
    def generate_llm_output(state: State) -> State:
        return {"llm_output": "This is the generated output."}

    # Human approval node
    def human_approval(state: State) -> Command[Literal["approved_path", "rejected_path"]]:
        decision = interrupt({
            "question": "Do you approve the following output?",
            "llm_output": state["llm_output"]
        })

        if decision == "approve":
            return Command(goto="approved_path", update={"decision": "approved"})
        else:
            return Command(goto="rejected_path", update={"decision": "rejected"})

    # Next steps after approval
    def approved_node(state: State) -> State:
        print("✅ Approved path taken.")
        return state

    # Alternative path after rejection
    def rejected_node(state: State) -> State:
        print("❌ Rejected path taken.")
        return state

    # Build the graph
    builder = StateGraph(State)
    builder.add_node("generate_llm_output", generate_llm_output)
    builder.add_node("human_approval", human_approval)
    builder.add_node("approved_path", approved_node)
    builder.add_node("rejected_path", rejected_node)

    builder.set_entry_point("generate_llm_output")
    builder.add_edge("generate_llm_output", "human_approval")
    builder.add_edge("approved_path", END)
    builder.add_edge("rejected_path", END)

    checkpointer = InMemorySaver()
    graph = builder.compile(checkpointer=checkpointer)

    # Run until interrupt
    config = {"configurable": {"thread_id": uuid.uuid4()}}
    result = graph.invoke({}, config=config)
    print(result["__interrupt__"])
    # Output:
    # Interrupt(value={'question': 'Do you approve the following output?', 'llm_output': 'This is the generated output.'}, ...)

    # Simulate resuming with human input
    # To test rejection, replace resume="approve" with resume="reject"
    final_result = graph.invoke(Command(resume="approve"), config=config)
    print(final_result)
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

    // Define the shared graph state
    const StateAnnotation = z.object({
      llmOutput: z.string(),
      decision: z.string(),
    });

    // Simulate an LLM output node
    function generateLlmOutput(state: z.infer<typeof StateAnnotation>) {
      return { llmOutput: "This is the generated output." };
    }

    // Human approval node
    function humanApproval(state: z.infer<typeof StateAnnotation>): Command {
      const decision = interrupt({
        question: "Do you approve the following output?",
        llmOutput: state.llmOutput
      });

      if (decision === "approve") {
        return new Command({
          goto: "approvedPath",
          update: { decision: "approved" }
        });
      } else {
        return new Command({
          goto: "rejectedPath",
          update: { decision: "rejected" }
        });
      }
    }

    // Next steps after approval
    function approvedNode(state: z.infer<typeof StateAnnotation>) {
      console.log("✅ Approved path taken.");
      return state;
    }

    // Alternative path after rejection
    function rejectedNode(state: z.infer<typeof StateAnnotation>) {
      console.log("❌ Rejected path taken.");
      return state;
    }

    // Build the graph
    const builder = new StateGraph(StateAnnotation)
      .addNode("generateLlmOutput", generateLlmOutput)
      .addNode("humanApproval", humanApproval, {
        ends: ["approvedPath", "rejectedPath"]
      })
      .addNode("approvedPath", approvedNode)
      .addNode("rejectedPath", rejectedNode)
      .addEdge(START, "generateLlmOutput")
      .addEdge("generateLlmOutput", "humanApproval")
      .addEdge("approvedPath", END)
      .addEdge("rejectedPath", END);

    const checkpointer = new MemorySaver();
    const graph = builder.compile({ checkpointer });

    // Run until interrupt
    const config = { configurable: { thread_id: uuidv4() } };
    const result = await graph.invoke({}, config);
    console.log(result.__interrupt__);
    // Output:
    // [{
    //   value: {
    //     question: 'Do you approve the following output?',
    //     llmOutput: 'This is the generated output.'
    //   },
    //   ...
    // }]

    // Simulate resuming with human input
    // To test rejection, replace resume: "approve" with resume: "reject"
    const finalResult = await graph.invoke(
      new Command({ resume: "approve" }),
      config
    );
    console.log(finalResult);
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`Interrupt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L157) (class in langgraph)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
