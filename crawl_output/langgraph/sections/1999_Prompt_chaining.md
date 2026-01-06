## Prompt chaining

In prompt chaining, each LLM call processes the output of the previous one.

As noted in the Anthropic blog on `Building Effective Agents`:

> Prompt chaining decomposes a task into a sequence of steps, where each LLM call processes the output of the previous one. You can add programmatic checks (see "gate" in the diagram below) on any intermediate steps to ensure that the process is still on track.

> When to use this workflow: This workflow is ideal for situations where the task can be easily and cleanly decomposed into fixed subtasks. The main goal is to trade off latency for higher accuracy, by making each LLM call an easier task.

![prompt_chain.png](./workflows/img/prompt_chain.png)

=== "Graph API"

    :::python
    ```python
    from typing_extensions import TypedDict
    from langgraph.graph import StateGraph, START, END
    from IPython.display import Image, display


    # Graph state
    class State(TypedDict):
        topic: str
        joke: str
        improved_joke: str
        final_joke: str


    # Nodes
    def generate_joke(state: State):
        """First LLM call to generate initial joke"""

        msg = llm.invoke(f"Write a short joke about {state['topic']}")
        return {"joke": msg.content}


    def check_punchline(state: State):
        """Gate function to check if the joke has a punchline"""

        # Simple check - does the joke contain "?" or "!"
        if "?" in state["joke"] or "!" in state["joke"]:
            return "Pass"
        return "Fail"


    def improve_joke(state: State):
        """Second LLM call to improve the joke"""

        msg = llm.invoke(f"Make this joke funnier by adding wordplay: {state['joke']}")
        return {"improved_joke": msg.content}


    def polish_joke(state: State):
        """Third LLM call for final polish"""

        msg = llm.invoke(f"Add a surprising twist to this joke: {state['improved_joke']}")
        return {"final_joke": msg.content}


    # Build workflow
    workflow = StateGraph(State)

    # Add nodes
    workflow.add_node("generate_joke", generate_joke)
    workflow.add_node("improve_joke", improve_joke)
    workflow.add_node("polish_joke", polish_joke)

    # Add edges to connect nodes
    workflow.add_edge(START, "generate_joke")
    workflow.add_conditional_edges(
        "generate_joke", check_punchline, {"Fail": "improve_joke", "Pass": END}
    )
    workflow.add_edge("improve_joke", "polish_joke")
    workflow.add_edge("polish_joke", END)

    # Compile
    chain = workflow.compile()

    # Show workflow
    display(Image(chain.get_graph().draw_mermaid_png()))

    # Invoke
    state = chain.invoke({"topic": "cats"})
    print("Initial joke:")
    print(state["joke"])
    print("\n--- --- ---\n")
    if "improved_joke" in state:
        print("Improved joke:")
        print(state["improved_joke"])
        print("\n--- --- ---\n")

        print("Final joke:")
        print(state["final_joke"])
    else:
        print("Joke failed quality gate - no punchline detected!")
    ```

    **LangSmith Trace**

    https://smith.langchain.com/public/a0281fca-3a71-46de-beee-791468607b75/r

    **Resources:**

    **LangChain Academy**

    See our lesson on Prompt Chaining [here](https://github.com/langchain-ai/langchain-academy/blob/main/module-1/chain.ipynb).
    :::

    :::js
    ```typescript
    import { StateGraph, START, END } from "@langchain/langgraph";
    import { z } from "zod";

    // Graph state
    const State = z.object({
      topic: z.string(),
      joke: z.string().optional(),
      improved_joke: z.string().optional(),
      final_joke: z.string().optional(),
    });

    // Nodes
    const generateJoke = async (state: z.infer<typeof State>) => {
      // First LLM call to generate initial joke
      const msg = await llm.invoke(`Write a short joke about ${state.topic}`);
      return { joke: msg.content };
    };

    const checkPunchline = (state: z.infer<typeof State>) => {
      // Gate function to check if the joke has a punchline
      // Simple check - does the joke contain "?" or "!"
      if (state.joke && (state.joke.includes("?") || state.joke.includes("!"))) {
        return "Pass";
      }
      return "Fail";
    };

    const improveJoke = async (state: z.infer<typeof State>) => {
      // Second LLM call to improve the joke
      const msg = await llm.invoke(`Make this joke funnier by adding wordplay: ${state.joke}`);
      return { improved_joke: msg.content };
    };

    const polishJoke = async (state: z.infer<typeof State>) => {
      // Third LLM call for final polish
      const msg = await llm.invoke(`Add a surprising twist to this joke: ${state.improved_joke}`);
      return { final_joke: msg.content };
    };

    // Build workflow
    const workflow = new StateGraph(State)
      .addNode("generate_joke", generateJoke)
      .addNode("improve_joke", improveJoke)
      .addNode("polish_joke", polishJoke)
      .addEdge(START, "generate_joke")
      .addConditionalEdges(
        "generate_joke",
        checkPunchline,
        { "Fail": "improve_joke", "Pass": END }
      )
      .addEdge("improve_joke", "polish_joke")
      .addEdge("polish_joke", END);

    // Compile
    const chain = workflow.compile();

    // Show workflow
    import * as fs from "node:fs/promises";
    const drawableGraph = await chain.getGraphAsync();
    const image = await drawableGraph.drawMermaidPng();
    const imageBuffer = new Uint8Array(await image.arrayBuffer());
    await fs.writeFile("workflow.png", imageBuffer);

    // Invoke
    const state = await chain.invoke({ topic: "cats" });
    console.log("Initial joke:");
    console.log(state.joke);
    console.log("\n--- --- ---\n");
    if (state.improved_joke) {
      console.log("Improved joke:");
      console.log(state.improved_joke);
      console.log("\n--- --- ---\n");

      console.log("Final joke:");
      console.log(state.final_joke);
    } else {
      console.log("Joke failed quality gate - no punchline detected!");
    }
    ```
    :::

=== "Functional API"

    :::python
    ```python
    from langgraph.func import entrypoint, task


    # Tasks
    @task
    def generate_joke(topic: str):
        """First LLM call to generate initial joke"""
        msg = llm.invoke(f"Write a short joke about {topic}")
        return msg.content


    def check_punchline(joke: str):
        """Gate function to check if the joke has a punchline"""
        # Simple check - does the joke contain "?" or "!"
        if "?" in joke or "!" in joke:
            return "Fail"

        return "Pass"


    @task
    def improve_joke(joke: str):
        """Second LLM call to improve the joke"""
        msg = llm.invoke(f"Make this joke funnier by adding wordplay: {joke}")
        return msg.content


    @task
    def polish_joke(joke: str):
        """Third LLM call for final polish"""
        msg = llm.invoke(f"Add a surprising twist to this joke: {joke}")
        return msg.content


    @entrypoint()
    def prompt_chaining_workflow(topic: str):
        original_joke = generate_joke(topic).result()
        if check_punchline(original_joke) == "Pass":
            return original_joke

        improved_joke = improve_joke(original_joke).result()
        return polish_joke(improved_joke).result()

    # Invoke
    for step in prompt_chaining_workflow.stream("cats", stream_mode="updates"):
        print(step)
        print("\n")
    ```

    **LangSmith Trace**

    https://smith.langchain.com/public/332fa4fc-b6ca-416e-baa3-161625e69163/r
    :::

    :::js
    ```typescript
    import { entrypoint, task } from "@langchain/langgraph";

    // Tasks
    const generateJoke = task("generate_joke", async (topic: string) => {
      // First LLM call to generate initial joke
      const msg = await llm.invoke(`Write a short joke about ${topic}`);
      return msg.content;
    });

    const checkPunchline = (joke: string) => {
      // Gate function to check if the joke has a punchline
      // Simple check - does the joke contain "?" or "!"
      if (joke.includes("?") || joke.includes("!")) {
        return "Pass";
      }
      return "Fail";
    };

    const improveJoke = task("improve_joke", async (joke: string) => {
      // Second LLM call to improve the joke
      const msg = await llm.invoke(`Make this joke funnier by adding wordplay: ${joke}`);
      return msg.content;
    });

    const polishJoke = task("polish_joke", async (joke: string) => {
      // Third LLM call for final polish
      const msg = await llm.invoke(`Add a surprising twist to this joke: ${joke}`);
      return msg.content;
    });

    const promptChainingWorkflow = entrypoint("promptChainingWorkflow", async (topic: string) => {
      const originalJoke = await generateJoke(topic);
      if (checkPunchline(originalJoke) === "Pass") {
        return originalJoke;
      }

      const improvedJoke = await improveJoke(originalJoke);
      return await polishJoke(improvedJoke);
    });

    // Invoke
    const stream = await promptChainingWorkflow.stream("cats", { streamMode: "updates" });
    for await (const step of stream) {
      console.log(step);
      console.log("\n");
    }
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`prompt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L566) (function in prebuilt)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`get_graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L704) (function in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
