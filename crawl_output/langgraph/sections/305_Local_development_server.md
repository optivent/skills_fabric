## Local development server

To test your locally running application using LangGraph Studio, ensure your application is set up following [this guide](https://langchain-ai.github.io/langgraph/cloud/deployment/setup/).

!!! info "LangSmith Tracing"
    For local development, if you do not wish to have data traced to LangSmith, set `LANGSMITH_TRACING=false` in your application's `.env` file. With tracing disabled, no data will leave your local server.

Next, install the [LangGraph CLI](../../../concepts/langgraph_cli.md):

```
pip install -U "langgraph-cli[inmem]"
```

and run:

```
langgraph dev
```

!!! warning "Browser Compatibility"
    Safari blocks `localhost` connections to Studio. To work around this, run the above command with `--tunnel` to access Studio via a secure tunnel.

This will start the LangGraph Server locally, running in-memory. The server will run in watch mode, listening for and automatically restarting on code changes. Read this [reference](https://langchain-ai.github.io/langgraph/cloud/reference/cli/#dev) to learn about all the options for starting the API server.

If successful, you will see the following logs:

> Ready!
>
> - API: [http://localhost:2024](http://localhost:2024/)
>
> - Docs: http://localhost:2024/docs
>
> - LangGraph Studio Web UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

Once running, you will automatically be directed to LangGraph Studio.

For an already running server, access Studio by either:

1.  Directly navigate to the following URL: `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`.
2.  Within LangSmith, navigate to the LangGraph Platform Deployments tab, click the "LangGraph Studio" button, enter `http://127.0.0.1:2024` and click "Connect".

If running your server at a different host or port, simply update the `baseUrl` to match.

### Source References

- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`list`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L174) (function in checkpoint)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`Command`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L364) (class in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`read`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1044) (class in sdk-py)
- [`setup`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/tests/test_redis_cache.py#L14) (function in checkpoint)
- [`set`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L84) (function in checkpoint)
- [`conn`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/conftest.py#L15) (function in checkpoint-postgres)
- [`Row`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L1163) (class in checkpoint-postgres)
