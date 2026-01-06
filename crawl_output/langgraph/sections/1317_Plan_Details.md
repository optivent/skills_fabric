## Plan Details

|                                                                  | Developer                                   | Plus                                                  | Enterprise                                          |
|------------------------------------------------------------------|---------------------------------------------|-------------------------------------------------------|-----------------------------------------------------|
| Deployment Options                                               | Local                          | Cloud SaaS                                         | <ul><li>Cloud SaaS</li><li>Self-Hosted Data Plane</li><li>Self-Hosted Control Plane</li><li>Standalone Container</li></ul> |
| Usage                                                            | Free | See [Pricing](https://www.langchain.com/langgraph-platform-pricing) | Custom                                              |
| APIs for retrieving and updating state and conversational history | ✅                                           | ✅                                                     | ✅                                                   |
| APIs for retrieving and updating long-term memory                | ✅                                           | ✅                                                     | ✅                                                   |
| Horizontally scalable task queues and servers                    | ✅                                           | ✅                                                     | ✅                                                   |
| Real-time streaming of outputs and intermediate steps            | ✅                                           | ✅                                                     | ✅                                                   |
| Assistants API (configurable templates for LangGraph apps)       | ✅                                           | ✅                                                     | ✅                                                   |
| Cron scheduling                                                  | --                                          | ✅                                                     | ✅                                                   |
| LangGraph Studio for prototyping                                 | 	✅                                         | ✅                                                    | ✅                                                  |
| Authentication & authorization to call the LangGraph APIs        | --                                          | Coming Soon!                                          | Coming Soon!                                        |
| Smart caching to reduce traffic to LLM API                       | --                                          | Coming Soon!                                          | Coming Soon!                                        |
| Publish/subscribe API for state                                  | --                                          | Coming Soon!                                          | Coming Soon!                                        |
| Scheduling prioritization                                        | --                                          | Coming Soon!                                          | Coming Soon!                                        |

For pricing information, see [LangGraph Platform Pricing](https://www.langchain.com/langgraph-platform-pricing).

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`Assistant`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L242) (class in sdk-py)
- [`Cron`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L348) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`assistants`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L998) (class in sdk-py)
- [`Auth`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/__init__.py#L13) (class in sdk-py)
