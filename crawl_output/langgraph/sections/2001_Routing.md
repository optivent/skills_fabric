## Routing

Routing classifies an input and directs it to a followup task. As noted in the Anthropic blog on `Building Effective Agents`:

> Routing classifies an input and directs it to a specialized followup task. This workflow allows for separation of concerns, and building more specialized prompts. Without this workflow, optimizing for one kind of input can hurt performance on other inputs.

> When to use this workflow: Routing works well for complex tasks where there are distinct categories that are better handled separately, and where classification can be handled accurately, either by an LLM or a more traditional classification model/algorithm.

![routing.png](./workflows/img/routing.png)

=== "Graph API"

    :::python
    ```python
    from typing_extensions import Literal
    from langchain_core.messages import HumanMessage, SystemMessage


    # Schema for structured output to use as routing logic
    class Route(BaseModel):
        step: Literal["poem", "story", "joke"] = Field(
            None, description="The next step in the routing process"
        )


    # Augment the LLM with schema for structured output
    router = llm.with_structured_output(Route)


    # State
    class State(TypedDict):
        input: str
        decision: str
        output: str


    # Nodes
    def llm_call_1(state: State):
        """Write a story"""

        result = llm.invoke(state["input"])
        return {"output": result.content}


    def llm_call_2(state: State):
        """Write a joke"""

        result = llm.invoke(state["input"])
        return {"output": result.content}


    def llm_call_3(state: State):
        """Write a poem"""

        result = llm.invoke(state["input"])
        return {"output": result.content}


    def llm_call_router(state: State):
        """Route the input to the appropriate node"""

        # Run the augmented LLM with structured output to serve as routing logic
        decision = router.invoke(
            [
                SystemMessage(
                    content="Route the input to story, joke, or poem based on the user's request."
                ),
                HumanMessage(content=state["input"]),
            ]
        )

        return {"decision": decision.step}


    # Conditional edge function to route to the appropriate node
    def route_decision(state: State):
        # Return the node name you want to visit next
        if state["decision"] == "story":
            return "llm_call_1"
        elif state["decision"] == "joke":
            return "llm_call_2"
        elif state["decision"] == "poem":
            return "llm_call_3"


    # Build workflow
    router_builder = StateGraph(State)

    # Add nodes
    router_builder.add_node("llm_call_1", llm_call_1)
    router_builder.add_node("llm_call_2", llm_call_2)
    router_builder.add_node("llm_call_3", llm_call_3)
    router_builder.add_node("llm_call_router", llm_call_router)

    # Add edges to connect nodes
    router_builder.add_edge(START, "llm_call_router")
    router_builder.add_conditional_edges(
        "llm_call_router",
        route_decision,
        {  # Name returned by route_decision : Name of next node to visit
            "llm_call_1": "llm_call_1",
            "llm_call_2": "llm_call_2",
            "llm_call_3": "llm_call_3",
        },
    )
    router_builder.add_edge("llm_call_1", END)
    router_builder.add_edge("llm_call_2", END)
    router_builder.add_edge("llm_call_3", END)

    # Compile workflow
    router_workflow = router_builder.compile()

    # Show the workflow
    display(Image(router_workflow.get_graph().draw_mermaid_png()))

    # Invoke
    state = router_workflow.invoke({"input": "Write me a joke about cats"})
    print(state["output"])
    ```

    **LangSmith Trace**

    https://smith.langchain.com/public/c4580b74-fe91-47e4-96fe-7fac598d509c/r

    **Resources:**

    **LangChain Academy**

    See our lesson on routing [here](https://github.com/langchain-ai/langchain-academy/blob/main/module-1/router.ipynb).

    **Examples**

    [Here](https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_adaptive_rag_local/) is RAG workflow that routes questions. See our video [here](https://www.youtube.com/watch?v=bq1Plo2RhYI).
    :::

    :::js
    ```typescript
    import { SystemMessage, HumanMessage } from "@langchain/core/messages";

    // Schema for structured output to use as routing logic
    const Route = z.object({
      step: z.enum(["poem", "story", "joke"]).describe("The next step in the routing process"),
    });

    // Augment the LLM with schema for structured output
    const router = llm.withStructuredOutput(Route);

    // State
    const State = z.object({
      input: z.string(),
      decision: z.string().optional(),
      output: z.string().optional(),
    });

    // Nodes
    const llmCall1 = async (state: z.infer<typeof State>) => {
      // Write a story
      const result = await llm.invoke(state.input);
      return { output: result.content };
    };

    const llmCall2 = async (state: z.infer<typeof State>) => {
      // Write a joke
      const result = await llm.invoke(state.input);
      return { output: result.content };
    };

    const llmCall3 = async (state: z.infer<typeof State>) => {
      // Write a poem
      const result = await llm.invoke(state.input);
      return { output: result.content };
    };

    const llmCallRouter = async (state: z.infer<typeof State>) => {
      // Route the input to the appropriate node
      const decision = await router.invoke([
        new SystemMessage("Route the input to story, joke, or poem based on the user's request."),
        new HumanMessage(state.input),
      ]);

      return { decision: decision.step };
    };

    // Conditional edge function to route to the appropriate node
    const routeDecision = (state: z.infer<typeof State>) => {
      // Return the node name you want to visit next
      if (state.decision === "story") {
        return "llm_call_1";
      } else if (state.decision === "joke") {
        return "llm_call_2";
      } else if (state.decision === "poem") {
        return "llm_call_3";
      }
    };

    // Build workflow
    const routerBuilder = new StateGraph(State)
      .addNode("llm_call_1", llmCall1)
      .addNode("llm_call_2", llmCall2)
      .addNode("llm_call_3", llmCall3)
      .addNode("llm_call_router", llmCallRouter)
      .addEdge(START, "llm_call_router")
      .addConditionalEdges(
        "llm_call_router",
        routeDecision,
        {
          "llm_call_1": "llm_call_1",
          "llm_call_2": "llm_call_2",
          "llm_call_3": "llm_call_3",
        }
      )
      .addEdge("llm_call_1", END)
      .addEdge("llm_call_2", END)
      .addEdge("llm_call_3", END);

    const routerWorkflow = routerBuilder.compile();

    // Invoke
    const state = await routerWorkflow.invoke({ input: "Write me a joke about cats" });
    console.log(state.output);
    ```
    :::

=== "Functional API"

    :::python
    ```python
    from typing_extensions import Literal
    from pydantic import BaseModel
    from langchain_core.messages import HumanMessage, SystemMessage


    # Schema for structured output to use as routing logic
    class Route(BaseModel):
        step: Literal["poem", "story", "joke"] = Field(
            None, description="The next step in the routing process"
        )


    # Augment the LLM with schema for structured output
    router = llm.with_structured_output(Route)


    @task
    def llm_call_1(input_: str):
        """Write a story"""
        result = llm.invoke(input_)
        return result.content


    @task
    def llm_call_2(input_: str):
        """Write a joke"""
        result = llm.invoke(input_)
        return result.content


    @task
    def llm_call_3(input_: str):
        """Write a poem"""
        result = llm.invoke(input_)
        return result.content


    def llm_call_router(input_: str):
        """Route the input to the appropriate node"""
        # Run the augmented LLM with structured output to serve as routing logic
        decision = router.invoke(
            [
                SystemMessage(
                    content="Route the input to story, joke, or poem based on the user's request."
                ),
                HumanMessage(content=input_),
            ]
        )
        return decision.step


    # Create workflow
    @entrypoint()
    def router_workflow(input_: str):
        next_step = llm_call_router(input_)
        if next_step == "story":
            llm_call = llm_call_1
        elif next_step == "joke":
            llm_call = llm_call_2
        elif next_step == "poem":
            llm_call = llm_call_3

        return llm_call(input_).result()

    # Invoke
    for step in router_workflow.stream("Write me a joke about cats", stream_mode="updates"):
        print(step)
        print("\n")
    ```

    **LangSmith Trace**

    https://smith.langchain.com/public/5e2eb979-82dd-402c-b1a0-a8cceaf2a28a/r
    :::

    :::js
    ```typescript
    import { SystemMessage, HumanMessage } from "@langchain/core/messages";

    // Schema for structured output to use as routing logic
    const Route = z.object({
      step: z.enum(["poem", "story", "joke"]).describe(
        "The next step in the routing process"
      ),
    });

    // Augment the LLM with schema for structured output
    const router = llm.withStructuredOutput(Route);

    const llmCall1 = task("llm_call_1", async (input: string) => {
      // Write a story
      const result = await llm.invoke(input);
      return result.content;
    });

    const llmCall2 = task("llm_call_2", async (input: string) => {
      // Write a joke
      const result = await llm.invoke(input);
      return result.content;
    });

    const llmCall3 = task("llm_call_3", async (input: string) => {
      // Write a poem
      const result = await llm.invoke(input);
      return result.content;
    });

    const llmCallRouter = async (input: string) => {
      // Route the input to the appropriate node
      const decision = await router.invoke([
        new SystemMessage("Route the input to story, joke, or poem based on the user's request."),
        new HumanMessage(input),
      ]);
      return decision.step;
    };

    // Create workflow
    const routerWorkflow = entrypoint("routerWorkflow", async (input: string) => {
      const nextStep = await llmCallRouter(input);

      let llmCall: typeof llmCall1;
      if (nextStep === "story") {
        llmCall = llmCall1;
      } else if (nextStep === "joke") {
        llmCall = llmCall2;
      } else if (nextStep === "poem") {
        llmCall = llmCall3;
      }

      return await llmCall(input);
    });

    // Invoke
    const stream = await routerWorkflow.stream("Write me a joke about cats", { streamMode: "updates" });
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
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`with_structured_output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/model.py#L52) (function in prebuilt)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
