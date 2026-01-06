## Commands

LangGraph CLI provides the following core functionality:

| Command                                                        | Description                                                                                                                                                                                                                                                                            |
| -------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`langgraph build`](../cloud/reference/cli.md#build)           | Builds a Docker image for the [LangGraph API server](./langgraph_server.md) that can be directly deployed.                                                                                                                                                                             |
| [`langgraph dev`](../cloud/reference/cli.md#dev)               | Starts a lightweight development server that requires no Docker installation. This server is ideal for rapid development and testing.                                                                                                                                                  |
| [`langgraph dockerfile`](../cloud/reference/cli.md#dockerfile) | Generates a [Dockerfile](https://docs.docker.com/reference/dockerfile/) that can be used to build images for and deploy instances of the [LangGraph API server](./langgraph_server.md). This is useful if you want to further customize the dockerfile or deploy in a more custom way. |
| [`langgraph up`](../cloud/reference/cli.md#up)                 | Starts an instance of the [LangGraph API server](./langgraph_server.md) locally in a docker container. This requires the docker server to be running locally. It also requires a LangSmith API key for local development or a license key for production use.                          |

For more information, see the [LangGraph CLI Reference](../cloud/reference/cli.md).

### Source References

- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`Command`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L364) (class in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`cli`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L164) (function in cli)
- [`up`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L3118) (function in langgraph)
- [`build`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L310) (function in langgraph)
- [`dockerfile`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L510) (function in cli)
- [`dev`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L685) (function in cli)
- [`run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/_branch.py#L122) (function in langgraph)
