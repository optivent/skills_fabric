## 2. Using a prebuilt agent

Given these tools, we can initialize a pre-built agent in a single line. To customize our agents behavior, we write a descriptive system prompt.

```python
from langgraph.prebuilt import create_react_agent

system_prompt = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Then you should query the schema of the most relevant tables.
""".format(
    dialect=db.dialect,
    top_k=5,
)

agent = create_react_agent(
    llm,
    tools,
    prompt=system_prompt,
)
```

!!! note
    This system prompt includes a number of instructions, such as always running specific tools before or after others. In the [next section](#3-customizing-the-agent), we will enforce these behaviors through the graph's structure, providing us a greater degree of control and allowing us to simplify the prompt.

Let's run this agent on a sample query and observe its behavior:

```python
question = "Which genre on average has the longest tracks?"

for step in agent.stream(
    {"messages": [{"role": "user", "content": question}]},
    stream_mode="values",
):
    step["messages"][-1].pretty_print()
```

**Output:**
```
================================ Human Message =================================

Which genre on average has the longest tracks?
================================== Ai Message ==================================
Tool Calls:
  sql_db_list_tables (call_d8lCgywSroCgpVl558nmXKwA)
 Call ID: call_d8lCgywSroCgpVl558nmXKwA
  Args:
================================= Tool Message =================================
Name: sql_db_list_tables

Album, Artist, Customer, Employee, Genre, Invoice, InvoiceLine, MediaType, Playlist, PlaylistTrack, Track
================================== Ai Message ==================================
Tool Calls:
  sql_db_schema (call_nNf6IIUcwMYLIkE0l6uWkZHe)
 Call ID: call_nNf6IIUcwMYLIkE0l6uWkZHe
  Args:
    table_names: Genre, Track
================================= Tool Message =================================
Name: sql_db_schema


CREATE TABLE "Genre" (
    "GenreId" INTEGER NOT NULL, 
    "Name" NVARCHAR(120), 
    PRIMARY KEY ("GenreId")
)

/*
3 rows from Genre table:
GenreId Name
1   Rock
2   Jazz
3   Metal
*/


CREATE TABLE "Track" (
    "TrackId" INTEGER NOT NULL, 
    "Name" NVARCHAR(200) NOT NULL, 
    "AlbumId" INTEGER, 
    "MediaTypeId" INTEGER NOT NULL, 
    "GenreId" INTEGER, 
    "Composer" NVARCHAR(220), 
    "Milliseconds" INTEGER NOT NULL, 
    "Bytes" INTEGER, 
    "UnitPrice" NUMERIC(10, 2) NOT NULL, 
    PRIMARY KEY ("TrackId"), 
    FOREIGN KEY("MediaTypeId") REFERENCES "MediaType" ("MediaTypeId"), 
    FOREIGN KEY("GenreId") REFERENCES "Genre" ("GenreId"), 
    FOREIGN KEY("AlbumId") REFERENCES "Album" ("AlbumId")
)

/*
3 rows from Track table:
TrackId Name    AlbumId MediaTypeId GenreId Composer    Milliseconds    Bytes   UnitPrice
1   For Those About To Rock (We Salute You) 1   1   1   Angus Young, Malcolm Young, Brian Johnson   343719  11170334    0.99
2   Balls to the Wall   2   2   1   None    342562  5510424 0.99
3   Fast As a Shark 3   2   1   F. Baltes, S. Kaufman, U. Dirkscneider & W. Hoffman 230619  3990994 0.99
*/
================================== Ai Message ==================================
Tool Calls:
  sql_db_query_checker (call_urTRmtiGtTxkwHtscec7Fd2K)
 Call ID: call_urTRmtiGtTxkwHtscec7Fd2K
  Args:
    query: SELECT Genre.Name, AVG(Track.Milliseconds) AS AvgMilliseconds
FROM Track
JOIN Genre ON Track.GenreId = Genre.GenreId
GROUP BY Genre.Name
ORDER BY AvgMilliseconds DESC
LIMIT 1;
================================= Tool Message =================================
Name: sql_db_query_checker

\`\`\`sql
SELECT Genre.Name, AVG(Track.Milliseconds) AS AvgMilliseconds
FROM Track
JOIN Genre ON Track.GenreId = Genre.GenreId
GROUP BY Genre.Name
ORDER BY AvgMilliseconds DESC
LIMIT 1;
\`\`\`
================================== Ai Message ==================================
Tool Calls:
  sql_db_query (call_RNMqyUEMv0rvy0UxSwrXY2AV)
 Call ID: call_RNMqyUEMv0rvy0UxSwrXY2AV
  Args:
    query: SELECT Genre.Name, AVG(Track.Milliseconds) AS AvgMilliseconds
FROM Track
JOIN Genre ON Track.GenreId = Genre.GenreId
GROUP BY Genre.Name
ORDER BY AvgMilliseconds DESC
LIMIT 1;
================================= Tool Message =================================
Name: sql_db_query

[('Sci Fi & Fantasy', 2911783.0384615385)]
================================== Ai Message ==================================

The genre with the longest average track length is "Sci Fi & Fantasy," with an average duration of about 2,911,783 milliseconds (approximately 48.5 minutes) per track.
```

This worked well enough: the agent correctly listed the tables, obtained the schemas, wrote a query, checked the query, and ran it to inform its final response.

!!! tip
    You can inspect all aspects of the above run, including steps taken, tools invoked, what prompts were seen by the LLM, and more in the [LangSmith trace](https://smith.langchain.com/public/bd594960-73e3-474b-b6f2-db039d7c713a/r).

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7586) (function in langgraph)
- [`prompt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L566) (function in prebuilt)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`create_react_agent`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L273) (function in prebuilt)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`delete`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L929) (function in checkpoint)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
