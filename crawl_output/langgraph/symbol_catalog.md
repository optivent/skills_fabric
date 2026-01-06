# LangGraph Source Symbol Catalog

Generated: 2026-01-06T10:57:17.448176

Total symbols: 3296

## Symbols by Module

### checkpoint

#### Classes
- [`AsyncBatchedBaseStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/batch.py#L58)
  - Efficiently batch operations in a background task....
- [`BaseCache`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/base/__init__.py#L15)
  - Base class for a cache....
- [`BaseCheckpointSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L116)
  - Base class for creating a graph checkpointer.

Checkpointers allow LangGraph agents to persist their...
- [`BaseStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L700)
  - Abstract base class for persistent key-value stores.

Stores enable persistence and memory that can ...
- [`ChannelProtocol`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/serde/types.py#L22)
- [`CharacterEmbeddings`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/tests/embed_test_utils.py#L11)
  - Simple character-frequency based embeddings using random projections....
- [`Checkpoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L59)
  - State snapshot at a given point in time....
- [`CheckpointMetadata`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L31)
  - Metadata associated with a checkpoint....
- [`CheckpointTuple`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L106)
  - A tuple containing a checkpoint and its associated data....
- [`CipherProtocol`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/serde/base.py#L51)
  - Protocol for encryption and decryption of data.

- `encrypt`: Encrypt plaintext.
- `decrypt`: Decryp...
- [`EmbeddingsLambda`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/embed.py#L109)
  - Wrapper to convert embedding functions into LangChain's Embeddings interface.

This class allows arb...
- [`EmptyChannelError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L379)
  - Raised when attempting to get the value of a channel that hasn't been updated
for the first time yet...
- [`EncryptedSerializer`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/serde/encrypted.py#L8)
  - Serializer that encrypts and decrypts data using an encryption protocol....
- [`GetOp`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L157)
  - Operation to retrieve a specific item by its namespace and key.

This operation allows precise retri...
- [`InMemoryCache`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/memory/__init__.py#L11)
- [`InMemorySaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L31)
  - An in-memory checkpoint saver.

This checkpoint saver stores checkpoints in memory using a `defaultd...
- [`InMemoryStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/memory/__init__.py#L136)
  - In-memory dictionary-backed store with optional vector search.

!!! example "Examples"
    Basic key...
- [`InnerDataclass`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/tests/test_jsonplus.py#L51)
- [`InnerPydantic`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/tests/test_jsonplus.py#L30)
- [`InnerPydanticV1`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/tests/test_jsonplus.py#L40)
- [`InvalidModuleError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/serde/jsonplus.py#L632)
  - Exception raised when a module is not in the allowlist....
- [`InvalidNamespaceError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L541)
  - Provided namespace is invalid....
- [`Item`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L51)
  - Represents a stored item with metadata.

Args:
    value: The stored data as a dictionary. Keys are ...
- [`JsonPlusSerializer`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/serde/jsonplus.py#L41)
  - Serializer that uses ormsgpack, with optional fallbacks.

!!! warning

    Security note: This seria...
- [`ListNamespacesOp`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L368)
  - Operation to list and filter namespaces in the store.

This operation allows exploring the organizat...
- [`MatchCondition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L333)
  - Represents a pattern for matching namespaces in the store.

This class combines a match type (prefix...
- [`MockAsyncBatchedStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/tests/test_store.py#L25)
- [`MockStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/tests/test_store.py#L195)
- [`MyDataclassWSlots`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/tests/test_jsonplus.py#L66)
- [`MyPydantic`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/tests/test_jsonplus.py#L34)
- [`MyPydanticV1`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/tests/test_jsonplus.py#L44)
- [`NotProvided`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L37)
  - Sentinel singleton....
- [`PersistentDict`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L533)
  - Persistent dictionary with an API compatible with shelve and anydbm.

The dict is kept in memory, so...
- [`PutOp`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L431)
  - Operation to store, update, or delete an item in the store.

This class represents a single operatio...
- [`PycryptodomeAesCipher`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/serde/encrypted.py#L65)
- [`RedisCache`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L10)
  - Redis-based cache implementation with TTL support....
- [`SearchItem`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L118)
  - Represents an item returned from a search operation with additional metadata....
- [`SearchOp`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L203)
  - Operation to search for items within a specified namespace hierarchy.

This operation supports both ...
- [`SendProtocol`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/serde/types.py#L42)
- [`SerializerCompat`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/serde/base.py#L29)
- [`SerializerProtocol`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/serde/base.py#L15)
  - Protocol for serialization and deserialization of objects.

- `dumps_typed`: Serialize an object to ...
- [`TestMemorySaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/tests/test_memory.py#L15)
- [`TestRedisCache`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/tests/test_redis_cache.py#L12)
- [`UUID`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/id.py#L15)
  - UUID draft version objects...
- [`UntypedSerializerProtocol`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/serde/base.py#L6)
  - Protocol for serialization and deserialization of objects....

#### Functions
- [`__bool__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L40)
- [`__del__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/batch.py#L70)
- [`_aembed_search_queries`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/memory/__init__.py#L287)
- [`_apply_operator`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/memory/__init__.py#L577)
- [`_apply_put_ops`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/memory/__init__.py#L404)
- [`_batch_search`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/memory/__init__.py#L302)
- [`_check_allowed_modules`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/serde/jsonplus.py#L142)
- [`_check_loop`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/batch.py#L33)
- [`_check_numpy`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/memory/__init__.py#L480)
- [`_compare_values`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/memory/__init__.py#L551)
- [`_cosine_similarity`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/memory/__init__.py#L493)
- [`_dedupe_ops`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/batch.py#L283)
- [`_does_match`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/memory/__init__.py#L525)
- [`_embed_one`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/tests/embed_test_utils.py#L25)
- [`_embed_search_queries`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/memory/__init__.py#L268)
- [`_encode_constructor_args`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/serde/jsonplus.py#L71)
- [`_ensure_refresh`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L1278)
- [`_ensure_task`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/batch.py#L77)
- [`_ensure_ttl`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L1288)
- [`_extract_from_obj`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/embed.py#L252)
- [`_extract_texts`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/memory/__init__.py#L418)
- [`_filter_items`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/memory/__init__.py#L238)
- [`_get_init_embeddings`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/embed.py#L420)
- [`_handle_list_namespaces`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/memory/__init__.py#L460)
- [`_insertinmem_store`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/memory/__init__.py#L446)
- [`_is_async_callable`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/embed.py#L399)
- [`_load_blobs`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/memory/__init__.py#L123)
- [`_make_key`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L31)
- [`_msgpack_default`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/serde/jsonplus.py#L224)
- [`_msgpack_enc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/serde/jsonplus.py#L649)
- [`_msgpack_ext_hook`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/serde/jsonplus.py#L451)
- [`_msgpack_ext_hook_to_json`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/serde/jsonplus.py#L539)
- [`_parse_key`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L36)
- [`_prepare_ops`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/memory/__init__.py#L375)
- [`_revive_lc2`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/serde/jsonplus.py#L109)
- [`_reviver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/serde/jsonplus.py#L92)
- [`_run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/batch.py#L326)
- [`_subsec_decode`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/id.py#L75)
- [`_validate_namespace`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L1255)
- [`abatch`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L737)
- [`aclear`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L141)
- [`adelete`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L1190)
- [`adelete_thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L346)
- [`aembed_documents`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/embed.py#L197)
- [`aembed_query`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/embed.py#L214)
- [`aget`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L252)
- [`alist`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L278)
- [`alist_namespaces`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L1199)
- [`asearch`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L1021)
- [`aset`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L110)
  ... and 90 more functions

### checkpoint-postgres

#### Classes
- [`ANNIndexConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L177)
  - Configuration for vector index in PostgreSQL store....
- [`AsyncPostgresSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/aio.py#L32)
  - Asynchronous checkpointer that stores checkpoints in a Postgres database....
- [`AsyncPostgresStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/aio.py#L42)
  - Asynchronous Postgres-backed store with optional vector search using pgvector.

!!! example "Example...
- [`AsyncShallowPostgresSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/shallow.py#L529)
  - A checkpoint saver that uses Postgres to store checkpoints asynchronously.

This checkpointer ONLY s...
- [`BasePostgresSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/base.py#L156)
- [`BasePostgresStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L235)
- [`HNSWConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L190)
  - Configuration for HNSW (Hierarchical Navigable Small World) index....
- [`IVFFlatConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L200)
  - IVFFlat index divides vectors into lists, and then searches a subset of those lists that are closest...
- [`Migration`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L54)
  - A database migration with optional conditions and parameters....
- [`PoolConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L150)
  - Connection pool settings for PostgreSQL connections.

Controls connection lifecycle and resource uti...
- [`PostgresIndexConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L219)
  - Configuration for vector embeddings in PostgreSQL store with pgvector-specific options.

Extends Emb...
- [`PostgresSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/__init__.py#L32)
  - Checkpointer that stores checkpoints in a Postgres database....
- [`PostgresStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L640)
  - Postgres-backed store with optional vector search using pgvector.

!!! example "Examples"
    Basic ...
- [`Row`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L1163)
- [`ShallowPostgresSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/shallow.py#L169)
  - A checkpoint saver that uses Postgres to store checkpoints.

This checkpointer ONLY stores the most ...

#### Functions
- [`_base_saver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/test_sync.py#L79)
- [`_batch_get_ops`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/aio.py#L446)
- [`_batch_list_namespaces_ops`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/aio.py#L529)
- [`_batch_put_ops`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/aio.py#L465)
- [`_batch_search_ops`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/aio.py#L500)
- [`_create_vector_store`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/test_store.py#L379)
- [`_cursor`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/shallow.py#L824)
- [`_decode_ns_bytes`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L1335)
- [`_dump_blobs`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/shallow.py#L148)
- [`_dump_writes`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/base.py#L239)
- [`_ensure_index_config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L1382)
- [`_exclude_keys`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/test_sync.py#L26)
- [`_execute_batch`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/aio.py#L409)
- [`_get_batch_GET_ops_queries`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L242)
- [`_get_batch_list_namespaces_queries`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L568)
- [`_get_filter_condition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L622)
- [`_get_index_params`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L1210)
- [`_get_vector_type_ops`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L1178)
- [`_get_version`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/aio.py#L236)
- [`_group_ops`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L1314)
- [`_inner_product`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/test_store.py#L766)
- [`_json_loads`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L1323)
- [`_load_checkpoint_tuple`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/__init__.py#L433)
- [`_load_writes`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/base.py#L223)
- [`_migrate_pending_sends`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/base.py#L167)
- [`_namespace_to_text`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L1251)
- [`_neg_l2_distance`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/test_store.py#L780)
- [`_pipe_saver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/test_sync.py#L54)
- [`_pool_saver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/test_sync.py#L31)
- [`_prepare_batch_PUT_queries`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L297)
- [`_prepare_batch_search_queries`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L411)
- [`_row_to_item`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L1260)
- [`_row_to_search_item`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L1288)
- [`_saver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/test_sync.py#L125)
- [`_search_where`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/base.py#L273)
- [`_shallow_saver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/test_sync.py#L102)
- [`_sweep_loop`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/aio.py#L333)
- [`clear_test_db`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/conftest.py#L23)
- [`conn`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/conftest.py#L15)
- [`from_conn_string`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/shallow.py#L571)
- [`get_connection`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/checkpoint/postgres/_internal.py#L14)
- [`get_distance_operator`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L1343)
- [`patched_load_checkpoint_tuple`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/test_sync.py#L351)
- [`start_ttl_sweeper`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/aio.py#L312)
- [`stop_ttl_sweeper`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/aio.py#L358)
- [`store`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/test_store.py#L34)
- [`sweep_ttl`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/aio.py#L296)
- [`test_abatch_order`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/test_async_store.py#L223)
- [`test_basic_store_ops`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/test_store.py#L255)
- [`test_batch_get_ops`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/test_store.py#L147)
  ... and 20 more functions

### checkpoint-sqlite

#### Classes
- [`AsyncSqliteSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/aio.py#L30)
  - An asynchronous checkpoint saver that stores checkpoints in a SQLite database.

This class provides ...
- [`AsyncSqliteStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/langgraph/store/sqlite/aio.py#L39)
  - Asynchronous SQLite-backed store with optional vector search.

This class provides an asynchronous i...
- [`BaseSqliteStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/langgraph/store/sqlite/base.py#L211)
  - Shared base class for SQLite stores....
- [`PreparedGetQuery`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/langgraph/store/sqlite/base.py#L203)
- [`SqliteCache`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/langgraph/cache/sqlite/__init__.py#L13)
  - File-based cache using SQLite....
- [`SqliteIndexConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/langgraph/store/sqlite/base.py#L90)
  - Configuration for vector embeddings in SQLite store....
- [`SqliteSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/__init__.py#L38)
  - A checkpoint saver that stores checkpoints in a SQLite database.

Note:
    This class is meant for ...
- [`SqliteStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/langgraph/store/sqlite/base.py#L707)
  - SQLite-backed store with optional vector search capabilities.

Examples:
    Basic setup and usage:
...
- [`TestAsyncSqliteSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_aiosqlite.py#L15)
- [`TestSqliteSaver`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_sqlite.py#L16)
- [`TestSqliteStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_store.py#L318)

#### Functions
- [`_decode_ns_text`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/langgraph/store/sqlite/base.py#L105)
- [`_metadata_predicate`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/utils.py#L31)
- [`_validate_filter_key`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/utils.py#L14)
- [`_where_value`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/utils.py#L42)
- [`conn_string`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_async_store.py#L71)
- [`create_vector_store`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_store.py#L111)
- [`cursor`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/__init__.py#L162)
- [`search_where`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/langgraph/checkpoint/sqlite/utils.py#L76)
- [`temp_db_file`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_ttl.py#L17)
- [`test_async_asearch_refresh_ttl`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_ttl.py#L370)
- [`test_async_search_with_ttl`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_ttl.py#L340)
- [`test_async_ttl_basic`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_ttl.py#L230)
- [`test_async_ttl_refresh`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_ttl.py#L261)
- [`test_async_ttl_sweeper`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_ttl.py#L301)
- [`test_basic_store_operations`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_store.py#L828)
- [`test_boolean_filter_safety`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_store.py#L1160)
- [`test_checkpoint_search_sql_injection_prevention`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_sqlite.py#L201)
- [`test_filter_keys_with_hyphens_and_digits`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_store.py#L1176)
- [`test_informative_async_errors`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_sqlite.py#L175)
- [`test_limit_parameter_sql_injection_prevention`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_sqlite.py#L247)
- [`test_list_namespaces_operations`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_store.py#L891)
- [`test_metadata_filter_keys_with_hyphens_and_digits`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_sqlite.py#L274)
- [`test_metadata_predicate`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_sqlite.py#L142)
- [`test_metadata_predicate_sql_injection_prevention`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_sqlite.py#L186)
- [`test_numeric_filter_safety`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_store.py#L1119)
- [`test_search_items`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_store.py#L992)
- [`test_search_where`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_sqlite.py#L131)
- [`test_search_with_ttl`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_ttl.py#L201)
- [`test_sql_injection_filter_values`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_store.py#L1072)
- [`test_sql_injection_vulnerability`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_store.py#L1052)
- [`test_ttl_basic`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_ttl.py#L25)
- [`test_ttl_custom_value`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_ttl.py#L129)
- [`test_ttl_override_default`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_ttl.py#L158)
- [`test_ttl_refresh`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_ttl.py#L50)
- [`test_ttl_sweeper`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-sqlite/tests/test_ttl.py#L92)

### cli

#### Classes
- [`AgentContext`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/graphs/agent.py#L21)
- [`AnswerWithCitations`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/graphs/storm.py#L277)
- [`AuthConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L257)
  - Configuration for custom authentication logic and how it integrates into the OpenAPI spec....
- [`CacheConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L236)
- [`CheckpointerConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L162)
  - Configuration for the built-in checkpointer, which handles checkpointing of state.

If omitted, no c...
- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528)
  - Top-level config for langgraph-cli or similar deployment tooling....
- [`ConfigurableHeaderConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L365)
  - Customize which headers to include as configurable values in your runs.

By default, omits x-api-key...
- [`ContextSchema`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/graph_prerelease_reqs/agent.py#L45)
- [`CorsConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L326)
  - Specifies Cross-Origin Resource Sharing (CORS) rules for your server.

If omitted, defaults are typi...
- [`DockerCapabilities`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/docker.py#L25)
- [`Editor`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/graphs/storm.py#L106)
- [`EncryptionConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L305)
  - Configuration for custom at-rest encryption logic.

Allows you to implement custom encryption for se...
- [`HttpConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L392)
  - Configuration for the built-in HTTP server that powers your deployment's routes and endpoints....
- [`IndexConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L31)
  - Configuration for indexing documents for semantic search in the store.

This governs how text is con...
- [`LocalDeps`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L311)
  - A container for referencing and managing local Python dependencies.

A "local dependency" is any ent...
- [`LogData`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/analytics.py#L20)
- [`MyContextMiddleware`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/my_app.py#L24)
- [`Outline`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/graphs/storm.py#L68)
- [`Progress`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/progress.py#L7)
- [`Queries`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/graphs/storm.py#L257)
- [`RelatedSubjects`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/graphs/storm.py#L95)
- [`ResearchState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/graphs/storm.py#L506)
- [`SecurityConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L184)
  - Configuration for OpenAPI security definitions and requirements.

Useful for specifying global or pa...
- [`SerdeConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L123)
  - Configuration for the built-in serde, which handles checkpointing of state.

If omitted, no serde is...
- [`StoreConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L81)
  - Configuration for the built-in long-term memory store.

This store can optionally perform semantic s...
- [`SubSection`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/graphs/storm.py#L425)
- [`Subsection`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/graphs/storm.py#L42)
- [`TTLConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L7)
  - Configuration for TTL (time-to-live) behavior in the store....
- [`ThreadTTLConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L107)
  - Configure a default TTL for checkpointed data within threads....
- [`Version`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/docker.py#L16)
- [`WebhookUrlPolicy`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L488)
- [`WebhooksConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L510)
- [`WikiSection`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/graphs/storm.py#L437)
- [`_Runner`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L18)

#### Functions
- [`Runner`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/exec.py#L12)
- [`_assemble_local_deps`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L369)
- [`_build`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L295)
- [`_calculate_relative_workdir`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L1190)
- [`_choose_template`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/templates.py#L54)
- [`_download_repo_with_requests`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/templates.py#L99)
- [`_extract_env_json`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/tests/unit_tests/test_config.py#L842)
- [`_get_docker_ignore_content`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L432)
- [`_get_node_pm_install_cmd`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L724)
- [`_get_pip_cleanup_lines`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L25)
- [`_get_template_url`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/templates.py#L133)
- [`_image_supports_uv`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L787)
- [`_is_node_graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L93)
- [`_parse_node_version`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L80)
- [`_parse_version`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/docker.py#L32)
- [`_update_auth_path`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L587)
- [`_update_encryption_path`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L628)
- [`_update_graph_paths`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L487)
- [`_update_http_app_path`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L671)
- [`add_descriptions_to_schema`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/generate_schema.py#L35)
- [`as_str`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/graphs/storm.py#L447)
- [`check_capabilities`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/docker.py#L48)
- [`check_reserved`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L389)
- [`clean_empty_lines`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/util.py#L4)
- [`cli`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L164)
- [`compose`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/docker.py#L247)
- [`compose_as_dict`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/docker.py#L138)
- [`conduct_interviews`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/graphs/storm.py#L530)
- [`config_to_compose`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L1238)
- [`config_to_docker`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L1205)
- [`create_new`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/templates.py#L164)
- [`custom_my_route`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/my_app.py#L34)
- [`debugger_compose`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/docker.py#L93)
- [`default_base_image`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L1148)
- [`dev`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L685)
- [`dict_to_yaml`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/docker.py#L117)
- [`disable_analytics_env`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/tests/unit_tests/conftest.py#L8)
- [`dispatch`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/my_app.py#L25)
- [`docker_tag`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L1156)
- [`dockerfile`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/cli.py#L510)
- [`format_conversation`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/graphs/storm.py#L553)
- [`format_doc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/graphs/storm.py#L154)
- [`format_docs`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/graphs/storm.py#L161)
- [`gen_answer`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/examples/graphs/storm.py#L322)
- [`generate_schema`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/generate_schema.py#L133)
- [`get_anonymized_params`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/analytics.py#L29)
- [`get_build_tools_to_uninstall`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L801)
- [`get_common_prefix`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/python-monorepo-example/libs/common/helpers.py#L4)
- [`get_dummy_message`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/python-monorepo-example/libs/shared/src/shared/utils.py#L4)
- [`get_pkg_manager_name`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/config.py#L733)
  ... and 114 more functions

### langgraph

#### Classes
- [`A`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L124)
- [`ANarrow`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L132)
- [`AgentAction`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/agents.py#L8)
  - Represents a request to execute an action by an agent.

The action consists of the name of the tool ...
- [`AgentFinish`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/agents.py#L22)
  - Final return value of an ActionAgent.

Agents return an AgentFinish when they have reached a stoppin...
- [`AgentState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/example_app/example_graph.py#L12)
- [`Analyst`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L3985)
- [`Anode`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L560)
- [`AnyDict`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/any_str.py#L49)
- [`AnyInt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/any_int.py#L1)
- [`AnyObject`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/any_str.py#L8)
- [`AnyStr`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/any_str.py#L33)
- [`AnyValue`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/any_value.py#L15)
  - Stores the last value received, assumes that if multiple values are
received, they are all equal....
- [`AnyVersion`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/any_str.py#L66)
- [`AsyncBackgroundExecutor`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_executor.py#L122)
  - A context manager that runs async tasks in the background.
Uses the current event loop to delegate t...
- [`AsyncFuncCallable`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_utils.py#L51)
- [`AsyncGenCallable`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_utils.py#L86)
- [`AsyncPregelLoop`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_loop.py#L1141)
- [`AsyncQueue`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L12)
  - Async unbounded FIFO queue with a wait() method.

Subclassed from asyncio.Queue, adding a wait() met...
- [`AwhileMaker`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L855)
- [`B`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L128)
- [`BNarrow`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L135)
- [`BackgroundExecutor`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_executor.py#L40)
  - A context manager that runs sync tasks in the background.
Uses a thread pool executor to delegate ta...
- [`BadReducerState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L101)
- [`Bar`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_state.py#L97)
- [`BaseChannel`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/base.py#L19)
  - Base class for all channels....
- [`BaseState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L3761)
- [`BinaryOperatorAggregate`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/binop.py#L41)
  - Stores the result of applying a binary operator to the current value and each new value.

```python
...
- [`BranchSpec`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/_branch.py#L83)
- [`BuiltinTypedDict`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pydantic.py#L46)
- [`CacheKey`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L237)
  - Cache key for a task....
- [`CachePolicy`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L141)
  - Configuration for caching nodes....
- [`Call`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_algo.py#L115)
- [`Cat`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel_async.py#L4123)
- [`ChannelRead`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_read.py#L23)
  - Implements the logic for reading state from CONFIG_KEY_READ.
Usable both as a runnable as well as a ...
- [`ChannelWrite`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_write.py#L46)
  - Implements the logic for sending writes to CONFIG_KEY_SEND.
Can be used as a runnable or as a static...
- [`ChannelWriteEntry`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_write.py#L26)
- [`ChannelWriteTupleEntry`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_write.py#L37)
- [`CheckDurability`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_deprecation.py#L201)
- [`CheckpointPayload`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/debug.py#L54)
- [`CheckpointTask`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/debug.py#L46)
- [`ChildState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L5303)
- [`ChooseAnalyzer`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L2904)
- [`Command`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L364)
  - One or more commands to update the graph's state and send messages to nodes.

Args:
    graph: Graph...
- [`CompiledStateGraph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/state.py#L932)
- [`Context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L1757)
- [`CustomError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_retry.py#L39)
- [`CustomException`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_retry.py#L142)
- [`CustomParentState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4740)
- [`DataclassLike`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_typing.py#L30)
  - Protocol to represent types that behave like dataclasses.

Inspired by the private _DataclassT from ...
- [`DataclassState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5090)
- [`DeprecatedKwargs`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_typing.py#L49)
  - TypedDict to use for extra keyword arguments, enabling type checking warnings for deprecated argumen...
- [`Dog`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel_async.py#L4127)
- [`DummyState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7749)
- [`Edge`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_draw.py#L29)
- [`EmptyInputError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/errors.py#L118)
  - Raised when graph receives an empty input....
- [`EphemeralValue`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/ephemeral_value.py#L15)
  - Stores the value received in the step immediately preceding, clears after....
- [`ErrorCode`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/errors.py#L29)
- [`FakeChatModel`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/fake_chat.py#L14)
- [`FakeFunctionChatModel`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/react_agent.py#L18)
- [`FakeTracer`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/fake_tracer.py#L10)
  - Fake tracer that records LangChain execution.
It replaces run ids with deterministic UUIDs for snaps...
- [`FaultyGetCheckpointer`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L159)
- [`FaultyPutCheckpointer`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L163)
- [`FaultyPutWritesCheckpointer`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L173)
- [`FaultySerializer`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel_async.py#L116)
- [`FaultyVersionCheckpointer`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L179)
- [`FloatBetween`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/any_str.py#L13)
- [`Foo`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6537)
- [`FooState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_state.py#L71)
- [`FunctionNonLocals`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_utils.py#L110)
  - Get the nonlocal variables accessed of a function....
- [`FuturesDict`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_runner.py#L71)
- [`GrandChildState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L5306)
- [`GraphBubbleUp`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/errors.py#L80)
- [`GraphInterrupt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/errors.py#L84)
  - Raised when a subgraph is interrupted, suppressed by the root graph.
Never raised directly, or surfa...
- [`GraphRecursionError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/errors.py#L45)
  - Raised when the graph has exhausted the maximum number of steps.

This prevents infinite loops. To i...
- [`Inner`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6825)
- [`InnerObject`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L2554)
- [`InnerState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L5026)
- [`Input`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L2570)
- [`InputState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L93)
- [`Interrupt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L157)
  - Information about an interrupt that occurred in a node.

!!! version-added "Added in version 0.2.24"...
- [`InterruptOnce`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L4662)
- [`InterviewState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4023)
- [`InvalidUpdateError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/errors.py#L68)
  - Raised when attempting to update a channel with an invalid set of updates.

Troubleshooting guides:
...
- [`IsLastStepManager`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/managed/is_last_step.py#L9)
- [`JokeInput`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/fanout_to_subgraph.py#L69)
- [`JokeOutput`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/fanout_to_subgraph.py#L72)
- [`JokeState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/fanout_to_subgraph.py#L75)
- [`LangGraphDeprecatedSinceV05`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/warnings.py#L50)
  - A specific `LangGraphDeprecationWarning` subclass defining functionality deprecated since LangGraph ...
- [`LangGraphDeprecatedSinceV10`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/warnings.py#L57)
  - A specific `LangGraphDeprecationWarning` subclass defining functionality deprecated since LangGraph ...
- [`LangGraphDeprecationWarning`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/warnings.py#L12)
  - A LangGraph specific deprecation warning.

Attributes:
    message: Description of the warning.
    ...
- [`LastValue`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/last_value.py#L20)
  - Stores the last value received, can receive at most one value per step....
- [`LastValueAfterFinish`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/last_value.py#L81)
  - Stores the last value received, but only made available after finish().
Once made available, clears ...
- [`LazyAtomicCounter`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_algo.py#L1199)
- [`LongPutCheckpointer`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel_async.py#L414)
- [`ManagedValue`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/managed/base.py#L18)
- [`MemorySaverAssertImmutable`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/memory_assert.py#L51)
- [`MemorySaverNeedsPendingSendsMigration`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/memory_assert.py#L29)
- [`MemorySaverNoPending`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/memory_assert.py#L96)
- [`MessageGraph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/message.py#L251)
  - A StateGraph where every node receives a list of messages as input and returns one or more messages ...
- [`MessagesState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/message.py#L307)
- [`MessagesStatePydantic`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_messages_state.py#L180)
- [`MoreState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L3818)
- [`MyBaseTypedDict`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_utils.py#L192)
- [`MyChildDict`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_utils.py#L217)
- [`MyClass`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_utils.py#L169)
- [`MyContextManager`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel_async.py#L223)
- [`MyDataclass`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_utils.py#L254)
- [`MyEnum`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel_async.py#L4137)
- [`MyGrandChildDict`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_utils.py#L222)
- [`MyPydanticModel`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_utils.py#L265)
- [`MyPydanticModelWithAnnotated`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_utils.py#L276)
- [`MyState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L556)
- [`MyTypedDict`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_utils.py#L242)
- [`NamedBarrierValue`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L13)
  - A channel that waits until all named values are received before making the value available....
- [`NamedBarrierValueAfterFinish`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L84)
  - A channel that waits until all named values are received before making the value ready to be made av...
- [`NestedModel`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel_async.py#L4112)
- [`Node`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L4671)
- [`Node2State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_state.py#L319)
- [`NodeBuilder`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L160)
- [`NodeInterrupt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/errors.py#L96)
  - Raised by a node to interrupt execution....
- [`NodeName`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4309)
- [`NonLocals`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_utils.py#L159)
  - Get nonlocal variables accessed....
- [`NoopSerializer`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/memory_assert.py#L21)
- [`NotACheckpointer`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L132)
- [`NotAllowed`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L86)
- [`OtherSubgraphState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6401)
- [`Output`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6360)
- [`OutputState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_state.py#L152)
- [`OverallState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/fanout_to_subgraph.py#L62)
- [`Overwrite`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L543)
  - Bypass a reducer and write the wrapped value directly to a `BinaryOperatorAggregate` channel.

Recei...
- [`ParentCommand`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/errors.py#L111)
- [`ParentState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7331)
- [`Person`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel_async.py#L4132)
- [`Perspectives`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4004)
- [`PlainState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_deprecation.py#L21)
- [`Pregel`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L324)
  - Pregel manages the runtime behavior for LangGraph applications.

## Overview

Pregel combines [**act...
- [`PregelExecutableTask`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L249)
- [`PregelLoop`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_loop.py#L140)
- [`PregelNode`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_read.py#L95)
  - A node in a Pregel graph. This won't be invoked as a runnable by the graph
itself, but instead acts ...
- [`PregelProtocol`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/protocol.py#L17)
- [`PregelRunner`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_runner.py#L122)
  - Responsible for executing a set of Pregel tasks concurrently, committing
their writes, yielding cont...
- [`PregelScratchpad`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_scratchpad.py#L9)
- [`PregelTask`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L219)
  - A Pregel task....
- [`PregelTaskWrites`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_algo.py#L105)
  - Simplest implementation of WritesProtocol, for usage with writes that
don't originate from a runnabl...
- [`PrivateState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_state.py#L280)
- [`PydanticModel`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pydantic.py#L54)
- [`PydanticState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5086)
- [`QueryModel`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L2557)
- [`Qux`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6560)
- [`RecursiveModel`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel_async.py#L4118)
- [`RemainingStepsManager`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/managed/is_last_step.py#L18)
- [`RemoteException`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/remote.py#L102)
  - Exception raised when an error occurs in the remote graph....
- [`RemoteGraph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/remote.py#L108)
  - The `RemoteGraph` class is a client implementation for calling remote
APIs that implement the LangGr...
- [`RemoveUIMessage`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/ui.py#L43)
  - A message type for removing UI components in LangGraph.

This TypedDict represents a message that ca...
- [`ResearchGraphState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4028)
- [`RetryPolicy`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L115)
  - Configuration for retrying nodes.

!!! version-added "Added in version 0.2.24"...
- [`RouterState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L6497)
- [`RunnableCallable`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L254)
  - A much simpler version of RunnableLambda that requires sync and async functions....
- [`RunnableSeq`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L535)
  - Sequence of `Runnable`, where the output of each is the input of the next.

`RunnableSeq` is a simpl...
- [`Runtime`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/runtime.py#L28)
  - Convenience class that bundles run-scoped context and other runtime utilities.

!!! version-added "A...
- [`Section`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L4009)
- [`Semaphore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L44)
  - Semaphore subclass with a wait() method....
- [`Send`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L285)
  - A message or packet to send to a specific node in the graph.

The `Send` class is used within a `Sta...
- [`SimpleGraphState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L7099)
- [`SomeCustomState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L8322)
- [`SomeParentState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_state.py#L140)
- [`State`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/bench/wide_dict.py#L14)
- [`State2`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_state.py#L28)
- [`StateForA`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L264)
- [`StateForB`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L274)
- [`StateForC`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L287)
- [`StateGraph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/state.py#L112)
  - A graph whose nodes communicate by reading and writing to a shared state.

The signature of each nod...
- [`StateNodeSpec`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/_node.py#L85)
- [`StateNotRequired`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_managed_values.py#L11)
- [`StatePlain`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_managed_values.py#L7)
- [`StateRequired`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_managed_values.py#L15)
- [`StateSnapshot`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L264)
  - Snapshot of the state of the graph at the beginning of a step....
- [`StateUpdate`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L213)
- [`StrEnum`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L121)
  - A string enum....
- [`StreamMessagesHandler`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_messages.py#L29)
  - A callback handler that implements stream_mode=messages.

Collects messages from:
(1) chat model str...
- [`StreamProtocol`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/protocol.py#L151)
- [`SubGraphState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L6474)
- [`SubgraphState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L4477)
- [`Submit`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_executor.py#L27)
- [`SyncAsyncFuture`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_call.py#L248)
- [`SyncFuncCallable`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_utils.py#L60)
- [`SyncGenCallable`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_utils.py#L95)
- [`SyncPregelLoop`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_loop.py#L965)
- [`SyncQueue`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L70)
  - Unbounded FIFO queue with a wait() method.
Adapted from pure Python implementation of queue.SimpleQu...
- [`TaskNotFound`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/errors.py#L124)
  - Raised when the executor is unable to find a task (for distributed mode)....
- [`TaskPayload`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/debug.py#L31)
- [`TaskResultPayload`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/debug.py#L38)
- [`ToolOutputMixin`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L38)
- [`ToolState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_large_cases.py#L495)
- [`Topic`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/topic.py#L23)
  - A configurable PubSub Topic.

Args:
    typ: The type of the value stored in the channel.
    accumu...
- [`TriggerEdge`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_draw.py#L36)
- [`TypedDictExtensions`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pydantic.py#L36)
- [`TypedDictLikeV1`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_typing.py#L12)
  - Protocol to represent types that behave like TypedDicts

Version 1: using `ClassVar` for keys....
- [`TypedDictLikeV2`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_typing.py#L21)
  - Protocol to represent types that behave like TypedDicts

Version 2: not using `ClassVar` for keys....
- [`TypedDictState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_type_checking.py#L15)
- [`UIMessage`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/ui.py#L22)
  - A message type for UI updates in LangGraph.

This TypedDict represents a UI message that can be sent...
- [`UnserializableResource`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L8655)
- [`UnsortedSequence`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/any_str.py#L77)
- [`UntrackedValue`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/untracked_value.py#L15)
  - Stores the last value received, never checkpointed....
- [`UpdateDocs34`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L2437)
- [`UserRole`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pydantic.py#L72)
- [`VanillaClass`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pydantic.py#L41)
- [`WritesProtocol`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_algo.py#L88)
  - Protocol for objects containing writes to be applied to checkpoint.
Implemented by PregelTaskWrites ...
- [`_Node`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/_node.py#L16)
- [`_NodeWithConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/_node.py#L20)
- [`_NodeWithConfigStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/_node.py#L44)
- [`_NodeWithConfigWriter`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/_node.py#L38)
- [`_NodeWithConfigWriterStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/_node.py#L50)
- [`_NodeWithRuntime`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/_node.py#L61)
- [`_NodeWithStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/_node.py#L28)
- [`_NodeWithWriter`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/_node.py#L24)
- [`_NodeWithWriterStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/_node.py#L32)
- [`_RunnableWithConfigStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L226)
- [`_RunnableWithConfigWriter`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L220)
- [`_RunnableWithConfigWriterStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L232)
- [`_RunnableWithStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L210)
- [`_RunnableWithWriter`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L206)
- [`_RunnableWithWriterStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L214)
- [`_RuntimeOverrides`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/runtime.py#L20)
- [`_TaskFunction`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/func/__init__.py#L46)
- [`_TaskIDFn`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_algo.py#L496)
- [`entrypoint`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/func/__init__.py#L228)
  - Define a LangGraph workflow using the `entrypoint` decorator.

### Function signature

The decorated...
- [`final`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/func/__init__.py#L431)
  - A primitive that can be returned from an entrypoint.

This primitive allows to save a value to the c...
- [`monotonic_uid`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_remote_graph.py#L1173)

#### Functions
- [`DuplexStream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_loop.py#L131)
- [`InputType`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L864)
- [`OutputType`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L891)
- [`UpdateType`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L112)
- [`ValueType`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L107)
- [`_AnyIdAIMessage`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/messages.py#L25)
- [`_AnyIdAIMessageChunk`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/messages.py#L32)
- [`_AnyIdDocument`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/messages.py#L18)
- [`_AnyIdHumanMessage`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/messages.py#L39)
- [`_AnyIdToolMessage`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/messages.py#L46)
- [`__aenter__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_executor.py#L183)
- [`__aexit__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_executor.py#L186)
- [`__await__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_call.py#L249)
- [`__call__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/func/__init__.py#L471)
- [`__enter__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_executor.py#L90)
- [`__eq__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L100)
- [`__exit__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_executor.py#L93)
- [`__getattr__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/constants.py#L34)
- [`__getattribute__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/memory_assert.py#L33)
- [`__hash__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/types.py#L346)
- [`__init__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L94)
- [`__new__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/any_str.py#L14)
- [`__or__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L573)
- [`__repr__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L321)
- [`__ror__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_runnable.py#L598)
- [`__setitem__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_runner.py#L94)
- [`__str__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/warnings.py#L42)
- [`_acall`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_runner.py#L620)
- [`_acall_impl`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_runner.py#L673)
- [`_add_messages`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/message.py#L42)
- [`_add_messages_wrapper`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/message.py#L41)
- [`_add_schema`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/state.py#L257)
- [`_all_edges`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/state.py#L252)
- [`_aprepare_state_snapshot`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/main.py#L1115)
- [`_aread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_read.py#L66)
- [`_aroute`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/graph/_branch.py#L169)
- [`_assemble_writes`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_write.py#L172)
- [`_astream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/fake_chat.py#L101)
- [`_awrite`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_write.py#L90)
- [`_call`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/pregel/_runner.py#L533)
- [`_call_check_cancel`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_future.py#L106)
- [`_call_set_state`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_future.py#L113)
- [`_chain_future`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_future.py#L82)
- [`_checkpointer_memory`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/conftest_checkpointer.py#L24)
- [`_checkpointer_memory_migrate_sends`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/conftest_checkpointer.py#L29)
- [`_checkpointer_postgres`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/conftest_checkpointer.py#L49)
- [`_checkpointer_postgres_aio`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/conftest_checkpointer.py#L116)
- [`_checkpointer_postgres_aio_pipe`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/conftest_checkpointer.py#L139)
- [`_checkpointer_postgres_aio_pool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/conftest_checkpointer.py#L165)
- [`_checkpointer_postgres_pipe`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/conftest_checkpointer.py#L68)
  ... and 948 more functions

### prebuilt

#### Classes
- [`ActionRequest`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/interrupt.py#L33)
  - Represents a request for human action within the graph execution.

Contains the action type and any ...
- [`AgentStateExtraKey`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L781)
- [`AgentStateExtraKeyPydantic`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L785)
- [`AgentStatePydantic`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L69)
  - The state of the agent....
- [`AgentStateWithStructuredResponse`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L88)
  - The state of the agent with a structured response....
- [`AgentStateWithStructuredResponsePydantic`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L105)
  - The state of the agent with a structured response....
- [`CallModelInputSchema`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L726)
- [`ComprehensiveToolSchema`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_tool_node.py#L1808)
- [`CustomAgentState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1863)
- [`CustomAgentStateAsync`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1894)
- [`CustomDynamicState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1663)
- [`CustomState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L525)
- [`CustomStatePydantic`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L529)
- [`CustomToolSchema`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_tool_node.py#L955)
- [`FakeToolCallingModel`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/model.py#L22)
- [`FlagState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1958)
- [`Handler`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L446)
- [`HumanInterrupt`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/interrupt.py#L51)
  - Represents an interrupt triggered by the graph that requires human intervention.

This is passed to ...
- [`HumanInterruptConfig`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/interrupt.py#L11)
  - Configuration that defines what actions are allowed for a human interrupt.

This controls the availa...
- [`HumanResponse`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/interrupt.py#L87)
  - The response provided by a human to an interrupt, which is returned when graph execution resumes.

A...
- [`InjectedState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1584)
  - Annotation for injecting graph state into tool arguments.

This annotation enables tools to access g...
- [`InjectedStore`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1660)
  - Annotation for injecting persistent store into tool arguments.

This annotation enables tools to acc...
- [`MyCustomTool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_tool_node.py#L958)
- [`MyModelV1`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_validation_node.py#L24)
- [`ResponseFormat`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent_graph.py#L28)
  - Response format for the agent....
- [`TestResponse`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1725)
- [`TestState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_tool_node.py#L1803)
- [`ToolCallRequest`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L127)
  - Tool execution request passed to tool call interceptors.

Attributes:
    tool_call: Tool call dict ...
- [`ToolCallWithContext`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L276)
  - ToolCall with additional context for graph state.

This is an internal data structure meant to help ...
- [`ToolInvocationError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L329)
  - An error occurred while invoking a tool due to invalid arguments.

This exception is only raised whe...
- [`ToolNode`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L610)
  - A node for executing tools in LangGraph workflows.

Handles tool execution patterns including functi...
- [`ToolRuntime`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1525)
  - Runtime context automatically injected into tools.

When a tool function has a parameter named `tool...
- [`ValidationNode`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_validator.py#L47)
  - A node that validates all tools requests from the last `AIMessage`.

It can be used either in `State...
- [`WeatherResponse`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1994)
- [`_InjectStateSchema`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_tool_node.py#L1304)
- [`_InjectedArgs`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L557)
  - Internal structure for tracking injected arguments for a tool.

This data structure is built once du...
- [`_InjectedStateDataclassSchema`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_tool_node.py#L1315)
- [`_InjectedStatePydanticSchema`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_tool_node.py#L1328)
- [`_InjectedStatePydanticV2Schema`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_tool_node.py#L1309)
- [`_ToolCallRequestOverrides`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L120)
  - Possible overrides for ToolCallRequest.override() method....

#### Functions
- [`__setattr__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L145)
- [`_afunc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L813)
- [`_are_more_steps_needed`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L609)
- [`_aresolve_model`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L597)
- [`_arun`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_tool_node.py#L971)
- [`_arun_one`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1139)
- [`_combine_tool_outputs`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L844)
- [`_create_config_with_runtime`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_tool_node.py#L69)
- [`_create_mock_runtime`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_tool_node.py#L55)
- [`_default_format_error`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_validator.py#L34)
- [`_default_handle_tool_errors`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L373)
- [`_execute_tool_async`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1041)
- [`_execute_tool_sync`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L888)
- [`_extract_state`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1259)
- [`_filter_validation_errors`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L500)
- [`_func`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_validator.py#L184)
- [`_get_all_injected_args`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1792)
- [`_get_injection_from_type`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1762)
- [`_get_message`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_validator.py#L168)
- [`_get_model`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L215)
- [`_get_model_input_state`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L625)
- [`_get_prompt_runnable`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L132)
- [`_get_state_value`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L124)
- [`_handle_tool_error`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L384)
- [`_infer_handled_types`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L434)
- [`_inject_tool_args`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1274)
- [`_is_injection`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1735)
- [`_llm_type`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/model.py#L49)
- [`_parse_input`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1202)
- [`_resolve_model`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L588)
- [`_run_one`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L986)
- [`_should_bind_tools`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L168)
- [`_sync_execute`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1178)
- [`_validate_chat_history`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L238)
- [`_validate_tool_call`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1246)
- [`_validate_tool_command`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/tool_node.py#L1371)
- [`acall_model`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L685)
- [`addition`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1129)
- [`advanced_tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1586)
- [`agenerate_structured_response`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/langgraph/prebuilt/chat_agent_executor.py#L758)
- [`async_add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_on_tool_call.py#L362)
- [`async_interceptor`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_tool_node_interceptor_unregistered.py#L113)
- [`async_transfer_to_bob`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_tool_node.py#L945)
- [`bad_handler`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_on_tool_call.py#L211)
- [`bad_interceptor`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_tool_node_interceptor_unregistered.py#L175)
- [`basic_tool`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_react_agent.py#L1581)
- [`capturing_interceptor`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_tool_node_interceptor_unregistered.py#L517)
- [`check_results`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_validation_node.py#L78)
- [`command_handler`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_on_tool_call.py#L1042)
- [`command_inspector_handler`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/prebuilt/tests/test_on_tool_call.py#L1080)
  ... and 185 more functions

### sdk-py

#### Classes
- [`APIConnectionError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L96)
- [`APIError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L17)
- [`APIResponseValidationError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L62)
- [`APIStatusError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L82)
- [`APITimeoutError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L103)
- [`Assistant`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L242)
  - Represents an assistant with additional properties....
- [`AssistantBase`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L213)
  - Base model for an assistant....
- [`AssistantVersion`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L236)
  - Represents a specific version of an assistant....
- [`AssistantsClient`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L614)
  - Client for managing assistants in LangGraph.

This class provides methods to interact with assistant...
- [`AssistantsCreate`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L590)
  - Payload for creating an assistant.

???+ example "Examples"

    ```python
    create_params = {
   ...
- [`AssistantsDelete`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L689)
  - Payload for deleting an assistant.

???+ example "Examples"

    ```python
    delete_params = {
   ...
- [`AssistantsRead`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L629)
  - Payload for reading an assistant.

???+ example "Examples"

    ```python
    read_params = {
      ...
- [`AssistantsSearch`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L705)
  - Payload for searching assistants.

???+ example "Examples"

    ```python
    search_params = {
    ...
- [`AssistantsSearchResponse`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L249)
  - Paginated response for assistant search results....
- [`AssistantsUpdate`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L649)
  - Payload for updating an assistant.

???+ example "Examples"

    ```python
    update_params = {
   ...
- [`AsyncListByteStream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_client_stream.py#L17)
- [`Auth`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/__init__.py#L13)
  - Add custom authentication and authorization management to your LangGraph application.

The Auth clas...
- [`AuthContext`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L383)
  - Complete authentication context with resource and action information.

Extends BaseAuthContext with ...
- [`AuthenticationError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L112)
- [`BadRequestError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L108)
- [`BaseAuthContext`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L367)
  - Base class for authentication context.

Provides the fundamental authentication information needed f...
- [`BaseUser`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L182)
  - The base ASGI user protocol...
- [`BytesLineDecoder`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/sse.py#L17)
  - Handles incrementally reading lines from text.

Has the same behaviour as the stdllib bytes splitlin...
- [`ConflictError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L124)
- [`Cron`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L348)
  - Represents a scheduled task....
- [`CronClient`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L2942)
  - Client for managing recurrent runs (cron jobs) in LangGraph.

A run is a single invocation of an ass...
- [`CronsCreate`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L733)
  - Payload for creating a cron job.

???+ example "Examples"

    ```python
    create_params = {
     ...
- [`CronsDelete`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L769)
  - Payload for deleting a cron job.

???+ example "Examples"

    ```python
    delete_params = {
     ...
- [`CronsRead`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L785)
  - Payload for reading a cron job.

???+ example "Examples"

    ```python
    read_params = {
        ...
- [`CronsSearch`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L825)
  - Payload for searching cron jobs.

???+ example "Examples"

    ```python
    search_params = {
     ...
- [`CronsUpdate`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L801)
  - Payload for updating a cron job.

???+ example "Examples"

    ```python
    update_params = {
     ...
- [`DuplicateHandlerError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L35)
  - Raised when attempting to register a duplicate encryption/decryption handler....
- [`Encryption`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L201)
  - Add custom at-rest encryption to your LangGraph application.

.. warning::
    This API is in beta a...
- [`EncryptionContext`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/types.py#L17)
  - Context passed to encryption/decryption handlers.

Contains arbitrary non-secret key-values that wil...
- [`GraphSchema`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L188)
  - Defines the structure and properties of a graph....
- [`HTTPException`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/exceptions.py#L9)
  - HTTP exception that you can raise to return a specific HTTP error response.

Since this is defined i...
- [`HttpClient`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L329)
  - Handle async requests to the LangGraph API.

Adds additional error messaging & content handling abov...
- [`InternalServerError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L136)
- [`LangGraphBetaWarning`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L22)
  - Warning for beta features in LangGraph SDK....
- [`LangGraphClient`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L291)
  - Top-level client for LangGraph API.

Attributes:
    assistants: Manages versioned configuration for...
- [`LangGraphError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L13)
- [`ListByteStream`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_client_stream.py#L32)
- [`ListNamespaceResponse`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L490)
  - Response structure for listing namespaces....
- [`MinimalUser`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L151)
  - User objects must at least expose the identity property....
- [`MinimalUserDict`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L164)
  - The dictionary representation of a user....
- [`MyModel`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L16)
- [`NotFoundError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L120)
- [`PermissionDeniedError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L116)
- [`RateLimitError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L132)
- [`Run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L327)
  - Represents a single execution run....
- [`RunCreate`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L442)
  - Defines the parameters for initiating a background run....
- [`RunCreateMetadata`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L568)
  - Metadata for a run creation request....
- [`RunsClient`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L1959)
  - Client for managing runs in LangGraph.

A run is a single assistant invocation with optional input, ...
- [`RunsCreate`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L534)
  - Payload for creating a run.

???+ example "Examples"

    ```python
    create_params = {
        "a...
- [`SSEDecoder`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/sse.py#L78)
- [`SearchItemsResponse`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L508)
  - Response structure for searching items....
- [`StoreClient`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3270)
  - Client for interacting with the graph's shared storage.

The Store provides a key-value storage syst...
- [`StoreDelete`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L921)
  - Operation to delete an item from the store....
- [`StoreGet`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L853)
  - Operation to retrieve a specific item by its namespace and key....
- [`StoreListNamespaces`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L882)
  - Operation to list and filter namespaces in the store....
- [`StorePut`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L905)
  - Operation to store, update, or delete an item in the store....
- [`StoreSearch`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L863)
  - Operation to search for items within a specified namespace hierarchy....
- [`StreamPart`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L515)
  - Represents a part of a stream response....
- [`StudioUser`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L218)
  - A user object that's populated from authenticated requests from the LangGraph studio.

Note: Studio ...
- [`SyncAssistantsClient`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3955)
  - Client for managing assistants in LangGraph synchronously.

This class provides methods to interact ...
- [`SyncCronClient`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L6244)
  - Synchronous client for managing cron jobs in LangGraph.

This class provides methods to create and m...
- [`SyncHttpClient`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3678)
  - Handle synchronous requests to the LangGraph API.

Provides error messaging and content handling enh...
- [`SyncLangGraphClient`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3637)
  - Synchronous client for interacting with the LangGraph API.

This class provides synchronous access t...
- [`SyncRunsClient`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L5279)
  - Synchronous client for managing runs in LangGraph.

This class provides methods to create, retrieve,...
- [`SyncStoreClient`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L6559)
  - A client for synchronous operations on a key-value store.

Provides methods to interact with a remot...
- [`SyncThreadsClient`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L4648)
  - Synchronous client for managing threads in LangGraph.

This class provides methods to create, retrie...
- [`TestDataClass`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde.py#L42)
- [`TestHandlerValidation`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_encryption.py#L6)
  - Test duplicate handler and signature validation....
- [`TestModel`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde.py#L58)
- [`TestSkipAutoLoadApiKey`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_skip_auto_load_api_key.py#L8)
  - Test the api_key parameter's auto-loading behavior....
- [`Thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L267)
  - Represents a conversation thread....
- [`ThreadState`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L298)
  - Represents the state of a thread....
- [`ThreadTTL`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L420)
  - Time-to-live configuration for a thread.

Matches the OpenAPI schema where TTL is represented as an ...
- [`ThreadTask`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L286)
  - Represents a task within a thread....
- [`ThreadUpdateStateResponse`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L320)
  - Represents the response from updating a thread's state....
- [`ThreadsClient`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L1311)
  - Client for managing threads in LangGraph.

A thread maintains the state of a graph across multiple i...
- [`ThreadsCreate`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L434)
  - Parameters for creating a new thread.

???+ example "Examples"

    ```python
    create_params = {
...
- [`ThreadsDelete`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L493)
  - Parameters for deleting a thread.

Called for deletes to a thread, thread version, or run...
- [`ThreadsRead`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L461)
  - Parameters for reading thread state or run information.

This type is used in three contexts:
1. Rea...
- [`ThreadsSearch`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L506)
  - Parameters for searching threads.

Called for searches to threads or runs....
- [`ThreadsUpdate`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L476)
  - Parameters for updating a thread or run.

Called for updates to a thread, thread version, or run
can...
- [`UnprocessableEntityError`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L128)
- [`_ActionHandler`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/__init__.py#L273)
- [`_AssistantsOn`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/__init__.py#L404)
- [`_BaseModelLike`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L605)
  - Protocol to represent types that behave like Pydantic `BaseModel`....
- [`_CronsOn`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/__init__.py#L462)
- [`_DataclassLike`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L596)
  - Protocol to represent types that behave like dataclasses.

Inspired by the private _DataclassT from ...
- [`_DecryptDecorators`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L134)
  - Decorators for decryption handlers.

Provides @encryption.decrypt.blob and @encryption.decrypt.json ...
- [`_EncryptDecorators`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L67)
  - Decorators for encryption handlers.

Provides @encryption.encrypt.blob and @encryption.encrypt.json ...
- [`_On`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/__init__.py#L554)
  - Entry point for authorization handlers that control access to specific resources.

The _On class pro...
- [`_ResourceActionOn`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/__init__.py#L282)
- [`_ResourceOn`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/__init__.py#L310)
  - Generic base class for resource-specific handlers....
- [`_StoreOn`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/__init__.py#L486)
- [`_ThreadsOn`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/__init__.py#L427)
- [`_TypedDictLikeV1`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L578)
  - Protocol to represent types that behave like TypedDicts

Version 1: using `ClassVar` for keys....
- [`_TypedDictLikeV2`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/schema.py#L587)
  - Protocol to represent types that behave like TypedDicts

Version 2: not using `ClassVar` for keys....
- [`assistants`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L998)
  - Types for assistant-related operations....
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039)
  - Type for cron creation parameters....
- [`create_run`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L973)
  - Type for creating or streaming a run....
- [`crons`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1034)
  - Types for cron-related operations....
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931)
  - Namespace for type definitions of different API operations.

This class organizes type definitions f...
- [`read`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1044)
  - Type for cron read parameters....
- [`threads`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L961)
  - Types for thread-related operations....

#### Functions
- [`__aiter__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_client_stream.py#L22)
- [`__contains__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L209)
- [`__getitem__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L205)
- [`__iter__`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L213)
- [`_adecode_error_body`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L158)
- [`_adecode_json`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L605)
- [`_aencode_json`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L589)
- [`_araise_for_status_typed`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L213)
- [`_assistant_payload`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_assistants_client.py#L14)
- [`_decode_error_body`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L174)
- [`_decode_json`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3950)
- [`_encode_json`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3938)
- [`_enum_from_query_select`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_select_fields_sync.py#L49)
- [`_enum_from_request_select`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_select_fields_sync.py#L31)
- [`_extract_error_message`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L140)
- [`_get_api_key`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L88)
- [`_get_headers`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L113)
- [`_get_run_metadata_from_response`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L162)
- [`_load_spec`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_select_fields_sync.py#L18)
- [`_map_status_error`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L190)
- [`_normalize_return_annotation`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_api_parity.py#L40)
- [`_orjson_default`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L134)
- [`_provided_vals`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L6857)
- [`_public_methods`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_api_parity.py#L22)
- [`_raise_for_status_typed`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/errors.py#L224)
- [`_register_handler`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/__init__.py#L687)
- [`_serde_roundtrip`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde.py#L10)
- [`_strip_self`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_api_parity.py#L33)
- [`_validate_handler`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L41)
- [`_warn_encryption_beta`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L27)
- [`aclose`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L323)
- [`aiter_lines_raw`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/sse.py#L142)
- [`authenticate`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/__init__.py#L189)
- [`blob`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L144)
- [`blob_dec`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_encryption.py#L18)
- [`blob_enc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_encryption.py#L14)
- [`cancel`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L6056)
- [`capture_pagination`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L4511)
- [`configure_loopback_transports`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L6865)
- [`context`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L387)
- [`count`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L6530)
- [`create_batch`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L5745)
- [`create_for_thread`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L6266)
- [`decode`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/sse.py#L91)
- [`delete_item`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L6685)
- [`display_name`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L258)
- [`dup`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_encryption.py#L51)
- [`filter_payload`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L5754)
- [`flush`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/sse.py#L68)
- [`get_asgi_transport`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L6871)
  ... and 64 more functions
