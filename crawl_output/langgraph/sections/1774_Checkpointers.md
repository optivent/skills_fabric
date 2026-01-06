## Checkpointers

::: langgraph.checkpoint.base
    options:
      members:
        - CheckpointMetadata
        - Checkpoint
        - BaseCheckpointSaver
        - create_checkpoint

::: langgraph.checkpoint.serde.base
    options:
      members:
        - SerializerProtocol
        - CipherProtocol

::: langgraph.checkpoint.serde.jsonplus
    options:
      members:
        - JsonPlusSerializer

::: langgraph.checkpoint.serde.encrypted
    options:
      members:
        - EncryptedSerializer

::: langgraph.checkpoint.memory

::: langgraph.checkpoint.sqlite

::: langgraph.checkpoint.sqlite.aio

::: langgraph.checkpoint.postgres
    options:
      members:
        - PostgresSaver

::: langgraph.checkpoint.postgres.aio
    options:
      members:
        - AsyncPostgresSaver

### Source References

- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59) (class in checkpoint)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`json`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L173) (function in sdk-py)
- [`AsyncPostgresSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/aio.py#L32) (class in checkpoint-postgres)
- [`PostgresSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/__init__.py#L32) (class in checkpoint-postgres)
- [`sync`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L556) (function in checkpoint)
- [`CheckpointMetadata`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L31) (class in checkpoint)
- [`BaseCheckpointSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L116) (class in checkpoint)
