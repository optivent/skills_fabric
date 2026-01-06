## Resume a stream after page refresh

The `useStream()` hook can automatically resume an ongoing run upon mounting by setting `reconnectOnMount: true`. This is useful for continuing a stream after a page refresh, ensuring no messages and events generated during the downtime are lost.

```tsx
const thread = useStream<{ messages: Message[] }>({
  apiUrl: "http://localhost:2024",
  assistantId: "agent",
  reconnectOnMount: true,
});
```

By default the ID of the created run is stored in `window.sessionStorage`, which can be swapped by passing a custom storage in `reconnectOnMount` instead. The storage is used to persist the in-flight run ID for a thread (under `lg:stream:${threadId}` key).

```tsx
const thread = useStream<{ messages: Message[] }>({
  apiUrl: "http://localhost:2024",
  assistantId: "agent",
  reconnectOnMount: () => window.localStorage,
});
```

You can also manually manage the resuming process by using the run callbacks to persist the run metadata and the `joinStream` function to resume the stream. Make sure to pass `streamResumable: true` when creating the run; otherwise some events might be lost.

```tsx
import type { Message } from "@langchain/langgraph-sdk";
import { useStream } from "@langchain/langgraph-sdk/react";
import { useCallback, useState, useEffect, useRef } from "react";

export default function App() {
  const [threadId, onThreadId] = useSearchParam("threadId");

  const thread = useStream<{ messages: Message[] }>({
    apiUrl: "http://localhost:2024",
    assistantId: "agent",

    threadId,
    onThreadId,

    onCreated: (run) => {
      window.sessionStorage.setItem(`resume:${run.thread_id}`, run.run_id);
    },
    onFinish: (_, run) => {
      window.sessionStorage.removeItem(`resume:${run?.thread_id}`);
    },
  });

  // Ensure that we only join the stream once per thread.
  const joinedThreadId = useRef<string | null>(null);
  useEffect(() => {
    if (!threadId) return;

    const resume = window.sessionStorage.getItem(`resume:${threadId}`);
    if (resume && joinedThreadId.current !== threadId) {
      thread.joinStream(resume);
      joinedThreadId.current = threadId;
    }
  }, [threadId]);

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const form = e.target as HTMLFormElement;
        const message = new FormData(form).get("message") as string;
        thread.submit(
          { messages: [{ type: "human", content: message }] },
          { streamResumable: true }
        );
      }}
    >
      <div>
        {thread.messages.map((message) => (
          <div key={message.id}>{message.content as string}</div>
        ))}
      </div>
      <input type="text" name="message" />
      <button type="submit">Send</button>
    </form>
  );
}

// Utility method to retrieve and persist data in URL as search param
function useSearchParam(key: string) {
  const [value, setValue] = useState<string | null>(() => {
    const params = new URLSearchParams(window.location.search);
    return params.get(key) ?? null;
  });

  const update = useCallback(
    (value: string | null) => {
      setValue(value);

      const url = new URL(window.location.href);
      if (value == null) {
        url.searchParams.delete(key);
      } else {
        url.searchParams.set(key, value);
      }

      window.history.pushState({}, "", url.toString());
    },
    [key]
  );

  return [value, update] as const;
}
```

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`delete`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L929) (function in checkpoint)
- [`stream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L720) (function in langgraph)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`search`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L771) (function in checkpoint)
- [`join`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L6114) (function in sdk-py)
