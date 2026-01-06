## Parallelization

With parallelization, LLMs work simultaneously on a task:

> LLMs can sometimes work simultaneously on a task and have their outputs aggregated programmatically. This workflow, parallelization, manifests in two key variations: Sectioning: Breaking a task into independent subtasks run in parallel. Voting: Running the same task multiple times to get diverse outputs.

> When to use this workflow: Parallelization is effective when the divided subtasks can be parallelized for speed, or when multiple perspectives or attempts are needed for higher confidence results. For complex tasks with multiple considerations, LLMs generally perform better when each consideration is handled by a separate LLM call, allowing focused attention on each specific aspect.

![parallelization.png](./workflows/img/parallelization.png)

=== "Graph API"

    :::python
    ```python
    # Graph state
    class State(TypedDict):
        topic: str
        joke: str
        story: str
        poem: str
        combined_output: str


    # Nodes
    def call_llm_1(state: State):
        """First LLM call to generate initial joke"""

        msg = llm.invoke(f"Write a joke about {state['topic']}")
        return {"joke": msg.content}


    def call_llm_2(state: State):
        """Second LLM call to generate story"""

        msg = llm.invoke(f"Write a story about {state['topic']}")
        return {"story": msg.content}


    def call_llm_3(state: State):
        """Third LLM call to generate poem"""

        msg = llm.invoke(f"Write a poem about {state['topic']}")
        return {"poem": msg.content}


    def aggregator(state: State):
        """Combine the joke and story into a single output"""

        combined = f"Here's a story, joke, and poem about {state['topic']}!\n\n"
        combined += f"STORY:\n{state['story']}\n\n"
        combined += f"JOKE:\n{state['joke']}\n\n"
        combined += f"POEM:\n{state['poem']}"
        return {"combined_output": combined}


    # Build workflow
    parallel_builder = StateGraph(State)

    # Add nodes
    parallel_builder.add_node("call_llm_1", call_llm_1)
    parallel_builder.add_node("call_llm_2", call_llm_2)
    parallel_builder.add_node("call_llm_3", call_llm_3)
    parallel_builder.add_node("aggregator", aggregator)

    # Add edges to connect nodes
    parallel_builder.add_edge(START, "call_llm_1")
    parallel_builder.add_edge(START, "call_llm_2")
    parallel_builder.add_edge(START, "call_llm_3")
    parallel_builder.add_edge("call_llm_1", "aggregator")
    parallel_builder.add_edge("call_llm_2", "aggregator")
    parallel_builder.add_edge("call_llm_3", "aggregator")
    parallel_builder.add_edge("aggregator", END)
    parallel_workflow = parallel_builder.compile()

    # Show workflow
    display(Image(parallel_workflow.get_graph().draw_mermaid_png()))

    # Invoke
    state = parallel_workflow.invoke({"topic": "cats"})
    print(state["combined_output"])
    ```

    **LangSmith Trace**

    https://smith.langchain.com/public/3be2e53c-ca94-40dd-934f-82ff87fac277/r

    **Resources:**

    **Documentation**

    See our documentation on parallelization [here](https://langchain-ai.github.io/langgraph/how-tos/branching/).

    **LangChain Academy**

    See our lesson on parallelization [here](https://github.com/langchain-ai/langchain-academy/blob/main/module-1/simple-graph.ipynb).
    :::

    :::js
    ```typescript
    // Graph state
    const State = z.object({
      topic: z.string(),
      joke: z.string().optional(),
      story: z.string().optional(),
      poem: z.string().optional(),
      combined_output: z.string().optional(),
    });

    // Nodes
    const callLlm1 = async (state: z.infer<typeof State>) => {
      // First LLM call to generate initial joke
      const msg = await llm.invoke(`Write a joke about ${state.topic}`);
      return { joke: msg.content };
    };

    const callLlm2 = async (state: z.infer<typeof State>) => {
      // Second LLM call to generate story
      const msg = await llm.invoke(`Write a story about ${state.topic}`);
      return { story: msg.content };
    };

    const callLlm3 = async (state: z.infer<typeof State>) => {
      // Third LLM call to generate poem
      const msg = await llm.invoke(`Write a poem about ${state.topic}`);
      return { poem: msg.content };
    };

    const aggregator = (state: z.infer<typeof State>) => {
      // Combine the joke and story into a single output
      let combined = `Here's a story, joke, and poem about ${state.topic}!\n\n`;
      combined += `STORY:\n${state.story}\n\n`;
      combined += `JOKE:\n${state.joke}\n\n`;
      combined += `POEM:\n${state.poem}`;
      return { combined_output: combined };
    };

    // Build workflow
    const parallelBuilder = new StateGraph(State)
      .addNode("call_llm_1", callLlm1)
      .addNode("call_llm_2", callLlm2)
      .addNode("call_llm_3", callLlm3)
      .addNode("aggregator", aggregator)
      .addEdge(START, "call_llm_1")
      .addEdge(START, "call_llm_2")
      .addEdge(START, "call_llm_3")
      .addEdge("call_llm_1", "aggregator")
      .addEdge("call_llm_2", "aggregator")
      .addEdge("call_llm_3", "aggregator")
      .addEdge("aggregator", END);

    const parallelWorkflow = parallelBuilder.compile();

    // Invoke
    const state = await parallelWorkflow.invoke({ topic: "cats" });
    console.log(state.combined_output);
    ```
    :::

=== "Functional API"

    :::python
    ```python
    @task
    def call_llm_1(topic: str):
        """First LLM call to generate initial joke"""
        msg = llm.invoke(f"Write a joke about {topic}")
        return msg.content


    @task
    def call_llm_2(topic: str):
        """Second LLM call to generate story"""
        msg = llm.invoke(f"Write a story about {topic}")
        return msg.content


    @task
    def call_llm_3(topic):
        """Third LLM call to generate poem"""
        msg = llm.invoke(f"Write a poem about {topic}")
        return msg.content


    @task
    def aggregator(topic, joke, story, poem):
        """Combine the joke and story into a single output"""

        combined = f"Here's a story, joke, and poem about {topic}!\n\n"
        combined += f"STORY:\n{story}\n\n"
        combined += f"JOKE:\n{joke}\n\n"
        combined += f"POEM:\n{poem}"
        return combined


    # Build workflow
    @entrypoint()
    def parallel_workflow(topic: str):
        joke_fut = call_llm_1(topic)
        story_fut = call_llm_2(topic)
        poem_fut = call_llm_3(topic)
        return aggregator(
            topic, joke_fut.result(), story_fut.result(), poem_fut.result()
        ).result()

    # Invoke
    for step in parallel_workflow.stream("cats", stream_mode="updates"):
        print(step)
        print("\n")
    ```

    **LangSmith Trace**

    https://smith.langchain.com/public/623d033f-e814-41e9-80b1-75e6abb67801/r
    :::

    :::js
    ```typescript
    const callLlm1 = task("call_llm_1", async (topic: string) => {
      // First LLM call to generate initial joke
      const msg = await llm.invoke(`Write a joke about ${topic}`);
      return msg.content;
    });

    const callLlm2 = task("call_llm_2", async (topic: string) => {
      // Second LLM call to generate story
      const msg = await llm.invoke(`Write a story about ${topic}`);
      return msg.content;
    });

    const callLlm3 = task("call_llm_3", async (topic: string) => {
      // Third LLM call to generate poem
      const msg = await llm.invoke(`Write a poem about ${topic}`);
      return msg.content;
    });

    const aggregator = task("aggregator", (topic: string, joke: string, story: string, poem: string) => {
      // Combine the joke and story into a single output
      let combined = `Here's a story, joke, and poem about ${topic}!\n\n`;
      combined += `STORY:\n${story}\n\n`;
      combined += `JOKE:\n${joke}\n\n`;
      combined += `POEM:\n${poem}`;
      return combined;
    });

    // Build workflow
    const parallelWorkflow = entrypoint("parallelWorkflow", async (topic: string) => {
      const jokeFut = callLlm1(topic);
      const storyFut = callLlm2(topic);
      const poemFut = callLlm3(topic);

      return await aggregator(
        topic,
        await jokeFut,
        await storyFut,
        await poemFut
      );
    });

    // Invoke
    const stream = await parallelWorkflow.stream("cats", { streamMode: "updates" });
    for await (const step of stream) {
      console.log(step);
      console.log("\n");
    }
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`get_graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L704) (function in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
