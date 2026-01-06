## define top-level supervisor

builder = StateGraph(MessagesState)
def top_level_supervisor(state: MessagesState) -> Command[Literal["team_1_graph", "team_2_graph", END]]:
    # you can pass relevant parts of the state to the LLM (e.g., state["messages"])
    # to determine which team to call next. a common pattern is to call the model
    # with a structured output (e.g. force it to return an output with a "next_team" field)
    response = model.invoke(...)
    # route to one of the teams or exit based on the supervisor's decision
    # if the supervisor returns "__end__", the graph will finish execution
    return Command(goto=response["next_team"])

builder = StateGraph(MessagesState)
builder.add_node(top_level_supervisor)
builder.add_node("team_1_graph", team_1_graph)
builder.add_node("team_2_graph", team_2_graph)
builder.add_edge(START, "top_level_supervisor")
builder.add_edge("team_1_graph", "top_level_supervisor")
builder.add_edge("team_2_graph", "top_level_supervisor")
graph = builder.compile()
```

:::

:::js

```typescript
import { StateGraph, MessagesZodState, Command, START, END } from "@langchain/langgraph";
import { ChatOpenAI } from "@langchain/openai";
import { z } from "zod";

const model = new ChatOpenAI();

// define team 1 (same as the single supervisor example above)

const team1Supervisor = async (state: z.infer<typeof MessagesZodState>) => {
  const response = await model.invoke(...);
  return new Command({ goto: response.nextAgent });
};

const team1Agent1 = async (state: z.infer<typeof MessagesZodState>) => {
  const response = await model.invoke(...);
  return new Command({
    goto: "team1Supervisor",
    update: { messages: [response] }
  });
};

const team1Agent2 = async (state: z.infer<typeof MessagesZodState>) => {
  const response = await model.invoke(...);
  return new Command({
    goto: "team1Supervisor",
    update: { messages: [response] }
  });
};

const team1Builder = new StateGraph(MessagesZodState)
  .addNode("team1Supervisor", team1Supervisor, {
    ends: ["team1Agent1", "team1Agent2", END]
  })
  .addNode("team1Agent1", team1Agent1, {
    ends: ["team1Supervisor"]
  })
  .addNode("team1Agent2", team1Agent2, {
    ends: ["team1Supervisor"]
  })
  .addEdge(START, "team1Supervisor");
const team1Graph = team1Builder.compile();

// define team 2 (same as the single supervisor example above)
const team2Supervisor = async (state: z.infer<typeof MessagesZodState>) => {
  // ...
};

const team2Agent1 = async (state: z.infer<typeof MessagesZodState>) => {
  // ...
};

const team2Agent2 = async (state: z.infer<typeof MessagesZodState>) => {
  // ...
};

const team2Builder = new StateGraph(MessagesZodState);
// ... build team2Graph
const team2Graph = team2Builder.compile();

// define top-level supervisor

const topLevelSupervisor = async (state: z.infer<typeof MessagesZodState>) => {
  // you can pass relevant parts of the state to the LLM (e.g., state.messages)
  // to determine which team to call next. a common pattern is to call the model
  // with a structured output (e.g. force it to return an output with a "next_team" field)
  const response = await model.invoke(...);
  // route to one of the teams or exit based on the supervisor's decision
  // if the supervisor returns "__end__", the graph will finish execution
  return new Command({ goto: response.nextTeam });
};

const builder = new StateGraph(MessagesZodState)
  .addNode("topLevelSupervisor", topLevelSupervisor, {
    ends: ["team1Graph", "team2Graph", END]
  })
  .addNode("team1Graph", team1Graph)
  .addNode("team2Graph", team2Graph)
  .addEdge(START, "topLevelSupervisor")
  .addEdge("team1Graph", "topLevelSupervisor")
  .addEdge("team2Graph", "topLevelSupervisor");

const graph = builder.compile();
```

:::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Command`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L364) (class in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`sync`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L556) (function in checkpoint)
