## Prerequisites

1. Use the [LangGraph CLI](../../concepts/langgraph_cli.md) to [test your application locally](../../tutorials/langgraph-platform/local-server.md).
1. Use the [LangGraph CLI](../../concepts/langgraph_cli.md) to build a Docker image (i.e. `langgraph build`).
1. The following environment variables are needed for a standalone container deployment.
    1. `REDIS_URI`: Connection details to a Redis instance. Redis will be used as a pub-sub broker to enable streaming real time output from background runs. The value of `REDIS_URI` must be a valid [Redis connection URI](https://redis-py.readthedocs.io/en/stable/connections.html#redis.Redis.from_url).

        !!! Note "Shared Redis Instance"
            Multiple self-hosted deployments can share the same Redis instance. For example, for `Deployment A`, `REDIS_URI` can be set to `redis://<hostname_1>:<port>/1` and for `Deployment B`, `REDIS_URI` can be set to `redis://<hostname_1>:<port>/2`.

            `1` and `2` are different database numbers within the same instance, but `<hostname_1>` is shared. **The same database number cannot be used for separate deployments**.

    1. `DATABASE_URI`: Postgres connection details. Postgres will be used to store assistants, threads, runs, persist thread state and long term memory, and to manage the state of the background task queue with 'exactly once' semantics. The value of `DATABASE_URI` must be a valid [Postgres connection URI](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING-URIS).

        !!! Note "Shared Postgres Instance"
            Multiple self-hosted deployments can share the same Postgres instance. For example, for `Deployment A`, `DATABASE_URI` can be set to `postgres://<user>:<password>@/<database_name_1>?host=<hostname_1>` and for `Deployment B`, `DATABASE_URI` can be set to `postgres://<user>:<password>@/<database_name_2>?host=<hostname_1>`.

            `<database_name_1>` and `database_name_2` are different databases within the same instance, but `<hostname_1>` is shared. **The same database cannot be used for separate deployments**.

    1. `LANGGRAPH_CLOUD_LICENSE_KEY`: (if using [Enterprise](../../concepts/langgraph_data_plane.md#licensing)) LangGraph Platform license key. This will be used to authenticate ONCE at server start up.
    1. `LANGSMITH_ENDPOINT`: To send traces to a [self-hosted LangSmith](https://docs.smith.langchain.com/self_hosting) instance, set `LANGSMITH_ENDPOINT` to the hostname of the self-hosted LangSmith instance.
1. Egress to `https://beacon.langchain.com` from your network. This is required for license verification and usage reporting if not running in air-gapped mode. See the [Egress documentation](../../cloud/deployment/egress.md) for more details.

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`Assistant`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L242) (class in sdk-py)
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267) (class in sdk-py)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`Send`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L285) (class in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
