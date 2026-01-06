## Prerequisites

1. You are using Kubernetes.
1. You have self-hosted LangSmith deployed.
1. Use the [LangGraph CLI](../../concepts/langgraph_cli.md) to [test your application locally](../../tutorials/langgraph-platform/local-server.md).
1. Use the [LangGraph CLI](../../concepts/langgraph_cli.md) to build a Docker image (i.e. `langgraph build`) and push it to a registry your Kubernetes cluster has access to.
1. `KEDA` is installed on your cluster.

         helm repo add kedacore https://kedacore.github.io/charts 
         helm install keda kedacore/keda --namespace keda --create-namespace
1. Ingress Configuration
    1. You must set up an ingress for your LangSmith instance. All agents will be deployed as Kubernetes services behind this ingress.
    1. You can use this guide to [set up an ingress](https://docs.smith.langchain.com/self_hosting/configuration/ingress) for your instance.
1. You have slack space in your cluster for multiple deployments. `Cluster-Autoscaler` is recommended to automatically provision new nodes.
1. A valid Dynamic PV provisioner or PVs available on your cluster. You can verify this by running:

        kubectl get storageclass

1. Egress to `https://beacon.langchain.com` from your network. This is required for license verification and usage reporting if not running in air-gapped mode. See the [Egress documentation](../../cloud/deployment/egress.md) for more details.

### Source References

- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`set`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L84) (function in checkpoint)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`cli`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L164) (function in cli)
- [`up`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L3118) (function in langgraph)
