## 2. Add steps

Add steps to your graph. Every step will be checkpointed in its state history:

:::python

```python
config = {"configurable": {"thread_id": "1"}}
events = graph.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "I'm learning LangGraph. "
                    "Could you do some research on it for me?"
                ),
            },
        ],
    },
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
```

```
================================ Human Message =================================

I'm learning LangGraph. Could you do some research on it for me?
================================== Ai Message ==================================

[{'text': "Certainly! I'd be happy to research LangGraph for you. To get the most up-to-date and accurate information, I'll use the Tavily search engine to look this up. Let me do that for you now.", 'type': 'text'}, {'id': 'toolu_01BscbfJJB9EWJFqGrN6E54e', 'input': {'query': 'LangGraph latest information and features'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]
Tool Calls:
  tavily_search_results_json (toolu_01BscbfJJB9EWJFqGrN6E54e)
 Call ID: toolu_01BscbfJJB9EWJFqGrN6E54e
  Args:
    query: LangGraph latest information and features
================================= Tool Message =================================
Name: tavily_search_results_json

[{"url": "https://blockchain.news/news/langchain-new-features-upcoming-events-update", "content": "LangChain, a leading platform in the AI development space, has released its latest updates, showcasing new use cases and enhancements across its ecosystem. According to the LangChain Blog, the updates cover advancements in LangGraph Platform, LangSmith's self-improving evaluators, and revamped documentation for LangGraph."}, {"url": "https://blog.langchain.dev/langgraph-platform-announce/", "content": "With these learnings under our belt, we decided to couple some of our latest offerings under LangGraph Platform. LangGraph Platform today includes LangGraph Server, LangGraph Studio, plus the CLI and SDK. ... we added features in LangGraph Server to deliver on a few key value areas. Below, we'll focus on these aspects of LangGraph Platform."}]
================================== Ai Message ==================================

Thank you for your patience. I've found some recent information about LangGraph for you. Let me summarize the key points:

1. LangGraph is part of the LangChain ecosystem, which is a leading platform in AI development.

2. Recent updates and features of LangGraph include:

   a. LangGraph Platform: This seems to be a cloud-based version of LangGraph, though specific details weren't provided in the search results.
...
3. Keep an eye on LangGraph Platform developments, as cloud-based solutions often provide an easier starting point for learners.
4. Consider how LangGraph fits into the broader LangChain ecosystem, especially its interaction with tools like LangSmith.

Is there any specific aspect of LangGraph you'd like to know more about? I'd be happy to do a more focused search on particular features or use cases.
Output is truncated. View as a scrollable element or open in a text editor. Adjust cell output settings...
```

```python
events = graph.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": (
                    "Ya that's helpful. Maybe I'll "
                    "build an autonomous agent with it!"
                ),
            },
        ],
    },
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()
```

```
================================ Human Message =================================

Ya that's helpful. Maybe I'll build an autonomous agent with it!
================================== Ai Message ==================================

[{'text': "That's an exciting idea! Building an autonomous agent with LangGraph is indeed a great application of this technology. LangGraph is particularly well-suited for creating complex, multi-step AI workflows, which is perfect for autonomous agents. Let me gather some more specific information about using LangGraph for building autonomous agents.", 'type': 'text'}, {'id': 'toolu_01QWNHhUaeeWcGXvA4eHT7Zo', 'input': {'query': 'Building autonomous agents with LangGraph examples and tutorials'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]
Tool Calls:
  tavily_search_results_json (toolu_01QWNHhUaeeWcGXvA4eHT7Zo)
 Call ID: toolu_01QWNHhUaeeWcGXvA4eHT7Zo
  Args:
    query: Building autonomous agents with LangGraph examples and tutorials
================================= Tool Message =================================
Name: tavily_search_results_json

[{"url": "https://towardsdatascience.com/building-autonomous-multi-tool-agents-with-gemini-2-0-and-langgraph-ad3d7bd5e79d", "content": "Building Autonomous Multi-Tool Agents with Gemini 2.0 and LangGraph | by Youness Mansar | Jan, 2025 | Towards Data Science Building Autonomous Multi-Tool Agents with Gemini 2.0 and LangGraph A practical tutorial with full code examples for building and running multi-tool agents Towards Data Science LLMs are remarkable — they can memorize vast amounts of information, answer general knowledge questions, write code, generate stories, and even fix your grammar. In this tutorial, we are going to build a simple LLM agent that is equipped with four tools that it can use to answer a user's question. This Agent will have the following specifications: Follow Published in Towards Data Science --------------------------------- Your home for data science and AI. Follow Follow Follow"}, {"url": "https://github.com/anmolaman20/Tools_and_Agents", "content": "GitHub - anmolaman20/Tools_and_Agents: This repository provides resources for building AI agents using Langchain and Langgraph. This repository provides resources for building AI agents using Langchain and Langgraph. This repository provides resources for building AI agents using Langchain and Langgraph. This repository serves as a comprehensive guide for building AI-powered agents using Langchain and Langgraph. It provides hands-on examples, practical tutorials, and resources for developers and AI enthusiasts to master building intelligent systems and workflows. AI Agent Development: Gain insights into creating intelligent systems that think, reason, and adapt in real time. This repository is ideal for AI practitioners, developers exploring language models, or anyone interested in building intelligent systems. This repository provides resources for building AI agents using Langchain and Langgraph."}]
================================== Ai Message ==================================

Great idea! Building an autonomous agent with LangGraph is definitely an exciting project. Based on the latest information I've found, here are some insights and tips for building autonomous agents with LangGraph:

1. Multi-Tool Agents: LangGraph is particularly well-suited for creating autonomous agents that can use multiple tools. This allows your agent to have a diverse set of capabilities and choose the right tool for each task.

2. Integration with Large Language Models (LLMs): You can combine LangGraph with powerful LLMs like Gemini 2.0 to create more intelligent and capable agents. The LLM can serve as the "brain" of your agent, making decisions and generating responses.

3. Workflow Management: LangGraph excels at managing complex, multi-step AI workflows. This is crucial for autonomous agents that need to break down tasks into smaller steps and execute them in the right order.
...
6. Pay attention to how you structure the agent's decision-making process and workflow.
7. Don't forget to implement proper error handling and safety measures, especially if your agent will be interacting with external systems or making important decisions.

Building an autonomous agent is an iterative process, so be prepared to refine and improve your agent over time. Good luck with your project! If you need any more specific information as you progress, feel free to ask.
Output is truncated. View as a scrollable element or open in a text editor. Adjust cell output settings...
```

