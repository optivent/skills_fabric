## Orchestrator-Worker

With orchestrator-worker, an orchestrator breaks down a task and delegates each sub-task to workers. As noted in the Anthropic blog on `Building Effective Agents`:

> In the orchestrator-workers workflow, a central LLM dynamically breaks down tasks, delegates them to worker LLMs, and synthesizes their results.

> When to use this workflow: This workflow is well-suited for complex tasks where you can't predict the subtasks needed (in coding, for example, the number of files that need to be changed and the nature of the change in each file likely depend on the task). Whereas it's topographically similar, the key difference from parallelization is its flexibility—subtasks aren't pre-defined, but determined by the orchestrator based on the specific input.

![worker.png](./workflows/img/worker.png)

=== "Graph API"

    :::python
    ```python
    from typing import Annotated, List
    import operator


    # Schema for structured output to use in planning
    class Section(BaseModel):
        name: str = Field(
            description="Name for this section of the report.",
        )
        description: str = Field(
            description="Brief overview of the main topics and concepts to be covered in this section.",
        )


    class Sections(BaseModel):
        sections: List[Section] = Field(
            description="Sections of the report.",
        )


    # Augment the LLM with schema for structured output
    planner = llm.with_structured_output(Sections)
    ```

    **Creating Workers in LangGraph**

    Because orchestrator-worker workflows are common, LangGraph **has the `Send` API to support this**. It lets you dynamically create worker nodes and send each one a specific input. Each worker has its own state, and all worker outputs are written to a *shared state key* that is accessible to the orchestrator graph. This gives the orchestrator access to all worker output and allows it to synthesize them into a final output. As you can see below, we iterate over a list of sections and `Send` each to a worker node. See further documentation [here](https://langchain-ai.github.io/langgraph/how-tos/map-reduce/) and [here](https://langchain-ai.github.io/langgraph/concepts/low_level/#send).

    ```python
    from langgraph.types import Send


    # Graph state
    class State(TypedDict):
        topic: str  # Report topic
        sections: list[Section]  # List of report sections
        completed_sections: Annotated[
            list, operator.add
        ]  # All workers write to this key in parallel
        final_report: str  # Final report


    # Worker state
    class WorkerState(TypedDict):
        section: Section
        completed_sections: Annotated[list, operator.add]


    # Nodes
    def orchestrator(state: State):
        """Orchestrator that generates a plan for the report"""

        # Generate queries
        report_sections = planner.invoke(
            [
                SystemMessage(content="Generate a plan for the report."),
                HumanMessage(content=f"Here is the report topic: {state['topic']}"),
            ]
        )

        return {"sections": report_sections.sections}


    def llm_call(state: WorkerState):
        """Worker writes a section of the report"""

        # Generate section
        section = llm.invoke(
            [
                SystemMessage(
                    content="Write a report section following the provided name and description. Include no preamble for each section. Use markdown formatting."
                ),
                HumanMessage(
                    content=f"Here is the section name: {state['section'].name} and description: {state['section'].description}"
                ),
            ]
        )

        # Write the updated section to completed sections
        return {"completed_sections": [section.content]}


    def synthesizer(state: State):
        """Synthesize full report from sections"""

        # List of completed sections
        completed_sections = state["completed_sections"]

        # Format completed section to str to use as context for final sections
        completed_report_sections = "\n\n---\n\n".join(completed_sections)

        return {"final_report": completed_report_sections}


    # Conditional edge function to create llm_call workers that each write a section of the report
    def assign_workers(state: State):
        """Assign a worker to each section in the plan"""

        # Kick off section writing in parallel via Send() API
        return [Send("llm_call", {"section": s}) for s in state["sections"]]


    # Build workflow
    orchestrator_worker_builder = StateGraph(State)

    # Add the nodes
    orchestrator_worker_builder.add_node("orchestrator", orchestrator)
    orchestrator_worker_builder.add_node("llm_call", llm_call)
    orchestrator_worker_builder.add_node("synthesizer", synthesizer)

    # Add edges to connect nodes
    orchestrator_worker_builder.add_edge(START, "orchestrator")
    orchestrator_worker_builder.add_conditional_edges(
        "orchestrator", assign_workers, ["llm_call"]
    )
    orchestrator_worker_builder.add_edge("llm_call", "synthesizer")
    orchestrator_worker_builder.add_edge("synthesizer", END)

    # Compile the workflow
    orchestrator_worker = orchestrator_worker_builder.compile()

    # Show the workflow
    display(Image(orchestrator_worker.get_graph().draw_mermaid_png()))

    # Invoke
    state = orchestrator_worker.invoke({"topic": "Create a report on LLM scaling laws"})

    from IPython.display import Markdown
    Markdown(state["final_report"])
    ```

    **LangSmith Trace**

    https://smith.langchain.com/public/78cbcfc3-38bf-471d-b62a-b299b144237d/r

    **Resources:**

    **LangChain Academy**

    See our lesson on orchestrator-worker [here](https://github.com/langchain-ai/langchain-academy/blob/main/module-4/map-reduce.ipynb).

    **Examples**

    [Here](https://github.com/langchain-ai/report-mAIstro) is a project that uses orchestrator-worker for report planning and writing. See our video [here](https://www.youtube.com/watch?v=wSxZ7yFbbas).
    :::

    :::js
    ```typescript
    import "@langchain/langgraph/zod";

    // Schema for structured output to use in planning
    const Section = z.object({
      name: z.string().describe("Name for this section of the report."),
      description: z.string().describe("Brief overview of the main topics and concepts to be covered in this section."),
    });

    const Sections = z.object({
      sections: z.array(Section).describe("Sections of the report."),
    });

    // Augment the LLM with schema for structured output
    const planner = llm.withStructuredOutput(Sections);
    ```

    **Creating Workers in LangGraph**

    Because orchestrator-worker workflows are common, LangGraph **has the `Send` API to support this**. It lets you dynamically create worker nodes and send each one a specific input. Each worker has its own state, and all worker outputs are written to a *shared state key* that is accessible to the orchestrator graph. This gives the orchestrator access to all worker output and allows it to synthesize them into a final output. As you can see below, we iterate over a list of sections and `Send` each to a worker node. See further documentation [here](https://langchain-ai.github.io/langgraph/how-tos/map-reduce/) and [here](https://langchain-ai.github.io/langgraph/concepts/low_level/#send).

    ```typescript
    import { withLangGraph } from "@langchain/langgraph/zod";
    import { Send } from "@langchain/langgraph";

    // Graph state
    const State = z.object({
      topic: z.string(), // Report topic
      sections: z.array(Section).optional(), // List of report sections
      // All workers write to this key
      completed_sections: withLangGraph(z.array(z.string()), {
        reducer: {
          fn: (x, y) => x.concat(y),
        },
        default: () => [],
      }),
      final_report: z.string().optional(), // Final report
    });

    // Worker state
    const WorkerState = z.object({
      section: Section,
      completed_sections: withLangGraph(z.array(z.string()), {
        reducer: {
          fn: (x, y) => x.concat(y),
        },
        default: () => [],
      }),
    });

    // Nodes
    const orchestrator = async (state: z.infer<typeof State>) => {
      // Orchestrator that generates a plan for the report
      const reportSections = await planner.invoke([
        new SystemMessage("Generate a plan for the report."),
        new HumanMessage(`Here is the report topic: ${state.topic}`),
      ]);

      return { sections: reportSections.sections };
    };

    const llmCall = async (state: z.infer<typeof WorkerState>) => {
      // Worker writes a section of the report
      const section = await llm.invoke([
        new SystemMessage(
          "Write a report section following the provided name and description. Include no preamble for each section. Use markdown formatting."
        ),
        new HumanMessage(
          `Here is the section name: ${state.section.name} and description: ${state.section.description}`
        ),
      ]);

      // Write the updated section to completed sections
      return { completed_sections: [section.content] };
    };

    const synthesizer = (state: z.infer<typeof State>) => {
      // Synthesize full report from sections
      const completedSections = state.completed_sections;
      const completedReportSections = completedSections.join("\n\n---\n\n");
      return { final_report: completedReportSections };
    };

    // Conditional edge function to create llm_call workers
    const assignWorkers = (state: z.infer<typeof State>) => {
      // Assign a worker to each section in the plan
      return state.sections!.map((s) => new Send("llm_call", { section: s }));
    };

    // Build workflow
    const orchestratorWorkerBuilder = new StateGraph(State)
      .addNode("orchestrator", orchestrator)
      .addNode("llm_call", llmCall)
      .addNode("synthesizer", synthesizer)
      .addEdge(START, "orchestrator")
      .addConditionalEdges("orchestrator", assignWorkers, ["llm_call"])
      .addEdge("llm_call", "synthesizer")
      .addEdge("synthesizer", END);

    // Compile the workflow
    const orchestratorWorker = orchestratorWorkerBuilder.compile();

    // Invoke
    const state = await orchestratorWorker.invoke({ topic: "Create a report on LLM scaling laws" });
    console.log(state.final_report);
    ```
    :::

=== "Functional API"

    :::python
    ```python
    from typing import List


    # Schema for structured output to use in planning
    class Section(BaseModel):
        name: str = Field(
            description="Name for this section of the report.",
        )
        description: str = Field(
            description="Brief overview of the main topics and concepts to be covered in this section.",
        )


    class Sections(BaseModel):
        sections: List[Section] = Field(
            description="Sections of the report.",
        )


    # Augment the LLM with schema for structured output
    planner = llm.with_structured_output(Sections)


    @task
    def orchestrator(topic: str):
        """Orchestrator that generates a plan for the report"""
        # Generate queries
        report_sections = planner.invoke(
            [
                SystemMessage(content="Generate a plan for the report."),
                HumanMessage(content=f"Here is the report topic: {topic}"),
            ]
        )

        return report_sections.sections


    @task
    def llm_call(section: Section):
        """Worker writes a section of the report"""

        # Generate section
        result = llm.invoke(
            [
                SystemMessage(content="Write a report section."),
                HumanMessage(
                    content=f"Here is the section name: {section.name} and description: {section.description}"
                ),
            ]
        )

        # Write the updated section to completed sections
        return result.content


    @task
    def synthesizer(completed_sections: list[str]):
        """Synthesize full report from sections"""
        final_report = "\n\n---\n\n".join(completed_sections)
        return final_report


    @entrypoint()
    def orchestrator_worker(topic: str):
        sections = orchestrator(topic).result()
        section_futures = [llm_call(section) for section in sections]
        final_report = synthesizer(
            [section_fut.result() for section_fut in section_futures]
        ).result()
        return final_report

    # Invoke
    report = orchestrator_worker.invoke("Create a report on LLM scaling laws")
    from IPython.display import Markdown
    Markdown(report)
    ```

    **LangSmith Trace**

    https://smith.langchain.com/public/75a636d0-6179-4a12-9836-e0aa571e87c5/r
    :::

    :::js
    ```typescript
    // Schema for structured output to use in planning
    const Section = z.object({
      name: z.string().describe("Name for this section of the report."),
      description: z.string().describe("Brief overview of the main topics and concepts to be covered in this section."),
    });

    const Sections = z.object({
      sections: z.array(Section).describe("Sections of the report."),
    });

    // Augment the LLM with schema for structured output
    const planner = llm.withStructuredOutput(Sections);

    const orchestrator = task("orchestrator", async (topic: string) => {
      // Orchestrator that generates a plan for the report
      const reportSections = await planner.invoke([
        new SystemMessage("Generate a plan for the report."),
        new HumanMessage(`Here is the report topic: ${topic}`),
      ]);
      return reportSections.sections;
    });

    const llmCall = task("llm_call", async (section: z.infer<typeof Section>) => {
      // Worker writes a section of the report
      const result = await llm.invoke([
        new SystemMessage("Write a report section."),
        new HumanMessage(
          `Here is the section name: ${section.name} and description: ${section.description}`
        ),
      ]);
      return result.content;
    });

    const synthesizer = task("synthesizer", (completedSections: string[]) => {
      // Synthesize full report from sections
      const finalReport = completedSections.join("\n\n---\n\n");
      return finalReport;
    });

    const orchestratorWorker = entrypoint("orchestratorWorker", async (topic: string) => {
      const sections = await orchestrator(topic);
      const sectionFutures = sections.map((section) => llmCall(section));
      const finalReport = await synthesizer(
        await Promise.all(sectionFutures)
      );
      return finalReport;
    });

    // Invoke
    const report = await orchestratorWorker.invoke("Create a report on LLM scaling laws");
    console.log(report);
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`with_structured_output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/model.py#L52) (function in prebuilt)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`get_graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L704) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
