## 3. Test your bot

Start the server again to test everything out:

```bash
langgraph dev --no-browser
```

If you didn't add the `--no-browser`, the studio UI will open in the browser. You may wonder, how is the studio able to still connect to our server? By default, we also permit access from the LangGraph studio, even when using custom auth. This makes it easier to develop and test your bot in the studio. You can remove this alternative authentication option by setting `disable_studio_auth: "true"` in your auth configuration:

:::python

```json
{
  "auth": {
    "path": "src/security/auth.py:auth",
    "disable_studio_auth": "true"
  }
}
```

:::

:::js

```json
{
  "auth": {
    "path": "src/security/auth.ts:auth",
    "disable_studio_auth": "true"
  }
}
```

:::

### Source References

- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`add`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L6331) (function in langgraph)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
- [`Auth`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/__init__.py#L13) (class in sdk-py)
- [`json`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/encryption/__init__.py#L173) (function in sdk-py)
- [`set`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/cache/redis/__init__.py#L84) (function in checkpoint)
- [`conn`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/tests/conftest.py#L15) (function in checkpoint-postgres)
- [`Row`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint-postgres/langgraph/store/postgres/base.py#L1163) (class in checkpoint-postgres)
- [`graph`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/tests/test_pregel.py#L5995) (function in langgraph)
