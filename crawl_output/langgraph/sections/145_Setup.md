## Setup

1. You give us your LangSmith organization ID. We will enable the Self-Hosted Data Plane for your organization.
1. We provide you a [Helm chart](https://github.com/langchain-ai/helm/tree/main/charts/langgraph-dataplane) which you run to setup your Kubernetes cluster. This chart contains a few important components.
    1. `langgraph-listener`: This is a service that listens to LangChain's [control plane](../../concepts/langgraph_control_plane.md) for changes to your deployments and creates/updates downstream CRDs.
    1. `LangGraphPlatform CRD`: A CRD for LangGraph Platform deployments. This contains the spec for managing an instance of a LangGraph Platform deployment.
    1. `langgraph-platform-operator`: This operator handles changes to your LangGraph Platform CRDs.
1. Configure your `langgraph-dataplane-values.yaml` file.

        config:
          langsmithApiKey: "" # API Key of your Workspace
          langsmithWorkspaceId: "" # Workspace ID
          hostBackendUrl: "https://api.host.langchain.com" # Only override this if on EU
          smithBackendUrl: "https://api.smith.langchain.com" # Only override this if on EU

1. Deploy `langgraph-dataplane` Helm chart.

        helm repo add langchain https://langchain-ai.github.io/helm/
        helm repo update
        helm upgrade -i langgraph-dataplane langchain/langgraph-dataplane --values langgraph-dataplane-values.yaml

1. If successful, you will see two services start up in your namespace.

        NAME                                          READY   STATUS              RESTARTS   AGE
        langgraph-dataplane-listener-7fccd788-wn2dx   0/1     Running             0          9s
        langgraph-dataplane-redis-0                   0/1     ContainerCreating   0          9s

1. You create a deployment from the [control plane UI](../../concepts/langgraph_control_plane.md#control-plane-ui).

### Source References

- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`override`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/runtime.py#L117) (function in langgraph)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`list`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L174) (function in checkpoint)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
