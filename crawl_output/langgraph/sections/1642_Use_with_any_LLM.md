## Use with any LLM

:::python
You can use `stream_mode="custom"` to stream data from **any LLM API** — even if that API does **not** implement the LangChain chat model interface.

This lets you integrate raw LLM clients or external services that provide their own streaming interfaces, making LangGraph highly flexible for custom setups.

```python
from langgraph.config import get_stream_writer

def call_arbitrary_model(state):
    """Example node that calls an arbitrary model and streams the output"""
    # highlight-next-line
    writer = get_stream_writer() # (1)!
    # Assume you have a streaming client that yields chunks
    for chunk in your_custom_streaming_client(state["topic"]): # (2)!
        # highlight-next-line
        writer({"custom_llm_chunk": chunk}) # (3)!
    return {"result": "completed"}

graph = (
    StateGraph(State)
    .add_node(call_arbitrary_model)
    # Add other nodes and edges as needed
    .compile()
)

for chunk in graph.stream(
    {"topic": "cats"},
    # highlight-next-line
    stream_mode="custom", # (4)!
):
    # The chunk will contain the custom data streamed from the llm
    print(chunk)
```

1. Get the stream writer to send custom data.
2. Generate LLM tokens using your custom streaming client.
3. Use the writer to send custom data to the stream.
4. Set `stream_mode="custom"` to receive the custom data in the stream.
   :::

:::js
You can use `streamMode: "custom"` to stream data from **any LLM API** — even if that API does **not** implement the LangChain chat model interface.

This lets you integrate raw LLM clients or external services that provide their own streaming interfaces, making LangGraph highly flexible for custom setups.

```typescript
import { LangGraphRunnableConfig } from "@langchain/langgraph";

const callArbitraryModel = async (
  state: any,
  config: LangGraphRunnableConfig
) => {
  // Example node that calls an arbitrary model and streams the output
  // Assume you have a streaming client that yields chunks
  for await (const chunk of yourCustomStreamingClient(state.topic)) {
    // (1)!
    config.writer({ custom_llm_chunk: chunk }); // (2)!
  }
  return { result: "completed" };
};

const graph = new StateGraph(State)
  .addNode("callArbitraryModel", callArbitraryModel)
  // Add other nodes and edges as needed
  .compile();

for await (const chunk of await graph.stream(
  { topic: "cats" },
  { streamMode: "custom" } // (3)!
)) {
  // The chunk will contain the custom data streamed from the llm
  console.log(chunk);
}
```

1. Generate LLM tokens using your custom streaming client.
2. Use the writer to send custom data to the stream.
3. Set `streamMode: "custom"` to receive the custom data in the stream.
   :::

