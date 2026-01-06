## View run results

We can see that the thread has data only from the second run

=== "Python"

    ```python
    state = await client.threads.get_state(thread["thread_id"])

    for m in convert_to_messages(state["values"]["messages"]):
        m.pretty_print()
    ```

=== "Javascript"

    ```js
    const state = await client.threads.getState(thread["thread_id"]);

    for (const m of state['values']['messages']) {
      prettyPrint(m);
    }
    ```

=== "CURL"

    ```bash
    source pretty_print.sh && curl --request GET \
    --url <DEPLOYMENT_URL>/threads/<THREAD_ID>/state | \
    jq -c '.values.messages[]' | while read -r element; do
        type=$(echo "$element" | jq -r '.type')
        content=$(echo "$element" | jq -r '.content | if type == "array" then tostring else . end')
        pretty_print "$type" "$content"
    done
    ```

Output:

    ================================ Human Message =================================
    
    what's the weather in nyc?
    ================================== Ai Message ==================================
    
    [{'id': 'toolu_01JzPqefao1gxwajHQ3Yh3JD', 'input': {'query': 'weather in nyc'}, 'name': 'tavily_search_results_json', 'type': 'tool_use'}]
    Tool Calls:
      tavily_search_results_json (toolu_01JzPqefao1gxwajHQ3Yh3JD)
     Call ID: toolu_01JzPqefao1gxwajHQ3Yh3JD
      Args:
        query: weather in nyc
    ================================= Tool Message =================================
    Name: tavily_search_results_json
    
    [{"url": "https://www.weatherapi.com/", "content": "{'location': {'name': 'New York', 'region': 'New York', 'country': 'United States of America', 'lat': 40.71, 'lon': -74.01, 'tz_id': 'America/New_York', 'localtime_epoch': 1718734479, 'localtime': '2024-06-18 14:14'}, 'current': {'last_updated_epoch': 1718733600, 'last_updated': '2024-06-18 14:00', 'temp_c': 29.4, 'temp_f': 84.9, 'is_day': 1, 'condition': {'text': 'Sunny', 'icon': '//cdn.weatherapi.com/weather/64x64/day/113.png', 'code': 1000}, 'wind_mph': 2.2, 'wind_kph': 3.6, 'wind_degree': 158, 'wind_dir': 'SSE', 'pressure_mb': 1025.0, 'pressure_in': 30.26, 'precip_mm': 0.0, 'precip_in': 0.0, 'humidity': 63, 'cloud': 0, 'feelslike_c': 31.3, 'feelslike_f': 88.3, 'windchill_c': 28.3, 'windchill_f': 82.9, 'heatindex_c': 29.6, 'heatindex_f': 85.3, 'dewpoint_c': 18.4, 'dewpoint_f': 65.2, 'vis_km': 16.0, 'vis_miles': 9.0, 'uv': 7.0, 'gust_mph': 16.5, 'gust_kph': 26.5}}"}]
    ================================== Ai Message ==================================
    
    The weather API results show that the current weather in New York City is sunny with a temperature of around 85°F (29°C). The wind is light at around 2-3 mph from the south-southeast. Overall it looks like a nice sunny summer day in NYC.


Verify that the original, rolled back run was deleted

=== "Python"

    ```python
    try:
        await client.runs.get(thread["thread_id"], rolled_back_run["run_id"])
    except httpx.HTTPStatusError as _:
        print("Original run was correctly deleted")
    ```

=== "Javascript"

    ```js
    try {
      await client.runs.get(thread["thread_id"], rolledBackRun["run_id"]);
    } catch (e) {
      console.log("Original run was correctly deleted");
    }
    ```

Output:

    Original run was correctly deleted

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`_run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/batch.py#L326) (function in checkpoint)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`delete`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L929) (function in checkpoint)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`search`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L771) (function in checkpoint)
