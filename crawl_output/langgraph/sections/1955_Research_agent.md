## Research agent

For web search, we will use `TavilySearch` tool from `langchain-tavily`:

```python
from langchain_tavily import TavilySearch

web_search = TavilySearch(max_results=3)
web_search_results = web_search.invoke("who is the mayor of NYC?")

print(web_search_results["results"][0]["content"])
```

**Output:**
```
Find events, attractions, deals, and more at nyctourism.com Skip Main Navigation Menu The Official Website of the City of New York Text Size Powered by Translate SearchSearch Primary Navigation The official website of NYC Home NYC Resources NYC311 Office of the Mayor Events Connect Jobs Search Office of the Mayor | Mayor's Bio | City of New York Secondary Navigation MayorBiographyNewsOfficials Eric L. Adams 110th Mayor of New York City Mayor Eric Adams has served the people of New York City as an NYPD officer, State Senator, Brooklyn Borough President, and now as the 110th Mayor of the City of New York. Mayor Eric Adams has served the people of New York City as an NYPD officer, State Senator, Brooklyn Borough President, and now as the 110th Mayor of the City of New York. He gave voice to a diverse coalition of working families in all five boroughs and is leading the fight to bring back New York City's economy, reduce inequality, improve public safety, and build a stronger, healthier city that delivers for all New Yorkers. As the representative of one of the nation's largest counties, Eric fought tirelessly to grow the local economy, invest in schools, reduce inequality, improve public safety, and advocate for smart policies and better government that delivers for all New Yorkers.
```

To create individual worker agents, we will use LangGraph's prebuilt [agent](../../agents/agents.md).

```python
from langgraph.prebuilt import create_react_agent

research_agent = create_react_agent(
    model="openai:gpt-4.1",
    tools=[web_search],
    prompt=(
        "You are a research agent.\n\n"
        "INSTRUCTIONS:\n"
        "- Assist ONLY with research-related tasks, DO NOT do any math\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."
    ),
    name="research_agent",
)
```

Let's [run the agent](../../agents/run_agents.md) to verify that it behaves as expected. 

!!! note "We'll use `pretty_print_messages` helper to render the streamed agent outputs nicely"

  ```python
  from langchain_core.messages import convert_to_messages


  def pretty_print_message(message, indent=False):
      pretty_message = message.pretty_repr(html=True)
      if not indent:
          print(pretty_message)
          return

      indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
      print(indented)


  def pretty_print_messages(update, last_message=False):
      is_subgraph = False
      if isinstance(update, tuple):
          ns, update = update
          # skip parent graph updates in the printouts
          if len(ns) == 0:
              return

          graph_id = ns[-1].split(":")[0]
          print(f"Update from subgraph {graph_id}:")
          print("\n")
          is_subgraph = True

      for node_name, node_update in update.items():
          update_label = f"Update from node {node_name}:"
          if is_subgraph:
              update_label = "\t" + update_label

          print(update_label)
          print("\n")

          messages = convert_to_messages(node_update["messages"])
          if last_message:
              messages = messages[-1:]

          for m in messages:
              pretty_print_message(m, indent=is_subgraph)
          print("\n")
  ```

  ```python
  for chunk in research_agent.stream(
      {"messages": [{"role": "user", "content": "who is the mayor of NYC?"}]}
  ):
      pretty_print_messages(chunk)
  ```

  **Output:**
  ```
  Update from node agent:


  ================================== Ai Message ==================================
  Name: research_agent
  Tool Calls:
    tavily_search (call_U748rQhQXT36sjhbkYLSXQtJ)
   Call ID: call_U748rQhQXT36sjhbkYLSXQtJ
    Args:
      query: current mayor of New York City
      search_depth: basic


  Update from node tools:


  ================================= Tool Message ==================================
  Name: tavily_search

  {"query": "current mayor of New York City", "follow_up_questions": null, "answer": null, "images": [], "results": [{"title": "List of mayors of New York City - Wikipedia", "url": "https://en.wikipedia.org/wiki/List_of_mayors_of_New_York_City", "content": "The mayor of New York City is the chief executive of the Government of New York City, as stipulated by New York City's charter.The current officeholder, the 110th in the sequence of regular mayors, is Eric Adams, a member of the Democratic Party.. During the Dutch colonial period from 1624 to 1664, New Amsterdam was governed by the Director of Netherland.", "score": 0.9039154, "raw_content": null}, {"title": "Office of the Mayor | Mayor's Bio | City of New York - NYC.gov", "url": "https://www.nyc.gov/office-of-the-mayor/bio.page", "content": "Mayor Eric Adams has served the people of New York City as an NYPD officer, State Senator, Brooklyn Borough President, and now as the 110th Mayor of the City of New York. He gave voice to a diverse coalition of working families in all five boroughs and is leading the fight to bring back New York City's economy, reduce inequality, improve", "score": 0.8405867, "raw_content": null}, {"title": "Eric Adams - Wikipedia", "url": "https://en.wikipedia.org/wiki/Eric_Adams", "content": "Eric Leroy Adams (born September 1, 1960) is an American politician and former police officer who has served as the 110th mayor of New York City since 2022. Adams was an officer in the New York City Transit Police and then the New York City Police Department (```
  ```

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`prompt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L566) (function in prebuilt)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
