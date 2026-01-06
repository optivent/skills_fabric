## Setup

1. As part of configuring your Self-Hosted LangSmith instance, you enable the `langgraphPlatform` option. This will provision a few key resources.
    1. `listener`: This is a service that listens to the [control plane](../../concepts/langgraph_control_plane.md) for changes to your deployments and creates/updates downstream CRDs.
    1. `LangGraphPlatform CRD`: A CRD for LangGraph Platform deployments. This contains the spec for managing an instance of a LangGraph platform deployment.
    1. `operator`: This operator handles changes to your LangGraph Platform CRDs.
    1. `host-backend`: This is the [control plane](../../concepts/langgraph_control_plane.md).
1. Two additional images will be used by the chart. Use the images that are specified in the latest release.

        hostBackendImage:
          repository: "docker.io/langchain/hosted-langserve-backend"
          pullPolicy: IfNotPresent
        operatorImage:
          repository: "docker.io/langchain/langgraph-operator"
          pullPolicy: IfNotPresent

1. In your config file for langsmith (usually `langsmith_config.yaml`, enable the `langgraphPlatform` option. Note that you must also have a valid ingress setup:

        config:
          langgraphPlatform:
            enabled: true
            langgraphPlatformLicenseKey: "YOUR_LANGGRAPH_PLATFORM_LICENSE_KEY"
1. In your `values.yaml` file, configure the `hostBackendImage` and `operatorImage` options (if you need to mirror images)

1. You can also configure base templates for your agents by overriding the base templates [here](https://github.com/langchain-ai/helm/blob/main/charts/langsmith/values.yaml#L898).
1. You create a deployment from the [control plane UI](../../concepts/langgraph_control_plane.md#control-plane-ui).

### Source References

- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129) (function in prebuilt)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`list`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L174) (function in checkpoint)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
