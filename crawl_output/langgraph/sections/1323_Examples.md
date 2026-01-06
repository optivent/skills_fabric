## Examples

:::python
While most users will interact with Pregel through the @[StateGraph][StateGraph] API or the @[entrypoint][entrypoint] decorator, it is possible to interact with Pregel directly.
:::

:::js
While most users will interact with Pregel through the @[StateGraph] API or the @[entrypoint] decorator, it is possible to interact with Pregel directly.
:::

Below are a few different examples to give you a sense of the Pregel API.

=== "Single node"

    :::python
    ```python
    from langgraph.channels import EphemeralValue
    from langgraph.pregel import Pregel, NodeBuilder

    node1 = (
        NodeBuilder().subscribe_only("a")
        .do(lambda x: x + x)
        .write_to("b")
    )

    app = Pregel(
        nodes={"node1": node1},
        channels={
            "a": EphemeralValue(str),
            "b": EphemeralValue(str),
        },
        input_channels=["a"],
        output_channels=["b"],
    )

    app.invoke({"a": "foo"})
    ```

    ```con
    {'b': 'foofoo'}
    ```
    :::

    :::js
    ```typescript
    import { EphemeralValue } from "@langchain/langgraph/channels";
    import { Pregel, NodeBuilder } from "@langchain/langgraph/pregel";

    const node1 = new NodeBuilder()
      .subscribeOnly("a")
      .do((x: string) => x + x)
      .writeTo("b");

    const app = new Pregel({
      nodes: { node1 },
      channels: {
        a: new EphemeralValue<string>(),
        b: new EphemeralValue<string>(),
      },
      inputChannels: ["a"],
      outputChannels: ["b"],
    });

    await app.invoke({ a: "foo" });
    ```

    ```console
    { b: 'foofoo' }
    ```
    :::

=== "Multiple nodes"

    :::python
    ```python
    from langgraph.channels import LastValue, EphemeralValue
    from langgraph.pregel import Pregel, NodeBuilder

    node1 = (
        NodeBuilder().subscribe_only("a")
        .do(lambda x: x + x)
        .write_to("b")
    )

    node2 = (
        NodeBuilder().subscribe_only("b")
        .do(lambda x: x + x)
        .write_to("c")
    )


    app = Pregel(
        nodes={"node1": node1, "node2": node2},
        channels={
            "a": EphemeralValue(str),
            "b": LastValue(str),
            "c": EphemeralValue(str),
        },
        input_channels=["a"],
        output_channels=["b", "c"],
    )

    app.invoke({"a": "foo"})
    ```

    ```con
    {'b': 'foofoo', 'c': 'foofoofoofoo'}
    ```
    :::

    :::js
    ```typescript
    import { LastValue, EphemeralValue } from "@langchain/langgraph/channels";
    import { Pregel, NodeBuilder } from "@langchain/langgraph/pregel";

    const node1 = new NodeBuilder()
      .subscribeOnly("a")
      .do((x: string) => x + x)
      .writeTo("b");

    const node2 = new NodeBuilder()
      .subscribeOnly("b")
      .do((x: string) => x + x)
      .writeTo("c");

    const app = new Pregel({
      nodes: { node1, node2 },
      channels: {
        a: new EphemeralValue<string>(),
        b: new LastValue<string>(),
        c: new EphemeralValue<string>(),
      },
      inputChannels: ["a"],
      outputChannels: ["b", "c"],
    });

    await app.invoke({ a: "foo" });
    ```

    ```console
    { b: 'foofoo', c: 'foofoofoofoo' }
    ```
    :::

=== "Topic"

    :::python
    ```python
    from langgraph.channels import EphemeralValue, Topic
    from langgraph.pregel import Pregel, NodeBuilder

    node1 = (
        NodeBuilder().subscribe_only("a")
        .do(lambda x: x + x)
        .write_to("b", "c")
    )

    node2 = (
        NodeBuilder().subscribe_to("b")
        .do(lambda x: x["b"] + x["b"])
        .write_to("c")
    )

    app = Pregel(
        nodes={"node1": node1, "node2": node2},
        channels={
            "a": EphemeralValue(str),
            "b": EphemeralValue(str),
            "c": Topic(str, accumulate=True),
        },
        input_channels=["a"],
        output_channels=["c"],
    )

    app.invoke({"a": "foo"})
    ```

    ```pycon
    {'c': ['foofoo', 'foofoofoofoo']}
    ```
    :::

    :::js
    ```typescript
    import { EphemeralValue, Topic } from "@langchain/langgraph/channels";
    import { Pregel, NodeBuilder } from "@langchain/langgraph/pregel";

    const node1 = new NodeBuilder()
      .subscribeOnly("a")
      .do((x: string) => x + x)
      .writeTo("b", "c");

    const node2 = new NodeBuilder()
      .subscribeTo("b")
      .do((x: { b: string }) => x.b + x.b)
      .writeTo("c");

    const app = new Pregel({
      nodes: { node1, node2 },
      channels: {
        a: new EphemeralValue<string>(),
        b: new EphemeralValue<string>(),
        c: new Topic<string>({ accumulate: true }),
      },
      inputChannels: ["a"],
      outputChannels: ["c"],
    });

    await app.invoke({ a: "foo" });
    ```

    ```console
    { c: ['foofoo', 'foofoofoofoo'] }
    ```
    :::

