import time

import pytest
from agent_bucket.config import Settings
from fastapi.testclient import TestClient


def sync(client: TestClient) -> dict[str, object]:
    response = client.post("/v1/sync")
    assert response.status_code == 202
    job_id = response.json()["id"]
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        job = client.get(f"/v1/jobs/{job_id}").json()
        if job["status"] in {"succeeded", "failed"}:
            assert job["status"] == "succeeded", job
            return dict(job)
        time.sleep(0.05)
    pytest.fail("Sync did not complete")


def test_auth_applies_to_rest_and_mcp(client: TestClient) -> None:
    assert client.get("/healthz", headers={"Authorization": ""}).status_code == 200
    for path in ["/v1/status", "/v1/jobs", "/mcp", "/mcp/"]:
        assert client.get(path, headers={"Authorization": "Bearer wrong"}).status_code == 401


@pytest.mark.parametrize("mode", ["keyword", "vector", "hybrid"])
def test_sync_and_retrieve(client: TestClient, mode: str) -> None:
    assert sync(client)["indexed"] == 2
    response = client.post("/v1/search", json={"query": "rotate access keys", "mode": mode})
    assert response.status_code == 200, response.text
    assert response.json()["hits"][0]["uri"] == "demo://keys.md"
    assert response.json()["embedding_provider"] == "hash"
    assert client.get("/v1/status").json()["documents"] == 2


def test_incremental_sync_and_deletion(client: TestClient, settings: Settings) -> None:
    sync(client)
    assert sync(client)["indexed"] == 0
    (settings.demo_dir / "keys.md").unlink()
    assert sync(client)["deleted"] == 1
    assert client.get("/v1/status").json()["documents"] == 1
    assert (
        client.post("/v1/search", json={"query": "rotate", "mode": "keyword"}).json()["hits"] == []
    )


def test_input_validation(client: TestClient) -> None:
    for body in [{"query": " "}, {"query": "keys", "limit": 100}, {"query": "keys", "mode": "sql"}]:
        assert client.post("/v1/search", json=body).status_code == 422
    assert client.get("/v1/jobs/unknown").status_code == 404


def test_mcp_tool_discovery_and_call(client: TestClient) -> None:
    headers = {"Accept": "application/json, text/event-stream"}
    response = client.post(
        "/mcp/",
        headers=headers,
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1"},
            },
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["result"]["serverInfo"]["name"] == "agent-bucket"
    response = client.post(
        "/mcp/",
        headers=headers,
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {},
        },
    )
    names = {tool["name"] for tool in response.json()["result"]["tools"]}
    assert names == {"search_objects", "bucket_status"}
    sync(client)
    response = client.post(
        "/mcp/",
        headers=headers,
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "search_objects",
                "arguments": {"request": {"query": "access keys", "mode": "keyword"}},
            },
        },
    )
    assert response.status_code == 200
    assert "demo://keys.md" in response.text
    assert not response.json()["result"].get("isError", False)
