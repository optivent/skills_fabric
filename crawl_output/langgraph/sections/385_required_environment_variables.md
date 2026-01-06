## required environment variables

CONTROL_PLANE_HOST = os.getenv("CONTROL_PLANE_HOST")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
INTEGRATION_ID = os.getenv("INTEGRATION_ID")
MAX_WAIT_TIME = 1800  # 30 mins


def get_headers() -> dict:
    """Return common headers for requests to LangGraph Control Plane API."""
    return {
        "X-Api-Key": LANGSMITH_API_KEY,
    }


def create_deployment() -> str:
    """Create deployment. Return deployment ID."""
    headers = get_headers()
    headers["Content-Type"] = "application/json"

    deployment_name = "my_deployment"

    request_body = {
        "name": deployment_name,
        "source": "github",
        "source_config": {
            "integration_id": INTEGRATION_ID,
            "repo_url": "https://github.com/langchain-ai/langgraph-example",
            "deployment_type": "dev",
            "build_on_push": False,
            "custom_url": None,
            "resource_spec": None,
        },
        "source_revision_config": {
            "repo_ref": "main",
            "langgraph_config_path": "langgraph.json",
            "image_uri": None,
        },
        "secrets": [
            {
                "name": "OPENAI_API_KEY",
                "value": "test_openai_api_key",
            },
            {
                "name": "ANTHROPIC_API_KEY",
                "value": "test_anthropic_api_key",
            },
            {
                "name": "TAVILY_API_KEY",
                "value": "test_tavily_api_key",
            },
        ],
    }

    response = requests.post(
        url=f"{CONTROL_PLANE_HOST}/v2/deployments",
        headers=headers,
        json=request_body,
    )

    if response.status_code != 201:
        raise Exception(f"Failed to create deployment: {response.text}")

    deployment_id = response.json()["id"]
    print(f"Created deployment {deployment_name} ({deployment_id})")
    return deployment_id


def get_deployment(deployment_id: str) -> dict:
    """Get deployment."""
    response = requests.get(
        url=f"{CONTROL_PLANE_HOST}/v2/deployments/{deployment_id}",
        headers=get_headers(),
    )

    if response.status_code != 200:
        raise Exception(f"Failed to get deployment ID {deployment_id}: {response.text}")

    return response.json()


def list_revisions(deployment_id: str) -> list[dict]:
    """List revisions.

    Return list is sorted by created_at in descending order (latest first).
    """
    response = requests.get(
        url=f"{CONTROL_PLANE_HOST}/v2/deployments/{deployment_id}/revisions",
        headers=get_headers(),
    )

    if response.status_code != 200:
        raise Exception(
            f"Failed to list revisions for deployment ID {deployment_id}: {response.text}"
        )

    return response.json()


def get_revision(
    deployment_id: str,
    revision_id: str,
) -> dict:
    """Get revision."""
    response = requests.get(
        url=f"{CONTROL_PLANE_HOST}/v2/deployments/{deployment_id}/revisions/{revision_id}",
        headers=get_headers(),
    )

    if response.status_code != 200:
        raise Exception(f"Failed to get revision ID {revision_id}: {response.text}")

    return response.json()


def patch_deployment(deployment_id: str) -> None:
    """Patch deployment."""
    headers = get_headers()
    headers["Content-Type"] = "application/json"

    response = requests.patch(
        url=f"{CONTROL_PLANE_HOST}/v2/deployments/{deployment_id}",
        headers=headers,
        json={
            "source_config": {
                "build_on_push": True,
            },
            "source_revision_config": {
                "repo_ref": "main",
                "langgraph_config_path": "langgraph.json",
            },
        },
    )

    if response.status_code != 200:
        raise Exception(f"Failed to patch deployment: {response.text}")

    print(f"Patched deployment ID {deployment_id}")


def wait_for_deployment(deployment_id: str, revision_id: str) -> None:
    """Wait for revision status to be DEPLOYED."""
    start_time = time.time()
    revision, status = None, None
    while time.time() - start_time < MAX_WAIT_TIME:
        revision = get_revision(deployment_id, revision_id)
        status = revision["status"]
        if status == "DEPLOYED":
            break
        elif "FAILED" in status:
            raise Exception(f"Revision ID {revision_id} failed: {revision}")

        print(f"Waiting for revision ID {revision_id} to be DEPLOYED...")
        time.sleep(60)

    if status != "DEPLOYED":
        raise Exception(
            f"Timeout waiting for revision ID {revision_id} to be DEPLOYED: {revision}"
        )


def delete_deployment(deployment_id: str) -> None:
    """Delete deployment."""
    response = requests.delete(
        url=f"{CONTROL_PLANE_HOST}/v2/deployments/{deployment_id}",
        headers=get_headers(),
    )

    if response.status_code != 204:
        raise Exception(
            f"Failed to delete deployment ID {deployment_id}: {response.text}"
        )

    print(f"Deployment ID {deployment_id} deleted")


if __name__ == "__main__":
    # create deployment and get the latest revision
    deployment_id = create_deployment()
    revisions = list_revisions(deployment_id)
    latest_revision = revisions["resources"][0]
    latest_revision_id = latest_revision["id"]

    # wait for latest revision to be DEPLOYED
    wait_for_deployment(deployment_id, latest_revision_id)

    # patch the deployment and get the latest revision
    patch_deployment(deployment_id)
    revisions = list_revisions(deployment_id)
    latest_revision = revisions["resources"][0]
    latest_revision_id = latest_revision["id"]

    # wait for latest revision to be DEPLOYED
    wait_for_deployment(deployment_id, latest_revision_id)

    # delete the deployment
    delete_deployment(deployment_id)
```

### Source References

- [`Config`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/cli/langgraph_cli/schemas.py#L528) (class in cli)
- [`rc`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/tests/test_serde_schema.py#L12) (function in sdk-py)
- [`get`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/channels/named_barrier_value.py#L147) (function in langgraph)
- [`post`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3707) (function in sdk-py)
- [`patch`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/client.py#L3753) (function in sdk-py)
- [`delete`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/store/base/__init__.py#L929) (function in checkpoint)
- [`create`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L1039) (class in sdk-py)
- [`wait`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/langgraph/langgraph/_internal/_queue.py#L108) (function in langgraph)
- [`list`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/checkpoint/langgraph/checkpoint/base/__init__.py#L174) (function in checkpoint)
- [`on`](https://github.com/langchain-ai/langgraph/blob/8ccead9560f6/libs/sdk-py/langgraph_sdk/auth/types.py#L931) (class in sdk-py)
