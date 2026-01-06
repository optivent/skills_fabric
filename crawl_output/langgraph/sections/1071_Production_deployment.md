## Production deployment

There are 4 main options for deploying with the [LangGraph Platform](langgraph_platform.md):

1. [Cloud SaaS](#cloud-saas)

1. [Self-Hosted Data Plane](#self-hosted-data-plane)

1. [Self-Hosted Control Plane](#self-hosted-control-plane)

1. [Standalone Container](#standalone-container)


A quick comparison:

|                      | **Cloud SaaS** | **Self-Hosted Data Plane** | **Self-Hosted Control Plane** | **Standalone Container** |
|----------------------|----------------|----------------------------|-------------------------------|--------------------------|
| **[Control plane UI/API](../concepts/langgraph_control_plane.md)** | Yes | Yes | Yes | No |
| **CI/CD** | Managed internally by platform | Managed externally by you | Managed externally by you | Managed externally by you |
| **Data/compute residency** | LangChain's cloud | Your cloud | Your cloud | Your cloud |
| **LangSmith compatibility** | Trace to LangSmith SaaS | Trace to LangSmith SaaS | Trace to Self-Hosted LangSmith | Optional tracing |
| **[Pricing](https://www.langchain.com/pricing-langgraph-platform)** | Plus | Enterprise | Enterprise | Enterprise |

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`main`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6527) (function in langgraph)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`a`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4642) (function in langgraph)
- [`A`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L124) (class in langgraph)
- [`B`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L128) (class in langgraph)
- [`b`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4645) (function in langgraph)
- [`one`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L8554) (function in langgraph)
- [`side`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L3130) (function in langgraph)
