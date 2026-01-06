## highlight-next-line

print(graph.invoke({}, context={"my_runtime_value": "b"}))
```

```
{'my_state_value': 1}
{'my_state_value': 2}
```
:::

:::js
```typescript
import { StateGraph, END, START } from "@langchain/langgraph";
import { RunnableConfig } from "@langchain/core/runnables";
import { z } from "zod";

// 1. Specify config schema
const ConfigurableSchema = z.object({
  myRuntimeValue: z.string(),
});

// 2. Define a graph that accesses the config in a node
const State = z.object({
  myStateValue: z.number(),
});

const graph = new StateGraph(State)
  .addNode("node", (state, config) => {
    // highlight-next-line
    if (config?.configurable?.myRuntimeValue === "a") {
      return { myStateValue: 1 };
      // highlight-next-line
    } else if (config?.configurable?.myRuntimeValue === "b") {
      return { myStateValue: 2 };
    } else {
      throw new Error("Unknown values.");
    }
  })
  .addEdge(START, "node")
  .addEdge("node", END)
  .compile();

// 3. Pass in configuration at runtime:
// highlight-next-line
console.log(await graph.invoke({}, { configurable: { myRuntimeValue: "a" } }));
// highlight-next-line
console.log(await graph.invoke({}, { configurable: { myRuntimeValue: "b" } }));
```

```
{ myStateValue: 1 }
{ myStateValue: 2 }
```
:::

??? example "Extended example: specifying LLM at runtime"

    :::python
    Below we demonstrate a practical example in which we configure what LLM to use at runtime. We will use both OpenAI and Anthropic models.

    ```python
    from dataclasses import dataclass

    from langchain.chat_models import init_chat_model
    from langgraph.graph import MessagesState, END, StateGraph, START
    from langgraph.runtime import Runtime
    from typing_extensions import TypedDict

    @dataclass
    class ContextSchema:
        model_provider: str = "anthropic"

    MODELS = {
        "anthropic": init_chat_model("anthropic:claude-3-5-haiku-latest"),
        "openai": init_chat_model("openai:gpt-4.1-mini"),
    }

    def call_model(state: MessagesState, runtime: Runtime[ContextSchema]):
        model = MODELS[runtime.context.model_provider]
        response = model.invoke(state["messages"])
        return {"messages": [response]}

    builder = StateGraph(MessagesState, context_schema=ContextSchema)
    builder.add_node("model", call_model)
    builder.add_edge(START, "model")
    builder.add_edge("model", END)

    graph = builder.compile()

    # Usage
    input_message = {"role": "user", "content": "hi"}
    # With no configuration, uses default (Anthropic)
    response_1 = graph.invoke({"messages": [input_message]}, context=ContextSchema())["messages"][-1]
    # Or, can set OpenAI
    response_2 = graph.invoke({"messages": [input_message]}, context={"model_provider": "openai"})["messages"][-1]

    print(response_1.response_metadata["model_name"])
    print(response_2.response_metadata["model_name"])
    ```
    ```
    claude-3-5-haiku-20241022
    gpt-4.1-mini-2025-04-14
    ```
    :::

    :::js
    Below we demonstrate a practical example in which we configure what LLM to use at runtime. We will use both OpenAI and Anthropic models.

    ```typescript
    import { ChatOpenAI } from "@langchain/openai";
    import { ChatAnthropic } from "@langchain/anthropic";
    import { MessagesZodState, StateGraph, START, END } from "@langchain/langgraph";
    import { RunnableConfig } from "@langchain/core/runnables";
    import { z } from "zod";

    const ConfigSchema = z.object({
      modelProvider: z.string().default("anthropic"),
    });

    const MODELS = {
      anthropic: new ChatAnthropic({ model: "claude-3-5-haiku-latest" }),
      openai: new ChatOpenAI({ model: "gpt-4o-mini" }),
    };

    const graph = new StateGraph(MessagesZodState)
      .addNode("model", async (state, config) => {
        const modelProvider = config?.configurable?.modelProvider || "anthropic";
        const model = MODELS[modelProvider as keyof typeof MODELS];
        const response = await model.invoke(state.messages);
        return { messages: [response] };
      })
      .addEdge(START, "model")
      .addEdge("model", END)
      .compile();

    // Usage
    const inputMessage = { role: "user", content: "hi" };
    // With no configuration, uses default (Anthropic)
    const response1 = await graph.invoke({ messages: [inputMessage] });
    // Or, can set OpenAI
    const response2 = await graph.invoke(
      { messages: [inputMessage] },
      { configurable: { modelProvider: "openai" } }
    );

    console.log(response1.messages.at(-1)?.response_metadata?.model);
    console.log(response2.messages.at(-1)?.response_metadata?.model);
    ```
    ```
    claude-3-5-haiku-20241022
    gpt-4o-mini-2024-07-18
    ```
    :::

??? example "Extended example: specifying model and system message at runtime"

    :::python
    Below we demonstrate a practical example in which we configure two parameters: the LLM and system message to use at runtime.

    ```python
    from dataclasses import dataclass
    from typing import Optional
    from langchain.chat_models import init_chat_model
    from langchain_core.messages import SystemMessage
    from langgraph.graph import END, MessagesState, StateGraph, START
    from langgraph.runtime import Runtime
    from typing_extensions import TypedDict

    @dataclass
    class ContextSchema:
        model_provider: str = "anthropic"
        system_message: str | None = None

    MODELS = {
        "anthropic": init_chat_model("anthropic:claude-3-5-haiku-latest"),
        "openai": init_chat_model("openai:gpt-4.1-mini"),
    }

    def call_model(state: MessagesState, runtime: Runtime[ContextSchema]):
        model = MODELS[runtime.context.model_provider]
        messages = state["messages"]
        if (system_message := runtime.context.system_message):
            messages = [SystemMessage(system_message)] + messages
        response = model.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState, context_schema=ContextSchema)
    builder.add_node("model", call_model)
    builder.add_edge(START, "model")
    builder.add_edge("model", END)

    graph = builder.compile()

    # Usage
    input_message = {"role": "user", "content": "hi"}
    response = graph.invoke({"messages": [input_message]}, context={"model_provider": "openai", "system_message": "Respond in Italian."})
    for message in response["messages"]:
        message.pretty_print()
    ```
    ```
    ================================ Human Message ================================

    hi
    ================================== Ai Message ==================================

    Ciao! Come posso aiutarti oggi?
    ```
    :::

    :::js
    Below we demonstrate a practical example in which we configure two parameters: the LLM and system message to use at runtime.

    ```typescript
    import { ChatOpenAI } from "@langchain/openai";
    import { ChatAnthropic } from "@langchain/anthropic";
    import { SystemMessage } from "@langchain/core/messages";
    import { MessagesZodState, StateGraph, START, END } from "@langchain/langgraph";
    import { z } from "zod";

    const ConfigSchema = z.object({
      modelProvider: z.string().default("anthropic"),
      systemMessage: z.string().optional(),
    });

    const MODELS = {
      anthropic: new ChatAnthropic({ model: "claude-3-5-haiku-latest" }),
      openai: new ChatOpenAI({ model: "gpt-4o-mini" }),
    };

    const graph = new StateGraph(MessagesZodState)
      .addNode("model", async (state, config) => {
        const modelProvider = config?.configurable?.modelProvider || "anthropic";
        const systemMessage = config?.configurable?.systemMessage;
        
        const model = MODELS[modelProvider as keyof typeof MODELS];
        let messages = state.messages;
        
        if (systemMessage) {
          messages = [new SystemMessage(systemMessage), ...messages];
        }
        
        const response = await model.invoke(messages);
        return { messages: [response] };
      })
      .addEdge(START, "model")
      .addEdge("model", END)
      .compile();

    // Usage
    const inputMessage = { role: "user", content: "hi" };
    const response = await graph.invoke(
      { messages: [inputMessage] },
      {
        configurable: {
          modelProvider: "openai",
          systemMessage: "Respond in Italian."
        }
      }
    );
    
    for (const message of response.messages) {
      console.log(`${message.getType()}: ${message.content}`);
    }
    ```
    ```
    human: hi
    ai: Ciao! Come posso aiutarti oggi?
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757) (class in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`call_model`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6930) (function in langgraph)
- [`_run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/batch.py#L326) (function in checkpoint)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