=== "BinaryOperatorAggregate"

    This examples demonstrates how to use the BinaryOperatorAggregate channel to implement a reducer.

    :::python
    ```python
    from langgraph.channels import EphemeralValue, BinaryOperatorAggregate
    from langgraph.pregel import Pregel, NodeBuilder


    node1 = (
        NodeBuilder().subscribe_only("a")
        .do(lambda x: x + x)
        .write_to("b", "c")
    )

    node2 = (
        NodeBuilder().subscribe_only("b")
        .do(lambda x: x + x)
        .write_to("c")
    )

    def reducer(current, update):
        if current:
            return current + " | " + update
        else:
            return update

    app = Pregel(
        nodes={"node1": node1, "node2": node2},
        channels={
            "a": EphemeralValue(str),
            "b": EphemeralValue(str),
            "c": BinaryOperatorAggregate(str, operator=reducer),
        },
        input_channels=["a"],
        output_channels=["c"],
    )

    app.invoke({"a": "foo"})
    ```
    :::

    :::js
    ```typescript
    import { EphemeralValue, BinaryOperatorAggregate } from "@langchain/langgraph/channels";
    import { Pregel, NodeBuilder } from "@langchain/langgraph/pregel";

    const node1 = new NodeBuilder()
      .subscribeOnly("a")
      .do((x: string) => x + x)
      .writeTo("b", "c");

    const node2 = new NodeBuilder()
      .subscribeOnly("b")
      .do((x: string) => x + x)
      .writeTo("c");

    const reducer = (current: string, update: string) => {
      if (current) {
        return current + " | " + update;
      } else {
        return update;
      }
    };

    const app = new Pregel({
      nodes: { node1, node2 },
      channels: {
        a: new EphemeralValue<string>(),
        b: new EphemeralValue<string>(),
        c: new BinaryOperatorAggregate<string>({ operator: reducer }),
      },
      inputChannels: ["a"],
      outputChannels: ["c"],
    });

    await app.invoke({ a: "foo" });
    ```
    :::

=== "Cycle"

    :::python

    This example demonstrates how to introduce a cycle in the graph, by having
    a chain write to a channel it subscribes to. Execution will continue
    until a `None` value is written to the channel.

    ```python
    from langgraph.channels import EphemeralValue
    from langgraph.pregel import Pregel, NodeBuilder, ChannelWriteEntry

    example_node = (
        NodeBuilder().subscribe_only("value")
        .do(lambda x: x + x if len(x) < 10 else None)
        .write_to(ChannelWriteEntry("value", skip_none=True))
    )

    app = Pregel(
        nodes={"example_node": example_node},
        channels={
            "value": EphemeralValue(str),
        },
        input_channels=["value"],
        output_channels=["value"],
    )

    app.invoke({"value": "a"})
    ```

    ```pycon
    {'value': 'aaaaaaaaaaaaaaaa'}
    ```
    :::

    :::js

    This example demonstrates how to introduce a cycle in the graph, by having
    a chain write to a channel it subscribes to. Execution will continue
    until a `null` value is written to the channel.

    ```typescript
    import { EphemeralValue } from "@langchain/langgraph/channels";
    import { Pregel, NodeBuilder, ChannelWriteEntry } from "@langchain/langgraph/pregel";

    const exampleNode = new NodeBuilder()
      .subscribeOnly("value")
      .do((x: string) => x.length < 10 ? x + x : null)
      .writeTo(new ChannelWriteEntry("value", { skipNone: true }));

    const app = new Pregel({
      nodes: { exampleNode },
      channels: {
        value: new EphemeralValue<string>(),
      },
      inputChannels: ["value"],
      outputChannels: ["value"],
    });

    await app.invoke({ value: "a" });
    ```

    ```console
    { value: 'aaaaaaaaaaaaaaaa' }
    ```
    :::

### Source References

- [`put`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L79) (function in langgraph)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14) (class in langgraph)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360) (class in langgraph)
- [`update`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L134) (function in langgraph)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`_On`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/__init__.py#L554) (class in sdk-py)
- [`decorator`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/func/__init__.py#L207) (function in langgraph)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
- [`up`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L3118) (function in langgraph)
