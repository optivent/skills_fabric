## Define the multi-agent supervisor graph

supervisor = (
    StateGraph(MessagesState)
    # NOTE: `destinations` is only needed for visualization and doesn't affect runtime behavior
    .add_node(supervisor_agent, destinations=("research_agent", "math_agent", END))
    .add_node(research_agent)
    .add_node(math_agent)
    .add_edge(START, "supervisor")
    # always return back to the supervisor
    .add_edge("research_agent", "supervisor")
    .add_edge("math_agent", "supervisor")
    .compile()
)
```

Notice that we've added explicit [edges](../../concepts/low_level.md#edges) from worker agents back to the supervisor — this means that they are guaranteed to return control back to the supervisor. If you want the agents to respond directly to the user (i.e., turn the system into a router, you can remove these edges).

```python
from IPython.display import display, Image

display(Image(supervisor.get_graph().draw_mermaid_png()))
```

![Graph](assets/multi-output.png)

**Note:** When you run this code, it will generate and display a visual representation of the multi-agent supervisor graph showing the flow between the supervisor and worker agents.

With the multi-agent graph created, let's now run it!

```python
for chunk in supervisor.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "find US and New York state GDP in 2024. what % of US GDP was New York state?",
            }
        ]
    },
):
    pretty_print_messages(chunk, last_message=True)

final_message_history = chunk["supervisor"]["messages"]
```

**Output:**
```
Update from node supervisor:


================================= Tool Message ==================================
Name: transfer_to_research_agent

Successfully transferred to research_agent


Update from node research_agent:


================================== Ai Message ==================================
Name: research_agent

- US GDP in 2024 is projected to be about $28.18 trillion USD (Statista; CBO projection).
- New York State's nominal GDP for 2024 is estimated at approximately $2.16 trillion USD (various economic reports).
- New York State's share of US GDP in 2024 is roughly 7.7%.

Sources:
- https://www.statista.com/statistics/216985/forecast-of-us-gross-domestic-product/
- https://nyassembly.gov/Reports/WAM/2025economic_revenue/2025_report.pdf?v=1740533306


Update from node supervisor:


================================= Tool Message ==================================
Name: transfer_to_math_agent

Successfully transferred to math_agent


Update from node math_agent:


================================== Ai Message ==================================
Name: math_agent

US GDP in 2024: $28.18 trillion
New York State GDP in 2024: $2.16 trillion
Percentage of US GDP from New York State: 7.67%


Update from node supervisor:


================================== Ai Message ==================================
Name: supervisor

Here are your results:

- 2024 US GDP (projected): $28.18 trillion USD
- 2024 New York State GDP (estimated): $2.16 trillion USD
- New York State's share of US GDP: approximately 7.7%

If you need the calculation steps or sources, let me know!


```

Let's examine the full resulting message history:

```python
for message in final_message_history:
    message.pretty_print()
```

**Output:**
```
================================ Human Message ==================================

find US and New York state GDP in 2024. what % of US GDP was New York state?
================================== Ai Message ===================================
Name: supervisor
Tool Calls:
  transfer_to_research_agent (call_KlGgvF5ahlAbjX8d2kHFjsC3)
 Call ID: call_KlGgvF5ahlAbjX8d2kHFjsC3
  Args:
================================= Tool Message ==================================
Name: transfer_to_research_agent

Successfully transferred to research_agent
================================== Ai Message ===================================
Name: research_agent
Tool Calls:
  tavily_search (call_ZOaTVUA6DKrOjWQldLhtrsO2)
 Call ID: call_ZOaTVUA6DKrOjWQldLhtrsO2
  Args:
    query: US GDP 2024 estimate or actual
    search_depth: advanced
  tavily_search (call_QsRAasxW9K03lTlqjuhNLFbZ)
 Call ID: call_QsRAasxW9K03lTlqjuhNLFbZ
  Args:
    query: New York state GDP 2024 estimate or actual
    search_depth: advanced
================================= Tool Message ==================================
Name: tavily_search

{"query": "US GDP 2024 estimate or actual", "follow_up_questions": null, "answer": null, "images": [], "results": [{"url": "https://www.advisorperspectives.com/dshort/updates/2025/05/29/gdp-gross-domestic-product-q1-2025-second-estimate", "title": "Q1 GDP Second Estimate: Real GDP at -0.2%, Higher Than Expected", "content": "> Real gross domestic product (GDP) decreased at an annual rate of 0.2 percent in the first quarter of 2025 (January, February, and March), according to the second estimate released by the U.S. Bureau of Economic Analysis. In the fourth quarter of 2024, real GDP increased 2.4 percent. The decrease in real GDP in the first quarter primarily reflected an increase in imports, which are a subtraction in the calculation of GDP, and a decrease in government spending. These movements were partly [...] by [Harry Mamaysky](https://www.advisor```
```

!!! important
    You can see that the supervisor system appends **all** of the individual agent messages (i.e., their internal tool-calling loop) to the full message history. This means that on every supervisor turn, supervisor agent sees this full history. If you want more control over:

    * **how inputs are passed to agents**: you can use LangGraph @[`Send()`][Send] primitive to directly send data to the worker agents during the handoff. See the [task delegation](#4-create-delegation-tasks) example below
    * **how agent outputs are added**: you can control how much of the agent's internal message history is added to the overall supervisor message history by wrapping the agent in a separate node function:

        ```python
        def call_research_agent(state):
            # return agent's final response,
            # excluding inner monologue
            response = research_agent.invoke(state)
            # highlight-next-line
            return {"messages": response["messages"][-1]}
        ```

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`get_graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L704) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