:::

:::js

```typescript
import { randomUUID } from "node:crypto";
const threadId = randomUUID();

let iter = 0;

for (const userInput of [
  "I'm learning LangGraph. Could you do some research on it for me?",
  "Ya that's helpful. Maybe I'll build an autonomous agent with it!",
]) {
  iter += 1;

  console.log(`\n--- Conversation Turn ${iter} ---\n`);
  const events = await graph.stream(
    { messages: [{ role: "user", content: userInput }] },
    { configurable: { thread_id: threadId }, streamMode: "values" }
  );

  for await (const event of events) {
    if ("messages" in event) {
      const lastMessage = event.messages.at(-1);

      console.log(
        "=".repeat(32),
        `${lastMessage?.getType()} Message`,
        "=".repeat(32)
      );
      console.log(lastMessage?.text);
    }
  }
}
```

```
--- Conversation Turn 1 ---

================================ human Message ================================
I'm learning LangGraph.js. Could you do some research on it for me?
================================ ai Message ================================
I'll search for information about LangGraph.js for you.
================================ tool Message ================================
{
  "query": "LangGraph.js framework TypeScript langchain what is it tutorial guide",
  "follow_up_questions": null,
  "answer": null,
  "images": [],
  "results": [
    {
      "url": "https://techcommunity.microsoft.com/blog/educatordeveloperblog/an-absolute-beginners-guide-to-langgraph-js/4212496",
      "title": "An Absolute Beginner's Guide to LangGraph.js",
      "content": "(...)",
      "score": 0.79369855,
      "raw_content": null
    },
    {
      "url": "https://langchain-ai.github.io/langgraphjs/",
      "title": "LangGraph.js",
      "content": "(...)",
      "score": 0.78154784,
      "raw_content": null
    }
  ],
  "response_time": 2.37
}
================================ ai Message ================================
Let me provide you with an overview of LangGraph.js based on the search results:

LangGraph.js is a JavaScript/TypeScript library that's part of the LangChain ecosystem, specifically designed for creating and managing complex LLM (Large Language Model) based workflows. Here are the key points about LangGraph.js:

1. Purpose:
- It's a low-level orchestration framework for building controllable agents
- Particularly useful for creating agentic workflows where LLMs decide the course of action based on current state
- Helps model workflows as graphs with nodes and edges

(...)

--- Conversation Turn 2 ---

================================ human Message ================================
Ya that's helpful. Maybe I'll build an autonomous agent with it!
================================ ai Message ================================
Let me search for specific information about building autonomous agents with LangGraph.js.
================================ tool Message ================================
{
  "query": "how to build autonomous agents with LangGraph.js examples tutorial react agent",
  "follow_up_questions": null,
  "answer": null,
  "images": [],
  "results": [
    {
      "url": "https://ai.google.dev/gemini-api/docs/langgraph-example",
      "title": "ReAct agent from scratch with Gemini 2.5 and LangGraph",
      "content": "(...)",
      "score": 0.7602419,
      "raw_content": null
    },
    {
      "url": "https://www.youtube.com/watch?v=ZfjaIshGkmk",
      "title": "Build Autonomous AI Agents with ReAct and LangGraph Tools",
      "content": "(...)",
      "score": 0.7471924,
      "raw_content": null
    }
  ],
  "response_time": 1.98
}
================================ ai Message ================================
Based on the search results, I can provide you with a practical overview of how to build an autonomous agent with LangGraph.js. Here's what you need to know:

1. Basic Structure for Building an Agent:
- LangGraph.js provides a ReAct (Reason + Act) pattern implementation
- The basic components include:
  - State management for conversation history
  - Nodes for different actions
  - Edges for decision-making flow
  - Tools for specific functionalities

(...)

```

:::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`execute`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1174) (function in prebuilt)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
