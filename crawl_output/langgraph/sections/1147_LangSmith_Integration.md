## LangSmith Integration

A [LangSmith](https://docs.smith.langchain.com/) tracing project and LangSmith API key are automatically created for each deployment. The deployment uses the API key to automatically send traces to LangSmith.

- The tracing project has the same name as the deployment.
- The API key has the description `LangGraph Platform: <deployment_name>`.
- The API key is never revealed and cannot be deleted manually.
- When creating a deployment, the `LANGCHAIN_TRACING` and `LANGSMITH_API_KEY`/`LANGCHAIN_API_KEY` environment variables do not need to be specified; they are set automatically by the control plane.

When a deployment is deleted, the traces and the tracing project are not deleted. However, the API will be deleted when the deployment is deleted.

### Source References

- [`delete`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L929) (function in checkpoint)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`Send`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L285) (class in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`set`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L84) (function in checkpoint)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`a`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4642) (function in langgraph)
- [`A`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L124) (class in langgraph)
- [`B`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L128) (class in langgraph)
- [`b`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4645) (function in langgraph)
