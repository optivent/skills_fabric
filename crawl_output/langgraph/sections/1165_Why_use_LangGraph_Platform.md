## Why use LangGraph Platform?

<div align="center"><iframe width="560" height="315" src="https://www.youtube.com/embed/pfAQxBS5z88?si=XGS6Chydn6lhSO1S" title="What is LangGraph Platform?" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>

LangGraph Platform makes it easy to get your agent running in production —  whether it’s built with LangGraph or another framework — so you can focus on your app logic, not infrastructure. Deploy with one click to get a live endpoint, and use our robust APIs and built-in task queues to handle production scale. 

- **[Streaming Support](../cloud/how-tos/streaming.md)**: As agents grow more sophisticated, they often benefit from streaming both token outputs and intermediate states back to the user. Without this, users are left waiting for potentially long operations with no feedback. LangGraph Server provides multiple streaming modes optimized for various application needs.

- **[Background Runs](../cloud/how-tos/background_run.md)**: For agents that take longer to process (e.g., hours), maintaining an open connection can be impractical. The LangGraph Server supports launching agent runs in the background and provides both polling endpoints and webhooks to monitor run status effectively.
 
- **Support for long runs**: Regular server setups often encounter timeouts or disruptions when handling requests that take a long time to complete. LangGraph Server’s API provides robust support for these tasks by sending regular heartbeat signals, preventing unexpected connection closures during prolonged processes.

- **Handling Burstiness**: Certain applications, especially those with real-time user interaction, may experience "bursty" request loads where numerous requests hit the server simultaneously. LangGraph Server includes a task queue, ensuring requests are handled consistently without loss, even under heavy loads.

- **[Double-texting](../cloud/how-tos/interrupt_concurrent.md)**: In user-driven applications, it’s common for users to send multiple messages rapidly. This “double texting” can disrupt agent flows if not handled properly. LangGraph Server offers built-in strategies to address and manage such interactions.

- **[Checkpointers and memory management](persistence.md#checkpoints)**: For agents needing persistence (e.g., conversation memory), deploying a robust storage solution can be complex. LangGraph Platform includes optimized [checkpointers](persistence.md#checkpoints) and a [memory store](persistence.md#memory-store), managing state across sessions without the need for custom solutions.

- **[Human-in-the-loop support](../cloud/how-tos/human_in_the_loop_breakpoint.md)**: In many applications, users require a way to intervene in agent processes. LangGraph Server provides specialized endpoints for human-in-the-loop scenarios, simplifying the integration of manual oversight into agent workflows.

- **[LangGraph Studio](./langgraph_studio.md)**: Enables visualization, interaction, and debugging of agentic systems that implement the LangGraph Server API protocol. Studio also integrates with LangSmith to enable tracing, evaluation, and prompt engineering.

- **[Deployment](./deployment_options.md)**: There are four ways to deploy on LangGraph Platform: [Cloud SaaS](../concepts/langgraph_cloud.md), [Self-Hosted Data Plane](../concepts/langgraph_self_hosted_data_plane.md), [Self-Hosted Control Plane](../concepts/langgraph_self_hosted_control_plane.md), and [Standalone Container](../concepts/langgraph_standalone_container.md).

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`prompt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L566) (function in prebuilt)
- [`handle`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L135) (function in cli)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`_run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/batch.py#L326) (function in checkpoint)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
