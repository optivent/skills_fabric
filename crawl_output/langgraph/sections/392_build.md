## `build`

=== "Python"

    Build LangGraph Platform API server Docker image.

    **Usage**

    ```
    langgraph build [OPTIONS]
    ```

    **Options**

    | Option               | Default          | Description                                                                                                     |
    | -------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------- |
    | `--platform TEXT`    |                  | Target platform(s) to build the Docker image for. Example: `langgraph build --platform linux/amd64,linux/arm64`              |
    | `-t, --tag TEXT`     |                  | **Required**. Tag for the Docker image. Example: `langgraph build -t my-image`                                               |
    | `--pull / --no-pull` | `--pull`         | Build with latest remote Docker image. Use `--no-pull` for running the LangGraph Platform API server with locally built images. |
    | `-c, --config FILE`  | `langgraph.json` | Path to configuration file declaring dependencies, graphs and environment variables.                                         |
    | `--help`             |                  | Display command documentation.                                                                                               |

=== "JS"

    Build LangGraph Platform API server Docker image.

    **Usage**

    ```
    npx @langchain/langgraph-cli build [OPTIONS]
    ```

    **Options**

    | Option               | Default          | Description                                                                                                     |
    | -------------------- | ---------------- | --------------------------------------------------------------------------------------------------------------- |
    | `--platform TEXT`    |                  | Target platform(s) to build the Docker image for. Example: `langgraph build --platform linux/amd64,linux/arm64`              |
    | `-t, --tag TEXT`     |                  | **Required**. Tag for the Docker image. Example: `langgraph build -t my-image`                                               |
    | `--no-pull`          |                  | Use locally built images. Defaults to `false` to build with latest remote Docker image.                                      |
    | `-c, --config FILE`  | `langgraph.json` | Path to configuration file declaring dependencies, graphs and environment variables.                                         |
    | `--help`             |                  | Display command documentation.                                                                                               |

### Source References

- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`Command`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L364) (class in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`json`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L173) (function in sdk-py)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`cli`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L164) (function in cli)
- [`build`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L310) (function in langgraph)
- [`run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/_branch.py#L122) (function in langgraph)
