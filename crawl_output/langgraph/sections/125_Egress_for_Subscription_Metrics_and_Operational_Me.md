## Egress for Subscription Metrics and Operational Metadata

> **Important: Self Hosted Only** 
> This section only applies to customers who are not running in offline mode and assumes you are using a self-hosted LangGraph Platform instance.
> This does not apply to SaaS or Hybrid deployments.

Self-Hosted LangGraph Platform instances store all information locally and will never send sensitive information outside of your network. We currently only track platform usage for billing purposes according to the entitlements in your order. In order to better remotely support our customers, we do require egress to `https://beacon.langchain.com`.

In the future, we will be introducing support diagnostics to help us ensure that the LangGraph Platform is running at an optimal level within your environment.

> **Warning**  
> **This will require egress to `https://beacon.langchain.com` from your network.**
> **If using an API key, you will also need to allow egress to `https://api.smith.langchain.com` or `https://eu.api.smith.langchain.com` for API key verification.**

Generally, data that we send to Beacon can be categorized as follows:

- **Subscription Metrics**
  - Subscription metrics are used to determine level of access and utilization of LangSmith. This includes, but are not limited to:
    - Nodes Executed
    - Runs Executed
    - License Key Verification
- **Operational Metadata**
  - This metadata will contain and collect the above subscription metrics to assist with remote support, allowing the LangChain team to diagnose and troubleshoot performance issues more effectively and proactively.

### Source References

- [`execute`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1174) (function in prebuilt)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327) (class in sdk-py)
- [`Send`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L285) (class in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`store`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/test_store.py#L34) (function in checkpoint-postgres)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`Section`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4009) (class in langgraph)
- [`up`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L3118) (function in langgraph)
- [`run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/_branch.py#L122) (function in langgraph)
- [`Cat`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel_async.py#L4123) (class in langgraph)
