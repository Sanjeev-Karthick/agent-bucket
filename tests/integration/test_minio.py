import os
from uuid import uuid4

import boto3
import pytest
from agent_bucket.app import create_app
from agent_bucket.config import Settings
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_minio_roundtrip(settings: Settings, monkeypatch: pytest.MonkeyPatch) -> None:
    endpoint = os.environ.get("AB_TEST_S3_ENDPOINT")
    if not endpoint:
        pytest.skip("Set AB_TEST_S3_ENDPOINT to run the MinIO integration test")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "minioadmin")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "minioadmin")
    bucket = "agent-bucket-test-" + uuid4().hex[:12]
    s3 = boto3.client("s3", endpoint_url=endpoint, region_name="us-east-1")
    s3.create_bucket(Bucket=bucket)
    try:
        s3.put_object(Bucket=bucket, Key="readme.md", Body=b"MinIO retrieval integration sentinel")
        config = settings.model_copy(
            update={"source": "s3", "s3_bucket": bucket, "s3_endpoint": endpoint}
        )
        with TestClient(create_app(config)) as client:
            client.headers["Authorization"] = "Bearer " + config.api_token.get_secret_value()
            import time

            job = client.post("/v1/sync").json()
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                current = client.get(f"/v1/jobs/{job['id']}").json()
                if current["status"] in {"succeeded", "failed"}:
                    break
                time.sleep(0.05)
            assert current["status"] == "succeeded", current
            result = client.post("/v1/search", json={"query": "sentinel", "mode": "keyword"})
            assert result.json()["hits"][0]["uri"] == f"s3://{bucket}/readme.md"
    finally:
        s3.delete_object(Bucket=bucket, Key="readme.md")
        s3.delete_bucket(Bucket=bucket)