??? example "Extended example: streaming arbitrary chat model"

      :::python
      ```python
      import operator
      import json

      from typing import TypedDict
      from typing_extensions import Annotated
      from langgraph.graph import StateGraph, START

      from openai import AsyncOpenAI

      openai_client = AsyncOpenAI()
      model_name = "gpt-4o-mini"


      async def stream_tokens(model_name: str, messages: list[dict]):
          response = await openai_client.chat.completions.create(
              messages=messages, model=model_name, stream=True
          )
          role = None
          async for chunk in response:
              delta = chunk.choices[0].delta

              if delta.role is not None:
                  role = delta.role

              if delta.content:
                  yield {"role": role, "content": delta.content}


      # this is our tool
      async def get_items(place: str) -> str:
          """Use this tool to list items one might find in a place you're asked about."""
          writer = get_stream_writer()
          response = ""
          async for msg_chunk in stream_tokens(
              model_name,
              [
                  {
                      "role": "user",
                      "content": (
                          "Can you tell me what kind of items "
                          f"i might find in the following place: '{place}'. "
                          "List at least 3 such items separating them by a comma. "
                          "And include a brief description of each item."
                      ),
                  }
              ],
          ):
              response += msg_chunk["content"]
              writer(msg_chunk)

          return response


      class State(TypedDict):
          messages: Annotated[list[dict], operator.add]


      # this is the tool-calling graph node
      async def call_tool(state: State):
          ai_message = state["messages"][-1]
          tool_call = ai_message["tool_calls"][-1]

          function_name = tool_call["function"]["name"]
          if function_name != "get_items":
              raise ValueError(f"Tool {function_name} not supported")

          function_arguments = tool_call["function"]["arguments"]
          arguments = json.loads(function_arguments)

          function_response = await get_items(**arguments)
          tool_message = {
              "tool_call_id": tool_call["id"],
              "role": "tool",
              "name": function_name,
              "content": function_response,
          }
          return {"messages": [tool_message]}


      graph = (
          StateGraph(State)
          .add_node(call_tool)
          .add_edge(START, "call_tool")
          .compile()
      )
      ```

      Let's invoke the graph with an AI message that includes a tool call:

      ```python
      inputs = {
          "messages": [
              {
                  "content": None,
                  "role": "assistant",
                  "tool_calls": [
                      {
                          "id": "1",
                          "function": {
                              "arguments": '{"place":"bedroom"}',
                              "name": "get_items",
                          },
                          "type": "function",
                      }
                  ],
              }
          ]
      }

      async for chunk in graph.astream(
          inputs,
          stream_mode="custom",
      ):
          print(chunk["content"], end="|", flush=True)
      ```
      :::

      :::js
      ```typescript
      import { StateGraph, START, LangGraphRunnableConfig } from "@langchain/langgraph";
      import { z } from "zod";
      import OpenAI from "openai";

      const openaiClient = new OpenAI();
      const modelName = "gpt-4o-mini";

      async function* streamTokens(modelName: string, messages: any[]) {
        const response = await openaiClient.chat.completions.create({
          messages,
          model: modelName,
          stream: true,
        });

        let role: string | null = null;
        for await (const chunk of response) {
          const delta = chunk.choices[0]?.delta;

          if (delta?.role) {
            role = delta.role;
          }

          if (delta?.content) {
            yield { role, content: delta.content };
          }
        }
      }

      // this is our tool
      const getItems = tool(
        async (input, config: LangGraphRunnableConfig) => {
          let response = "";
          for await (const msgChunk of streamTokens(
            modelName,
            [
              {
                role: "user",
                content: `Can you tell me what kind of items i might find in the following place: '${input.place}'. List at least 3 such items separating them by a comma. And include a brief description of each item.`,
              },
            ]
          )) {
            response += msgChunk.content;
            config.writer?.(msgChunk);
          }
          return response;
        },
        {
          name: "get_items",
          description: "Use this tool to list items one might find in a place you're asked about.",
          schema: z.object({
            place: z.string().describe("The place to look up items for."),
          }),
        }
      );

      const State = z.object({
        messages: z.array(z.any()),
      });

      const graph = new StateGraph(State)
        // this is the tool-calling graph node
        .addNode("callTool", async (state) => {
          const aiMessage = state.messages.at(-1);
          const toolCall = aiMessage.tool_calls?.at(-1);

          const functionName = toolCall?.function?.name;
          if (functionName !== "get_items") {
            throw new Error(`Tool ${functionName} not supported`);
          }

          const functionArguments = toolCall?.function?.arguments;
          const args = JSON.parse(functionArguments);

          const functionResponse = await getItems.invoke(args);
          const toolMessage = {
            tool_call_id: toolCall.id,
            role: "tool",
            name: functionName,
            content: functionResponse,
          };
          return { messages: [toolMessage] };
        })
        .addEdge(START, "callTool")
        .compile();
      ```

      Let's invoke the graph with an AI message that includes a tool call:

      ```typescript
      const inputs = {
        messages: [
          {
            content: null,
            role: "assistant",
            tool_calls: [
              {
                id: "1",
                function: {
                  arguments: '{"place":"bedroom"}',
                  name: "get_items",
                },
                type: "function",
              }
            ],
          }
        ]
      };

      for await (const chunk of await graph.stream(
        inputs,
        { streamMode: "custom" }
      )) {
        console.log(chunk.content + "|");
      }
      ```
      :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
