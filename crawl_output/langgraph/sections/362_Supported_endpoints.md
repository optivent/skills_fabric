## Supported endpoints

The following API endpoints accept a `webhook` parameter:

| Operation            | HTTP Method | Endpoint                          |
|----------------------|-------------|-----------------------------------|
| Create Run           | `POST`      | `/thread/{thread_id}/runs`        |
| Create Thread Cron   | `POST`      | `/thread/{thread_id}/runs/crons`  |
| Stream Run           | `POST`      | `/thread/{thread_id}/runs/stream` |
| Wait Run             | `POST`      | `/thread/{thread_id}/runs/wait`   |
| Create Cron          | `POST`      | `/runs/crons`                     |
| Stream Run Stateless | `POST`      | `/runs/stream`                    |
| Wait Run Stateless   | `POST`      | `/runs/wait`                      |

In this guide, we’ll show how to trigger a webhook after streaming a run.

### Source References

- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`Cron`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L348) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`crons`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1034) (class in sdk-py)
